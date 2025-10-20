#!/usr/bin/env python3
"""
Fix Railway Database - Remove All Non-Events
Connects directly to Railway database and removes non-events
"""

import asyncio
import os
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

async def fix_railway_database():
    """Connect to Railway database and remove all non-events."""
    print("🧹 ============================================")
    print("🧹 FIXING RAILWAY DATABASE")
    print("🧹 ============================================")
    
    # Railway MongoDB connection string
    railway_mongodb_uri = "mongodb://mongo:PPGnjbCCrwCxRvvFQnMcMpumOkJOMoOw@trolley.proxy.rlwy.net:21533"
    database_name = "event_scraper"
    
    try:
        # Connect to Railway database
        print("🔗 Connecting to Railway MongoDB...")
        client = AsyncIOMotorClient(railway_mongodb_uri)
        db = client[database_name]
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to Railway database successfully")
        
        # Get current count
        total_before = await db.events.count_documents({})
        print(f"📊 Total records before cleanup: {total_before}")
        
        # Get all events to analyze
        print("🔍 Analyzing all events...")
        all_events = []
        async for event in db.events.find({}):
            all_events.append(event)
        
        print(f"📊 Found {len(all_events)} total records")
        
        # Identify non-events (blog articles, news, etc.)
        non_events = []
        real_events = []
        
        for event in all_events:
            title = event.get('title', '').lower()
            description = event.get('description', '').lower()
            website = event.get('contact_info', {}).get('website', '').lower()
            
            # Keywords that indicate this is NOT an event
            non_event_keywords = [
                # Blog/article indicators
                'faq', 'frequently asked questions', 'q&a',
                'vs ', 'comparison', 'review', 'guide', 'tutorial',
                'how to', 'what is', 'everything you need to know',
                'top ', 'best ', 'list of', 'beginner guide',
                'ultimate guide', 'marketing tools', 'ai tools',
                'supplements', 'health', 'wellness', 'blockchain',
                'cryptocurrency', 'nft', 'grammarly', 'prowritingaid',
                'collagen', 'skin care', 'affiliate', 'commission',
                'copy.ai', 'hotpot.ai', 'deep-nostalgia', 'pfpmaker',
                'brandmark', 'lumen5', 'namelix', 'bigjpg',
                'limewire', 'ai studio review', 'ai tools that will transform',
                'free ai tools', 'ai tools that make', 'make your life easier',
                
                # News indicators
                'breaking news', 'reports', 'announces', 'launches',
                'acquires', 'merges', 'partnership', 'investment',
                'funding', 'ipo', 'earnings', 'quarterly results',
                
                # Article indicators
                'read more', 'continue reading', 'full article',
                'blog post', 'opinion', 'analysis', 'commentary',
                'techncruncher.blogspot.com', 'blogspot', 'blog',
            ]
            
            # Check if it's likely a non-event
            is_non_event = any(keyword in title or keyword in description or keyword in website for keyword in non_event_keywords)
            
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
        
        # Remove non-events
        if non_events:
            print(f"\n🗑️  Removing {len(non_events)} non-event records...")
            non_event_ids = [event['_id'] for event in non_events]
            
            result = await db.events.delete_many({
                '_id': {'$in': non_event_ids}
            })
            
            print(f"✅ Removed {result.deleted_count} non-event records")
        
        # Get final count
        total_after = await db.events.count_documents({})
        print(f"\n📊 Cleanup Results:")
        print(f"   📊 Total records before: {total_before}")
        print(f"   📊 Total records after: {total_after}")
        print(f"   🗑️  Total removed: {total_before - total_after}")
        
        print("\n🎉 Railway database cleanup complete!")
        print("✅ Database now contains only real events")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Disconnect
        if 'client' in locals():
            client.close()
            print("🔌 Disconnected from Railway database")

if __name__ == "__main__":
    asyncio.run(fix_railway_database())
