"""
SpamLevi - Advanced WhatsApp Spam Tool

A comprehensive Python package for WhatsApp spamming with advanced features
including rate limiting, security management, and detailed logging.
"""

__version__ = "1.0.0"
__author__ = "SpamLevi Team"
__email__ = "support@spamlevi.com"
__description__ = "Advanced WhatsApp spam tool with security management and rate limiting"

from .core.spam_engine import SpamEngine, TargetManager
from .core.request_manager import RequestManager, RateLimitExceededError
from .config.config import Config
from .core.logger import SecurityLogger

__all__ = [
    'SpamEngine',
    'TargetManager', 
    'RequestManager',
    'RateLimitExceededError',
    'Config',
    'SecurityLogger',
]