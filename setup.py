#!/usr/bin/env python3
"""
Setup script for SpamLevi - Advanced WhatsApp Spam Tool
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='spamlevi',
    version='1.0.0',
    author='SpamLevi Team',
    author_email='support@spamlevi.com',
    description='Advanced WhatsApp spam tool with security management and rate limiting',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/spamlevi/spamlevi',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Communications',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8',
    install_requires=[
        'aiohttp>=3.8.0',
        'rich>=13.0.0',
        'click>=8.0.0',
        'asyncio-throttle>=1.0.0',
        'cryptography>=3.4.8',
        'fake-useragent>=1.1.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.0.0',
            'bandit>=1.7.0',
            'flake8>=5.0.0',
            'black>=22.0.0',
        ],
        'test': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'spamlevi=spamlevi.cli:main',
        ],
    },
    include_package_data=True,
    package_data={
        'spamlevi': ['config.ini'],
    },
    zip_safe=False,
)