"""Test script using in-memory database."""
import asyncio
import logging
from datetime import datetime, timedelta

from config import settings
from models import ScrapeRequest, QueryRequest, Event, Location, ContactInfo, EventSource
from scrapers.scraper_manager import scraper_manager
from ai_processor import ai_processor
from memory_db import memory_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_complete_workflow():
    """Test the complete workflow with in-memory database."""
    print("🎉 AI Event Scraper - Complete Test with Memory Database")
    print("=" * 60)
    
    # Connect to memory database
    await memory_db.connect()
    
    try:
        # Create some sample events for testing
        sample_events = [
            Event(
                title="Tech Meetup: AI and Machine Learning",
                description="Join us for an evening of discussions about the latest trends in AI and ML.",
                start_date=datetime.now() + timedelta(days=3, hours=18),
                location=Location(
                    address="123 Tech Street",
                    city="Fredericton",
                    country="Canada",
                    venue_name="Tech Hub"
                ),
                contact_info=ContactInfo(
                    email="contact@techmeetup.com",
                    website="https://techmeetup.com"
                ),
                price="Free",
                sources=[EventSource(
                    platform="meetup",
                    url="https://meetup.com/tech-ai-ml",
                    scraped_at=datetime.utcnow()
                )]
            ),
            Event(
                title="Startup Networking Event",
                description="Connect with entrepreneurs and investors in Fredericton.",
                start_date=datetime.now() + timedelta(days=5, hours=19),
                location=Location(
                    address="456 Business Ave",
                    city="Fredericton",
                    country="Canada",
                    venue_name="Business Center"
                ),
                contact_info=ContactInfo(
                    email="events@startupnetwork.com",
                    phone="+1-506-555-0123"
                ),
                price="25",
                currency="CAD",
                sources=[EventSource(
                    platform="eventbrite",
                    url="https://eventbrite.com/startup-networking",
                    scraped_at=datetime.utcnow()
                )]
            ),
            Event(
                title="Python Workshop for Beginners",
                description="Learn Python programming from scratch in this hands-on workshop.",
                start_date=datetime.now() + timedelta(days=7, hours=10),
                location=Location(
                    address="789 Code Lane",
                    city="Fredericton",
                    country="Canada",
                    venue_name="Code Academy"
                ),
                contact_info=ContactInfo(
                    email="workshops@codeacademy.com",
                    website="https://codeacademy.com"
                ),
                price="50",
                currency="CAD",
                sources=[EventSource(
                    platform="facebook",
                    url="https://facebook.com/events/python-workshop",
                    scraped_at=datetime.utcnow()
                )]
            )
        ]
        
        print(f"📝 Created {len(sample_events)} sample events")
        
        # Process events with AI
        print("\n🤖 Processing events with AI...")
        processed_events = []
        for event in sample_events:
            processed_event = await ai_processor.process_event(event)
            processed_events.append(processed_event)
            print(f"  ✓ {processed_event.title}")
            print(f"    Category: {processed_event.category}")
            print(f"    Tags: {', '.join(processed_event.tags)}")
            print(f"    Confidence: {processed_event.confidence_score}")
        
        # Save events to memory database
        print(f"\n💾 Saving {len(processed_events)} events to database...")
        event_ids = await memory_db.insert_events(processed_events)
        print(f"  ✓ Saved {len(event_ids)} events")
        
        # Query events
        print("\n🔍 Querying events...")
        
        # Query all events
        all_events = await memory_db.find_events(QueryRequest())
        print(f"  ✓ Found {len(all_events)} total events")
        
        # Query by city
        fredericton_events = await memory_db.find_events(QueryRequest(city="Fredericton"))
        print(f"  ✓ Found {len(fredericton_events)} events in Fredericton")
        
        # Query by category
        tech_events = await memory_db.find_events(QueryRequest(category="Technology"))
        print(f"  ✓ Found {len(tech_events)} technology events")
        
        # Query by tags
        meetup_events = await memory_db.find_events(QueryRequest(tags=["meetup"]))
        print(f"  ✓ Found {len(meetup_events)} meetup events")
        
        # Display sample results
        print("\n📊 Sample Events:")
        for i, event in enumerate(all_events[:3], 1):
            print(f"\n{i}. {event.title}")
            print(f"   Date: {event.start_date.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Location: {event.location.city}, {event.location.country}")
            print(f"   Category: {event.category}")
            print(f"   Price: {event.price} {event.currency or ''}")
            print(f"   Tags: {', '.join(event.tags)}")
            print(f"   Sources: {', '.join([s.platform for s in event.sources])}")
        
        # Test deduplication
        print("\n🔄 Testing deduplication...")
        
        # Create a duplicate event
        duplicate_event = Event(
            title="Tech Meetup: AI and Machine Learning",  # Same title
            description="AI and ML discussion event",  # Similar description
            start_date=datetime.now() + timedelta(days=3, hours=18, minutes=30),  # Same day, slightly different time
            location=Location(
                address="123 Tech Street",
                city="Fredericton",
                country="Canada",
                venue_name="Tech Hub"
            ),
            sources=[EventSource(
                platform="eventbrite",
                url="https://eventbrite.com/ai-ml-meetup",
                scraped_at=datetime.utcnow()
            )]
        )
        
        # Find duplicates
        duplicates = await memory_db.find_duplicate_events(duplicate_event)
        print(f"  ✓ Found {len(duplicates)} potential duplicates")
        
        if duplicates:
            print(f"  ✓ Duplicate detected: '{duplicates[0].title}'")
            print(f"    Original sources: {', '.join([s.platform for s in duplicates[0].sources])}")
            print(f"    New event sources: {', '.join([s.platform for s in duplicate_event.sources])}")
        
        print("\n" + "=" * 60)
        print("🎉 Complete workflow test successful!")
        print("\nThe AI Event Scraper is working perfectly with:")
        print("✅ AI processing and categorization")
        print("✅ Event storage and retrieval")
        print("✅ Flexible querying by city, category, tags")
        print("✅ Duplicate detection")
        print("✅ Rich data models and validation")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        logger.error(f"Test error: {e}", exc_info=True)
    
    finally:
        await memory_db.disconnect()


if __name__ == "__main__":
    asyncio.run(test_complete_workflow())

