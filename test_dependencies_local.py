#!/usr/bin/env python3
"""Test script to verify all dependencies are working locally."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all critical imports."""
    print("🔍 Testing critical imports...")
    
    try:
        import feedparser
        print("✅ feedparser imported successfully")
    except ImportError as e:
        print(f"❌ feedparser failed: {e}")
    
    try:
        import icalendar
        print("✅ icalendar imported successfully")
    except ImportError as e:
        print(f"❌ icalendar failed: {e}")
    
    try:
        import selenium
        print("✅ selenium imported successfully")
    except ImportError as e:
        print(f"❌ selenium failed: {e}")
    
    try:
        import playwright
        print("✅ playwright imported successfully")
    except ImportError as e:
        print(f"❌ playwright failed: {e}")
    
    try:
        import undetected_chromedriver
        print("✅ undetected_chromedriver imported successfully")
    except ImportError as e:
        print(f"❌ undetected_chromedriver failed: {e}")
    
    try:
        import requests_html
        print("✅ requests_html imported successfully")
    except ImportError as e:
        print(f"❌ requests_html failed: {e}")

def test_scrapers():
    """Test scraper imports."""
    print("\n🔍 Testing scraper imports...")
    
    try:
        from scrapers.rss_scraper import RSSEventScraper
        print("✅ RSSEventScraper imported successfully")
    except ImportError as e:
        print(f"❌ RSSEventScraper failed: {e}")
    
    try:
        from scrapers.api_scraper import APIEventScraper
        print("✅ APIEventScraper imported successfully")
    except ImportError as e:
        print(f"❌ APIEventScraper failed: {e}")
    
    try:
        from scrapers.local_events_scraper import LocalEventsScraper
        print("✅ LocalEventsScraper imported successfully")
    except ImportError as e:
        print(f"❌ LocalEventsScraper failed: {e}")
    
    try:
        from scrapers.enhanced_scraper_manager import enhanced_scraper_manager
        print("✅ enhanced_scraper_manager imported successfully")
    except ImportError as e:
        print(f"❌ enhanced_scraper_manager failed: {e}")

def test_config():
    """Test configuration."""
    print("\n🔍 Testing configuration...")
    
    try:
        from core.config import settings
        print("✅ Settings imported successfully")
        print(f"📊 Eventbrite API key: {'✅ Set' if getattr(settings, 'eventbrite_api_key', None) else '❌ Not set'}")
    except ImportError as e:
        print(f"❌ Settings failed: {e}")

if __name__ == "__main__":
    test_imports()
    test_scrapers()
    test_config()
    print("\n🎯 Dependency test completed!")
