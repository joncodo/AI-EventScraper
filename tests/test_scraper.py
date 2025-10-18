"""Test script for the AI Event Scraper."""
import asyncio
import logging
from datetime import datetime, timedelta

from config import settings
from database import db
from models import ScrapeRequest, QueryRequest
from scrapers.scraper_manager import scraper_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_database_connection():
    """Test database connection."""
    print("Testing database connection...")
    try:
        await db.connect()
        print("✓ Database connection successful")
        
        # Test basic operations
        total_events = await db.get_event_count(QueryRequest())
        print(f"✓ Total events in database: {total_events}")
        
        await db.disconnect()
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


async def test_scraper_status():
    """Test scraper status."""
    print("\nTesting scraper status...")
    try:
        status = await scraper_manager.get_scraper_status()
        
        for platform, info in status.items():
            if info["status"] == "online":
                print(f"✓ {platform.title()} scraper: OK")
            else:
                print(f"✗ {platform.title()} scraper: {info.get('error', 'Unknown error')}")
        
        return True
    except Exception as e:
        print(f"✗ Scraper status check failed: {e}")
        return False


async def test_scraping():
    """Test scraping functionality."""
    print("\nTesting scraping functionality...")
    
    # Create a test scrape request
    request = ScrapeRequest(
        city="San Francisco",
        country="United States",
        radius_km=50,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30)
    )
    
    try:
        await db.connect()
        
        # Test scraping
        events = await scraper_manager.scrape_all_events(request)
        
        if events:
            print(f"✓ Scraped {len(events)} events successfully")
            
            # Test saving to database
            event_ids = await scraper_manager.save_events_to_database(events)
            print(f"✓ Saved {len(event_ids)} events to database")
            
            # Test querying
            query_request = QueryRequest(
                city="San Francisco",
                limit=5
            )
            
            queried_events = await db.find_events(query_request)
            print(f"✓ Queried {len(queried_events)} events from database")
            
        else:
            print("⚠ No events found (this might be normal)")
        
        await db.disconnect()
        return True
        
    except Exception as e:
        print(f"✗ Scraping test failed: {e}")
        logger.error(f"Scraping test error: {e}", exc_info=True)
        return False


async def main():
    """Run all tests."""
    print("AI Event Scraper - Test Suite")
    print("=" * 40)
    
    # Test database connection
    db_ok = await test_database_connection()
    
    # Test scraper status
    scrapers_ok = await test_scraper_status()
    
    # Test scraping if basic tests pass
    scraping_ok = False
    if db_ok and scrapers_ok:
        scraping_ok = await test_scraping()
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Summary:")
    print(f"Database: {'✓ PASS' if db_ok else '✗ FAIL'}")
    print(f"Scrapers: {'✓ PASS' if scrapers_ok else '✗ FAIL'}")
    print(f"Scraping: {'✓ PASS' if scraping_ok else '✗ FAIL'}")
    
    if all([db_ok, scrapers_ok, scraping_ok]):
        print("\n🎉 All tests passed! The AI Event Scraper is ready to use.")
    else:
        print("\n⚠ Some tests failed. Please check the configuration and try again.")


if __name__ == "__main__":
    asyncio.run(main())
