#!/usr/bin/env python3
"""Test API keys configuration and functionality."""

import os
import sys
import asyncio
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import settings
from src.scrapers.api_scraper import APIEventScraper

async def test_api_keys():
    """Test all configured API keys."""
    print("🧪 Testing API Keys Configuration...")
    print("=" * 50)
    
    # Test configuration loading
    print("📋 Configuration Status:")
    print(f"Environment: {settings.environment}")
    print(f"Debug Mode: {settings.debug}")
    print()
    
    # Test individual API keys
    print("🔑 API Keys Status:")
    
    # Meetup API
    if settings.meetup_api_key and settings.meetup_api_key != "your_meetup_key_here":
        print("✅ Meetup API Key: Configured")
    else:
        print("❌ Meetup API Key: Not configured")
    
    # Facebook API
    if settings.facebook_api_key and settings.facebook_api_key != "your_facebook_token_here":
        print("✅ Facebook API Key: Configured")
    else:
        print("❌ Facebook API Key: Not configured")
    
    # Google API
    if settings.google_api_key and settings.google_api_key != "your_google_key_here":
        print("✅ Google API Key: Configured")
    else:
        print("❌ Google API Key: Not configured")
    
    # Eventbrite API
    if settings.eventbrite_api_key and settings.eventbrite_api_key != "your_eventbrite_token_here":
        print("✅ Eventbrite API Key: Configured")
    else:
        print("❌ Eventbrite API Key: Not configured")
    
    print()
    
    # Test API Scraper initialization
    print("🔧 Testing API Scraper:")
    try:
        scraper = APIEventScraper()
        print("✅ API Scraper: Initialized successfully")
        
        # Test API configurations
        print("\n📊 API Configurations:")
        for platform, config in scraper.api_configs.items():
            status = "✅ Enabled" if config.get('enabled') else "❌ Disabled"
            has_key = "✅ Has Key" if config.get('api_key') else "❌ No Key"
            print(f"  {platform.title()}: {status} | {has_key}")
            
    except Exception as e:
        print(f"❌ API Scraper: Error - {e}")
    
    print()
    
    # Test environment variables
    print("🌍 Environment Variables:")
    env_vars = [
        'EVENT_SCRAPER_MEETUP_API_KEY',
        'EVENT_SCRAPER_FACEBOOK_API_KEY', 
        'EVENT_SCRAPER_GOOGLE_API_KEY',
        'EVENT_SCRAPER_EVENTBRITE_API_KEY'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value and not value.startswith('your_'):
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Not set")
    
    print()
    print("🎯 Next Steps:")
    print("1. Get API keys from the setup guide")
    print("2. Add them to your .env file")
    print("3. Run this test again to verify")
    print("4. Start scraping events!")

if __name__ == "__main__":
    asyncio.run(test_api_keys())
