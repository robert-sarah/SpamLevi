"""
Request manager for handling HTTP requests with rate limiting and security features.
"""

import asyncio
import aiohttp
import time
from typing import Dict, Any, Optional
from fake_useragent import UserAgent
import logging


class RateLimitExceededError(Exception):
    """Raised when rate limit is exceeded."""
    pass


class RateLimiter:
    """Rate limiter with configurable limits per minute and hour."""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = max(1, requests_per_minute)
        self.requests_per_hour = max(1, requests_per_hour)
        
        self.minute_requests = []
        self.hour_requests = []
        self.lock = asyncio.Lock()
    
    async def check_rate_limit(self) -> bool:
        """Check if we can make a request without exceeding limits."""
        async with self.lock:
            now = time.time()
            
            # Clean old requests
            self.minute_requests = [t for t in self.minute_requests if now - t < 60]
            self.hour_requests = [t for t in self.hour_requests if now - t < 3600]
            
            # Check limits
            if len(self.minute_requests) >= self.requests_per_minute:
                return False
            
            if len(self.hour_requests) >= self.requests_per_hour:
                return False
            
            return True
    
    async def record_request(self):
        """Record a request has been made."""
        async with self.lock:
            now = time.time()
            self.minute_requests.append(now)
            self.hour_requests.append(now)
    
    async def wait_time(self) -> float:
        """Calculate wait time before next request can be made."""
        async with self.lock:
            now = time.time()
            
            # Check minute limit
            if len(self.minute_requests) >= self.requests_per_minute:
                oldest_minute = min(self.minute_requests)
                wait_minute = max(0, 60 - (now - oldest_minute))
            else:
                wait_minute = 0
            
            # Check hour limit
            if len(self.hour_requests) >= self.requests_per_hour:
                oldest_hour = min(self.hour_requests)
                wait_hour = max(0, 3600 - (now - oldest_hour))
            else:
                wait_hour = 0
            
            return max(wait_minute, wait_hour)


class RequestManager:
    """Manages HTTP requests with security features and rate limiting."""
    
    def __init__(self, config):
        self.config = config
        self.rate_limiter = RateLimiter(
            config.rate_limit.requests_per_minute,
            config.rate_limit.requests_per_hour
        )
        self.ua = UserAgent()
        self.session = None
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure aiohttp session is created."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.whatsapp.timeout)
            
            # Prepare headers with rotating user agent
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            # Add proxy configuration if provided
            connector = None
            if self.config.security.proxy_url:
                connector = aiohttp.ProxyConnector.from_url(self.config.security.proxy_url)
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers,
                connector=connector
            )
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def check_rate_limit(self) -> bool:
        """Check if we can make a request."""
        return await self.rate_limiter.check_rate_limit()
    
    async def send_message(self, phone: str, message: str) -> bool:
        """Send a message via WhatsApp API."""
        try:
            await self._ensure_session()
            
            # Check rate limit
            if not await self.check_rate_limit():
                wait_time = await self.rate_limiter.wait_time()
                self.logger.warning(f"Rate limit exceeded. Waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                
                # Check again after waiting
                if not await self.check_rate_limit():
                    raise RateLimitExceededError("Rate limit still exceeded after waiting")
            
            # Prepare payload
            payload = {
                'phone': phone,
                'message': message,
                'type': 'text'
            }
            
            # Add authentication if configured
            if hasattr(self.config.security, 'api_key') and self.config.security.api_key:
                payload['key'] = self.config.security.api_key
            
            # Send request with retry logic
            max_retries = 3
            retry_delay = 1.0
            
            for attempt in range(max_retries):
                try:
                    # Update user agent for each attempt
                    if self.session:
                        self.session.headers['User-Agent'] = self.ua.random
                    
                    async with self.session.post(
                        f"{self.config.whatsapp.api_url}{self.config.whatsapp.send_endpoint}",
                        json=payload
                    ) as response:
                        
                        # Record request
                        await self.rate_limiter.record_request()
                        
                        if response.status == 200:
                            result = await response.json()
                            if result.get('success', False):
                                self.logger.info(f"Message sent to {phone}")
                                return True
                            else:
                                self.logger.warning(f"API reported failure for {phone}: {result}")
                                return False
                        elif response.status == 429:
                            # Rate limited by API
                            retry_after = int(response.headers.get('Retry-After', retry_delay))
                            self.logger.warning(f"API rate limit hit. Waiting {retry_after}s")
                            await asyncio.sleep(retry_after)
                            continue
                        else:
                            self.logger.error(f"HTTP {response.status} for {phone}")
                            return False
                            
                except aiohttp.ClientError as e:
                    self.logger.error(f"Network error (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (2 ** attempt))
                        continue
                    return False
                except asyncio.TimeoutError:
                    self.logger.error(f"Timeout error (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (2 ** attempt))
                        continue
                    return False
            
            return False
            
        except RateLimitExceededError as e:
            self.logger.error(f"Rate limit error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error sending message: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check if the WhatsApp API is accessible."""
        try:
            await self._ensure_session()
            
            async with self.session.get(self.config.whatsapp.api_url) as response:
                return response.status == 200
                
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get current rate limiting statistics."""
        return {
            'requests_per_minute': self.rate_limiter.requests_per_minute,
            'requests_per_hour': self.rate_limiter.requests_per_hour,
            'minute_requests': len(self.rate_limiter.minute_requests),
            'hour_requests': len(self.rate_limiter.hour_requests),
            'minute_limit': self.rate_limiter.requests_per_minute,
            'hour_limit': self.rate_limiter.requests_per_hour
        }