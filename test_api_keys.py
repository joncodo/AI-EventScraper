#!/usr/bin/env python3
"""
Test script for API key configuration.

This script tests if API keys are properly configured and working.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from core.config import settings
from scrapers.api_scraper import APIEventScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_api_keys():
    """Check which API keys are configured."""
    print("🔑 Checking API Key Configuration...")
    print("=" * 50)
    
    api_keys = {
        'Eventbrite': settings.eventbrite_api_key,
        'Meetup': settings.meetup_api_key,
        'Facebook': settings.facebook_api_key,
        'Google Calendar': settings.google_api_key,
        'NewsAPI': settings.newsapi_key,
        'PR Newswire': settings.prnewswire_api_key,
        'CitySpark': settings.cityspark_api_key,
        'Eventful': settings.eventful_api_key,
    }
    
    configured_count = 0
    total_count = len(api_keys)
    
    for platform, key in api_keys.items():
        if key:
            print(f"✅ {platform}: Configured")
            configured_count += 1
        else:
            print(f"❌ {platform}: Not configured")
    
    print("=" * 50)
    print(f"📊 API Keys Status: {configured_count}/{total_count} configured")
    
    if configured_count == 0:
        print("\n⚠️  No API keys configured!")
        print("   Please follow the API Keys Setup Guide to configure API keys.")
        print("   Start with Eventbrite API for the biggest impact.")
        return False
    elif configured_count < 4:
        print(f"\n💡 {total_count - configured_count} API keys missing.")
        print("   Consider adding more API keys for better event coverage.")
        return True
    else:
        print("\n🎉 All major API keys configured!")
        print("   You should get excellent event coverage.")
        return True


async def test_api_scraper():
    """Test the API scraper with configured keys."""
    print("\n🧪 Testing API Scraper...")
    print("=" * 50)
    
    try:
        async with APIEventScraper() as scraper:
            # Test with a major city
            events = await scraper.scrape_events(
                city="San Francisco",
                country="United States",
                radius_km=50
            )
            
            print(f"✅ API scraper found {len(events)} events")
            
            if events:
                print("\n📋 Sample events:")
                for i, event in enumerate(events[:5]):  # Show first 5 events
                    print(f"   {i+1}. {event.title}")
                    print(f"      Date: {event.start_date}")
                    print(f"      Source: {event.sources[0].platform}")
                    print(f"      Location: {event.location.city}, {event.location.country}")
                    print()
                
                # Count events by source
                source_counts = {}
                for event in events:
                    for source in event.sources:
                        platform = source.platform
                        source_counts[platform] = source_counts.get(platform, 0) + 1
                
                print("📊 Events by source:")
                for platform, count in source_counts.items():
                    print(f"   - {platform}: {count} events")
            
            return len(events) > 0
            
    except Exception as e:
        print(f"❌ API scraper error: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting API Keys Test")
    print("=" * 60)
    
    # Check API key configuration
    keys_configured = check_api_keys()
    
    if not keys_configured:
        print("\n❌ No API keys configured. Please set up API keys first.")
        print("   See API_KEYS_SETUP.md for instructions.")
        return False
    
    # Test API scraper
    scraper_working = await test_api_scraper()
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    
    if keys_configured and scraper_working:
        print("✅ API keys are configured and working!")
        print("   Your event scraper should now get hundreds of events per city.")
        print("   Deploy to Railway to see the full impact.")
        return True
    elif keys_configured and not scraper_working:
        print("⚠️  API keys are configured but scraper is not working.")
        print("   Check the API key values and permissions.")
        return False
    else:
        print("❌ API keys are not properly configured.")
        print("   Please follow the API Keys Setup Guide.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
