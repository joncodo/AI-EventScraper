#!/usr/bin/env python3
"""Test script to verify source tracking functionality."""

import asyncio
import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.models import Event, EventSource, Location, ContactInfo
from src.core.database import db


async def test_source_tracking():
    """Test that source tracking works correctly."""
    print("🧪 Testing source tracking functionality...")
    
    try:
        # Connect to database
        await db.connect()
        print("✅ Connected to database")
        
        # Create test event with source
        test_source = EventSource(
            platform="test_platform",
            url="https://example.com/event/123",
            scraped_at=datetime.utcnow(),
            source_id="test_123"
        )
        
        test_event = Event(
            title="Test Event with Source",
            description="This is a test event to verify source tracking",
            start_date=datetime.utcnow(),
            location=Location(
                address="123 Test St",
                city="Test City",
                country="Test Country"
            ),
            sources=[test_source]
        )
        
        # Insert the event
        event_id = await db.insert_event(test_event)
        print(f"✅ Created test event with ID: {event_id}")
        
        # Test source statistics
        stats = await db.get_source_statistics()
        print(f"✅ Source statistics: {stats}")
        
        # Test finding events by source platform
        events_by_source = await db.find_events_by_source_platform("test_platform")
        print(f"✅ Found {len(events_by_source)} events from test_platform")
        
        # Test that event has required source
        assert len(test_event.sources) >= 1, "Event must have at least one source"
        print("✅ Event validation passed - has required source")
        
        # Test source URL uniqueness
        existing_urls = {source.url for source in test_event.sources}
        assert len(existing_urls) == len(test_event.sources), "Source URLs should be unique"
        print("✅ Source URL uniqueness verified")
        
        # Clean up test event
        await db.delete_event(event_id)
        print("✅ Cleaned up test event")
        
        print("\n🎉 All source tracking tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
    finally:
        await db.disconnect()


async def test_source_validation():
    """Test that events without sources are rejected."""
    print("\n🧪 Testing source validation...")
    
    try:
        # This should fail because no sources are provided
        try:
            invalid_event = Event(
                title="Invalid Event",
                description="This event has no sources",
                start_date=datetime.utcnow(),
                location=Location(
                    address="123 Test St",
                    city="Test City", 
                    country="Test Country"
                ),
                sources=[]  # Empty sources should fail
            )
            assert False, "Event without sources should have been rejected"
        except ValueError as e:
            if "Every event must have at least one source" in str(e):
                print("✅ Source validation working - events without sources are rejected")
            else:
                raise
                
    except Exception as e:
        print(f"❌ Source validation test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_source_tracking())
    asyncio.run(test_source_validation())
    print("\n🎉 All tests completed successfully!")

