#!/usr/bin/env python3
"""
Test script for alternative data sources.

This script tests the new alternative data sources (RSS, APIs, Local Events)
to ensure they work correctly and provide reliable event data.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from scrapers.rss_scraper import RSSEventScraper
from scrapers.api_scraper import APIEventScraper
from scrapers.local_events_scraper import LocalEventsScraper
from scrapers.enhanced_scraper_manager import enhanced_scraper_manager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_rss_scraper():
    """Test the RSS scraper."""
    print("\n🧪 Testing RSS Scraper...")
    
    try:
        async with RSSEventScraper() as scraper:
            events = await scraper.scrape_events(
                city="San Francisco",
                country="United States",
                radius_km=50
            )
            
            print(f"✅ RSS scraper found {len(events)} events")
            
            if events:
                print("   Sample events:")
                for i, event in enumerate(events[:3]):  # Show first 3 events
                    print(f"   {i+1}. {event.title} - {event.start_date}")
                    print(f"      Source: {event.sources[0].platform}")
            
            return len(events) > 0
            
    except Exception as e:
        print(f"❌ RSS scraper error: {e}")
        return False


async def test_api_scraper():
    """Test the API scraper."""
    print("\n🧪 Testing API Scraper...")
    
    try:
        async with APIEventScraper() as scraper:
            events = await scraper.scrape_events(
                city="New York",
                country="United States",
                radius_km=50
            )
            
            print(f"✅ API scraper found {len(events)} events")
            
            if events:
                print("   Sample events:")
                for i, event in enumerate(events[:3]):  # Show first 3 events
                    print(f"   {i+1}. {event.title} - {event.start_date}")
                    print(f"      Source: {event.sources[0].platform}")
            
            return len(events) > 0
            
    except Exception as e:
        print(f"❌ API scraper error: {e}")
        return False


async def test_local_events_scraper():
    """Test the local events scraper."""
    print("\n🧪 Testing Local Events Scraper...")
    
    try:
        async with LocalEventsScraper() as scraper:
            events = await scraper.scrape_events(
                city="San Francisco",
                country="United States",
                radius_km=50
            )
            
            print(f"✅ Local events scraper found {len(events)} events")
            
            if events:
                print("   Sample events:")
                for i, event in enumerate(events[:3]):  # Show first 3 events
                    print(f"   {i+1}. {event.title} - {event.start_date}")
                    print(f"      Source: {event.sources[0].platform}")
            
            return len(events) > 0
            
    except Exception as e:
        print(f"❌ Local events scraper error: {e}")
        return False


async def test_enhanced_scraper_manager_with_alternatives():
    """Test the enhanced scraper manager with all alternative sources."""
    print("\n🧪 Testing Enhanced Scraper Manager with Alternatives...")
    
    try:
        from core.models import ScrapeRequest
        
        # Create a test request
        request = ScrapeRequest(
            city="San Francisco",
            country="United States",
            radius_km=50
        )
        
        # Test scraping with all sources
        events = await enhanced_scraper_manager.scrape_all_events(request)
        
        print(f"✅ Enhanced scraper manager found {len(events)} events")
        
        if events:
            print("   Event sources breakdown:")
            source_counts = {}
            for event in events:
                for source in event.sources:
                    platform = source.platform
                    source_counts[platform] = source_counts.get(platform, 0) + 1
            
            for platform, count in source_counts.items():
                print(f"   - {platform}: {count} events")
        
        return len(events) > 0
        
    except Exception as e:
        print(f"❌ Enhanced scraper manager error: {e}")
        return False


async def test_scraper_status_with_alternatives():
    """Test scraper status with alternative sources."""
    print("\n🧪 Testing Scraper Status with Alternatives...")
    
    try:
        status = await enhanced_scraper_manager.get_scraper_status()
        
        print("✅ Scraper status retrieved:")
        for platform, info in status.items():
            print(f"   - {platform}: {info.get('status', 'unknown')} "
                  f"({info.get('type', 'unknown')}, "
                  f"reliability: {info.get('reliability', 'unknown')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Scraper status error: {e}")
        return False


async def test_stealth_capabilities_with_alternatives():
    """Test stealth capabilities with alternative sources."""
    print("\n🧪 Testing Stealth Capabilities with Alternatives...")
    
    try:
        capabilities = await enhanced_scraper_manager.test_stealth_capabilities()
        
        print("✅ Stealth capabilities test completed:")
        for platform, info in capabilities.items():
            print(f"   - {platform}: {info.get('status', 'unknown')} "
                  f"(events: {info.get('events_found', 0)}, "
                  f"stealth: {info.get('stealth_level', 'unknown')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Stealth capabilities test error: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting Alternative Data Sources Tests")
    print("=" * 60)
    
    tests = [
        ("RSS Scraper", test_rss_scraper),
        ("API Scraper", test_api_scraper),
        ("Local Events Scraper", test_local_events_scraper),
        ("Enhanced Scraper Manager with Alternatives", test_enhanced_scraper_manager_with_alternatives),
        ("Scraper Status with Alternatives", test_scraper_status_with_alternatives),
        ("Stealth Capabilities with Alternatives", test_stealth_capabilities_with_alternatives),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"   Tests run: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    
    if total - passed > 0:
        print("\n❌ Failed Tests:")
        for test_name, result in results:
            if not result:
                print(f"   - {test_name}")
    
    if passed == total:
        print("\n🎉 All alternative data source tests passed!")
        print("   Your event scraper now has multiple reliable data sources!")
        print("   - RSS/iCal feeds for real-time updates")
        print("   - Official APIs for structured data")
        print("   - Local government/university APIs for regional events")
        print("   - Enhanced stealth scraping as fallback")
    else:
        print(f"\n⚠️ {total - passed} tests failed.")
        print("   Some alternative data sources may not be working correctly.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
