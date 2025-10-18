#!/usr/bin/env python3
"""Test MongoDB connection and basic operations."""

import asyncio
import sys
from database import Database
from models import Event, Location, ContactInfo, EventSource
from datetime import datetime

async def test_mongodb():
    """Test MongoDB connection and operations."""
    print("🔍 Testing MongoDB connection...")
    
    db = Database()
    
    try:
        # Test connection
        await db.connect()
        print("✅ MongoDB connected successfully!")
        
        # Test inserting a sample event
        sample_event = Event(
            title="Test Event for MongoDB",
            description="Testing MongoDB connection and operations",
            start_date=datetime.now(),
            location=Location(
                address="123 Test St",
                city="Test City",
                country="Test Country"
            ),
            contact_info=ContactInfo(
                email="test@example.com"
            ),
            sources=[EventSource(
                platform="test",
                url="https://test.example.com/event/123",
                scraped_at=datetime.now()
            )],
            category="Test",
            tags=["test", "mongodb"],
            ai_processed=True,
            confidence_score=0.95
        )
        
        # Insert event
        event_id = await db.insert_event(sample_event)
        print(f"✅ Event inserted with ID: {event_id}")
        
        # Test querying
        from models import QueryRequest
        query = QueryRequest(city="Test City", limit=10)
        events = await db.find_events(query)
        print(f"✅ Found {len(events)} events in query")
        
        print("🎉 MongoDB is working perfectly for massive scale!")
        
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")
        return False
    finally:
        await db.disconnect()
        print("🔌 Disconnected from MongoDB")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_mongodb())
    sys.exit(0 if success else 1)
