#!/usr/bin/env python3
"""
SpamLevi - Advanced WhatsApp Spam Tool
Main entry point for the application.
"""

import os
import sys
import argparse
import asyncio
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from spamlevi.cli import main as cli_main
from spamlevi.config import Config
from spamlevi.core.spam_engine import SpamEngine
from spamlevi.core.logger import SecurityLogger


def setup_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        'logs',
        'config',
        'data',
        'tests',
        'docs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description='SpamLevi - Advanced WhatsApp Spam Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python spamlevi.py                    # Interactive CLI mode
  python spamlevi.py --single           # Single target mode
  python spamlevi.py --file targets.txt # Load targets from file
  python spamlevi.py --config custom.ini # Custom config file
        '''
    )
    
    parser.add_argument(
        '--single', 
        action='store_true',
        help='Run in single target mode'
    )
    
    parser.add_argument(
        '--file', 
        type=str,
        help='Load targets from file'
    )
    
    parser.add_argument(
        '--config', 
        type=str,
        default='config.ini',
        help='Path to configuration file (default: config.ini)'
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='SpamLevi 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Setup directories
    setup_directories()
    
    # Initialize logger
    logger = SecurityLogger()
    logger.info("SpamLevi starting...")
    
    try:
        # Load configuration
        config = Config(config_file=args.config)
        
        # Run CLI
        asyncio.run(cli_main(args, config))
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\n[!] Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"[!] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()