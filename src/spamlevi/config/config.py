"""
Configuration management for SpamLevi
Handles loading and saving configuration from INI files and environment variables.
"""

import os
import configparser
from dataclasses import dataclass, asdict
from typing import Optional
from pathlib import Path


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    max_requests_per_minute: int = 30
    max_requests_per_hour: int = 500
    cooldown_period: int = 60
    max_retries: int = 3
    retry_delay: int = 5


@dataclass
class SecurityConfig:
    """Security configuration."""
    enable_logging: bool = True
    log_level: str = "INFO"
    encrypt_data: bool = True
    use_proxy: bool = False
    user_agent_rotation: bool = True
    log_directory: str = "logs"
    max_log_size: int = 10485760  # 10MB
    backup_count: int = 5


@dataclass
class WhatsAppConfig:
    """WhatsApp API configuration."""
    api_url: str = "https://web.whatsapp.com"
    send_endpoint: str = "/send"
    timeout: int = 30
    max_concurrent: int = 5
    retry_on_failure: bool = True
    max_retry_attempts: int = 3
    retry_delay: float = 2.0


class Config:
    """Main configuration class that loads and manages all configurations."""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.rate_limit = RateLimitConfig()
        self.security = SecurityConfig()
        self.whatsapp = WhatsAppConfig()
        
        self.load_config()
    
    def load_config(self):
        """Load configuration from INI file and environment variables."""
        config = configparser.ConfigParser()
        
        # Load from file if it exists
        if os.path.exists(self.config_file):
            config.read(self.config_file)
        
        # Override with environment variables
        self._load_rate_limit_config(config)
        self._load_security_config(config)
        self._load_whatsapp_config(config)
        
        # Ensure log directory exists
        Path(self.security.log_directory).mkdir(exist_ok=True)
    
    def _load_rate_limit_config(self, config: configparser.ConfigParser):
        """Load rate limit configuration."""
        if 'rate_limit' in config:
            section = config['rate_limit']
            self.rate_limit.max_requests_per_minute = int(
                os.getenv('SPAMLEVI_MAX_REQUESTS_PER_MINUTE', 
                         section.get('max_requests_per_minute', 30))
            )
            self.rate_limit.max_requests_per_hour = int(
                os.getenv('SPAMLEVI_MAX_REQUESTS_PER_HOUR',
                         section.get('max_requests_per_hour', 500))
            )
            self.rate_limit.cooldown_period = int(
                os.getenv('SPAMLEVI_COOLDOWN_PERIOD',
                         section.get('cooldown_period', 60))
            )
            self.rate_limit.max_retries = int(
                os.getenv('SPAMLEVI_MAX_RETRIES',
                         section.get('max_retries', 3))
            )
            self.rate_limit.retry_delay = int(
                os.getenv('SPAMLEVI_RETRY_DELAY',
                         section.get('retry_delay', 5))
            )
    
    def _load_security_config(self, config: configparser.ConfigParser):
        """Load security configuration."""
        if 'security' in config:
            section = config['security']
            self.security.enable_logging = config.getboolean(
                'security', 'enable_logging', fallback=True
            )
            self.security.log_level = os.getenv(
                'SPAMLEVI_LOG_LEVEL',
                section.get('log_level', 'INFO')
            ).upper()
            self.security.encrypt_data = config.getboolean(
                'security', 'encrypt_data', fallback=True
            )
            self.security.use_proxy = config.getboolean(
                'security', 'use_proxy', fallback=False
            )
            self.security.user_agent_rotation = config.getboolean(
                'security', 'user_agent_rotation', fallback=True
            )
            self.security.log_directory = section.get('log_directory', 'logs')
            self.security.max_log_size = int(
                section.get('max_log_size', 10485760)
            )
            self.security.backup_count = int(
                section.get('backup_count', 5)
            )
    
    def _load_whatsapp_config(self, config: configparser.ConfigParser):
        """Load WhatsApp configuration."""
        if 'whatsapp' in config:
            section = config['whatsapp']
            self.whatsapp.api_url = section.get('api_url', 'https://web.whatsapp.com')
            self.whatsapp.send_endpoint = section.get('send_endpoint', '/send')
            self.whatsapp.timeout = int(
                os.getenv('SPAMLEVI_TIMEOUT',
                         section.get('timeout', 30))
            )
            self.whatsapp.max_concurrent = int(
                os.getenv('SPAMLEVI_MAX_CONCURRENT',
                         section.get('max_concurrent', 5))
            )
            self.whatsapp.retry_on_failure = config.getboolean(
                'whatsapp', 'retry_on_failure', fallback=True
            )
            self.whatsapp.max_retry_attempts = int(
                section.get('max_retry_attempts', 3)
            )
            self.whatsapp.retry_delay = float(
                section.get('retry_delay', 2.0)
            )
    
    def save_config(self, file_path: Optional[str] = None):
        """Save current configuration to INI file."""
        if file_path is None:
            file_path = self.config_file
        
        config = configparser.ConfigParser()
        
        # Rate limit section
        config['rate_limit'] = {
            'max_requests_per_minute': str(self.rate_limit.max_requests_per_minute),
            'max_requests_per_hour': str(self.rate_limit.max_requests_per_hour),
            'cooldown_period': str(self.rate_limit.cooldown_period),
            'max_retries': str(self.rate_limit.max_retries),
            'retry_delay': str(self.rate_limit.retry_delay),
        }
        
        # Security section
        config['security'] = {
            'enable_logging': str(self.security.enable_logging),
            'log_level': self.security.log_level,
            'encrypt_data': str(self.security.encrypt_data),
            'use_proxy': str(self.security.use_proxy),
            'user_agent_rotation': str(self.security.user_agent_rotation),
            'log_directory': self.security.log_directory,
            'max_log_size': str(self.security.max_log_size),
            'backup_count': str(self.security.backup_count),
        }
        
        # WhatsApp section
        config['whatsapp'] = {
            'api_url': self.whatsapp.api_url,
            'send_endpoint': self.whatsapp.send_endpoint,
            'timeout': str(self.whatsapp.timeout),
            'max_concurrent': str(self.whatsapp.max_concurrent),
            'retry_on_failure': str(self.whatsapp.retry_on_failure),
            'max_retry_attempts': str(self.whatsapp.max_retry_attempts),
            'retry_delay': str(self.whatsapp.retry_delay),
        }
        
        with open(file_path, 'w') as f:
            config.write(f)
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            'rate_limit': asdict(self.rate_limit),
            'security': asdict(self.security),
            'whatsapp': asdict(self.whatsapp),
        }
    
    def from_dict(self, config_dict: dict):
        """Load configuration from dictionary."""
        if 'rate_limit' in config_dict:
            self.rate_limit = RateLimitConfig(**config_dict['rate_limit'])
        if 'security' in config_dict:
            self.security = SecurityConfig(**config_dict['security'])
        if 'whatsapp' in config_dict:
            self.whatsapp = WhatsAppConfig(**config_dict['whatsapp'])