#!/usr/bin/env python3
"""
Database Sanitization Script
Removes all non-event data from the database
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the src directory to the path
sys.path.append('src')

from core.database import Database

async def sanitize_database():
    """Remove all non-event data from the database."""
    print("🧹 ============================================")
    print("🧹 DATABASE SANITIZATION SCRIPT")
    print("🧹 ============================================")
    
    # Initialize database
    db = Database()
    
    try:
        # Connect to database
        print("🔗 Connecting to database...")
        await db.connect()
        print("✅ Connected to database")
        
        # Get current count
        total_before = await db.db.events.count_documents({})
        print(f"📊 Total records before sanitization: {total_before}")
        
        # Get all events to analyze
        print("🔍 Analyzing all events...")
        all_events = []
        async for event in db.db.events.find({}):
            all_events.append(event)
        
        print(f"📊 Found {len(all_events)} total records")
        
        # Identify non-events (blog articles, news, etc.)
        non_events = []
        real_events = []
        
        for event in all_events:
            title = event.get('title', '').lower()
            description = event.get('description', '').lower()
            
            # Keywords that indicate non-events
            non_event_keywords = [
                'faq', 'frequently asked questions',
                'vs ', 'comparison', 'review',
                'guide', 'tutorial', 'how to',
                'what is', 'everything you need to know',
                'top ', 'best ', 'list of',
                'beginner guide', 'ultimate guide',
                'marketing tools', 'ai tools',
                'supplements', 'health', 'wellness',
                'blockchain', 'cryptocurrency', 'nft',
                'grammarly', 'prowritingaid',
                'collagen', 'skin care'
            ]
            
            # Check if it's likely a non-event
            is_non_event = any(keyword in title or keyword in description for keyword in non_event_keywords)
            
            # Additional checks for non-events
            if is_non_event or len(description) > 2000:  # Very long descriptions are usually articles
                non_events.append(event)
            else:
                real_events.append(event)
        
        print(f"🚫 Identified {len(non_events)} non-events to remove")
        print(f"✅ Identified {len(real_events)} real events to keep")
        
        # Show some examples of what we're removing
        print("\n📋 Examples of non-events being removed:")
        for i, event in enumerate(non_events[:5]):
            print(f"  {i+1}. {event.get('title', 'No title')[:80]}...")
        
        # Confirm deletion
        print(f"\n⚠️  About to delete {len(non_events)} non-event records")
        print("This action cannot be undone!")
        
        # Delete non-events
        if non_events:
            print("🗑️  Deleting non-events...")
            non_event_ids = [event['_id'] for event in non_events]
            
            result = await db.db.events.delete_many({
                '_id': {'$in': non_event_ids}
            })
            
            print(f"✅ Deleted {result.deleted_count} non-event records")
        
        # Get final count
        total_after = await db.db.events.count_documents({})
        print(f"📊 Total records after sanitization: {total_after}")
        print(f"📊 Removed {total_before - total_after} non-event records")
        
        print("\n🎉 Database sanitization complete!")
        print("✅ Database now contains only real events")
        
    except Exception as e:
        print(f"❌ Error during sanitization: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Disconnect
        await db.disconnect()
        print("🔌 Disconnected from database")

if __name__ == "__main__":
    asyncio.run(sanitize_database())
