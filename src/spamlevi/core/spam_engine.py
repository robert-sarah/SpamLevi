"""
Main spam engine for SpamLevi
Handles the core spamming functionality with rate limiting and statistics.
"""

import asyncio
import csv
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp

from .request_manager import RequestManager
from .logger import SecurityLogger


class TargetManager:
    """Manages target validation and preparation."""
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        if not phone:
            return False
        
        # Basic validation: must start with + and contain only digits after
        pattern = r'^\+\d{7,15}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_message(message: str) -> bool:
        """Validate message content."""
        if not message:
            return False
        
        # WhatsApp message limit is 4096 characters
        return len(message) <= 4096
    
    @staticmethod
    def prepare_target(phone: str, message: str, count: int = 1, delay: float = 1.0) -> Dict[str, Any]:
        """Prepare a single target for spamming."""
        return {
            'phone': phone,
            'message': message,
            'count': max(1, count),
            'delay': max(0.1, delay)
        }
    
    def load_targets_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Load targets from a CSV file."""
        targets = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                
                for line_num, row in enumerate(reader, 1):
                    # Skip empty lines and comments
                    if not row or row[0].strip().startswith('#'):
                        continue
                    
                    try:
                        if len(row) >= 4:
                            phone = row[0].strip()
                            message = row[1].strip()
                            count = int(row[2])
                            delay = float(row[3])
                            
                            if self.validate_phone(phone) and self.validate_message(message):
                                targets.append(self.prepare_target(phone, message, count, delay))
                            else:
                                print(f"Skipping invalid target on line {line_num}")
                        else:
                            print(f"Skipping incomplete target on line {line_num}")
                            
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing line {line_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"Target file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading target file: {e}")
        
        return targets


class SpamEngine:
    """Main spam engine that coordinates spamming operations."""
    
    def __init__(self, config):
        self.config = config
        self.request_manager = RequestManager(config)
        self.logger = SecurityLogger()
        self.stats = self._initialize_stats()
    
    def _initialize_stats(self) -> Dict[str, Any]:
        """Initialize statistics tracking."""
        return {
            'total_sent': 0,
            'total_failed': 0,
            'total_rate_limited': 0,
            'start_time': None,
            'end_time': None,
            'targets_processed': 0,
            'messages_per_second': 0.0,
            'success_rate': 0.0,
            'phone_stats': {}
        }
    
    def reset_statistics(self):
        """Reset all statistics."""
        self.stats = self._initialize_stats()
        self.logger.info("Statistics reset")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current statistics."""
        if self.stats['start_time'] and self.stats['end_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            if duration > 0:
                self.stats['messages_per_second'] = self.stats['total_sent'] / duration
        
        total_attempts = self.stats['total_sent'] + self.stats['total_failed']
        if total_attempts > 0:
            self.stats['success_rate'] = (self.stats['total_sent'] / total_attempts) * 100
        
        return self.stats.copy()
    
    async def spam_single_target(self, phone: str, message: str, count: int = 1, delay: float = 1.0) -> Dict[str, Any]:
        """Spam a single target."""
        target = TargetManager().prepare_target(phone, message, count, delay)
        return await self.spam_multiple_targets([target])
    
    async def spam_multiple_targets(self, targets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Spam multiple targets concurrently with rate limiting."""
        if not targets:
            return {}
        
        self.stats['start_time'] = datetime.now()
        self.logger.info(f"Starting spam operation with {len(targets)} targets")
        
        semaphore = asyncio.Semaphore(self.config.whatsapp.max_concurrent)
        results = {}
        
        async def process_target(target: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                return await self._process_single_target(target)
        
        # Process targets concurrently
        tasks = [process_target(target) for target in targets]
        target_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for target, result in zip(targets, target_results):
            phone = target['phone']
            if isinstance(result, Exception):
                self.logger.error(f"Error processing {phone}: {result}")
                results[phone] = {
                    'success': False,
                    'sent': 0,
                    'failed': target['count'],
                    'error': str(result)
                }
            else:
                results[phone] = result
        
        self.stats['end_time'] = datetime.now()
        self.logger.info("Spam operation completed")
        
        return results
    
    async def _process_single_target(self, target: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single target."""
        phone = target['phone']
        message = target['message']
        count = target['count']
        delay = target['delay']
        
        self.logger.info(f"Processing target: {phone}")
        
        sent = 0
        failed = 0
        
        for i in range(count):
            try:
                # Check rate limits
                if not await self.request_manager.check_rate_limit():
                    self.stats['total_rate_limited'] += 1
                    self.logger.warning(f"Rate limit exceeded for {phone}")
                    failed += 1
                    continue
                
                # Send message
                success = await self.request_manager.send_message(phone, message)
                
                if success:
                    sent += 1
                    self.stats['total_sent'] += 1
                    self.logger.info(f"Message {i+1}/{count} sent to {phone}")
                else:
                    failed += 1
                    self.stats['total_failed'] += 1
                    self.logger.warning(f"Failed to send message {i+1}/{count} to {phone}")
                
                # Update phone-specific stats
                if phone not in self.stats['phone_stats']:
                    self.stats['phone_stats'][phone] = {'sent': 0, 'failed': 0}
                
                if success:
                    self.stats['phone_stats'][phone]['sent'] += 1
                else:
                    self.stats['phone_stats'][phone]['failed'] += 1
                
                # Delay between messages
                if i < count - 1:  # Don't delay after the last message
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                self.logger.error(f"Error sending message to {phone}: {e}")
                failed += 1
                self.stats['total_failed'] += 1
        
        self.stats['targets_processed'] += 1
        
        return {
            'success': sent > 0,
            'sent': sent,
            'failed': failed
        }
    
    def stop(self):
        """Stop the spam engine."""
        self.logger.info("Spam engine stopped")
        # Add any cleanup logic here
    
    async def health_check(self) -> bool:
        """Check if the WhatsApp API is accessible."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.config.whatsapp.api_url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False