#!/usr/bin/env python3
"""
Remove ALL News Content from Railway Database
Removes all news articles and keeps only actual events
"""

import asyncio
import os
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

async def remove_all_news():
    """Remove all news content from Railway database."""
    print("🧹 ============================================")
    print("🧹 REMOVING ALL NEWS CONTENT FROM RAILWAY DB")
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
        
        # Remove ALL news sources and content
        news_sources = [
            {"contact_info.website": {"$regex": "bbc.com", "$options": "i"}},
            {"contact_info.website": {"$regex": "bbc.co.uk", "$options": "i"}},
            {"contact_info.website": {"$regex": "npr.org", "$options": "i"}},
            {"contact_info.website": {"$regex": "cnn.com", "$options": "i"}},
            {"contact_info.website": {"$regex": "reuters.com", "$options": "i"}},
            {"contact_info.website": {"$regex": "techcrunch.com", "$options": "i"}},
            {"contact_info.website": {"$regex": "feeds.bbci.co.uk", "$options": "i"}},
            {"contact_info.website": {"$regex": "feeds.npr.org", "$options": "i"}},
        ]
        
        total_removed = 0
        
        for i, pattern in enumerate(news_sources):
            print(f"🔍 Removing news source {i+1}/{len(news_sources)}: {str(pattern)[:50]}...")
            
            result = await db.events.delete_many(pattern)
            removed_count = result.deleted_count
            
            if removed_count > 0:
                print(f"   ✅ Removed {removed_count} events")
                total_removed += removed_count
        
        # Also remove any events with very short titles (likely news headlines)
        print(f"🔍 Removing events with very short titles...")
        result = await db.events.delete_many({
            "title": {"$regex": "^.{1,20}$"}  # Titles with 1-20 characters
        })
        removed_count = result.deleted_count
        if removed_count > 0:
            print(f"   ✅ Removed {removed_count} events with short titles")
            total_removed += removed_count
        
        # Remove any events with generic descriptions
        print(f"🔍 Removing events with generic descriptions...")
        result = await db.events.delete_many({
            "description": {"$regex": "^(Think you can|The move will|The BBC's|Brentford earn|Emeka Ilione's|Watch: BBC|Pizza Hut to close)"}
        })
        removed_count = result.deleted_count
        if removed_count > 0:
            print(f"   ✅ Removed {removed_count} events with generic descriptions")
            total_removed += removed_count
        
        # Get final count
        total_after = await db.events.count_documents({})
        print(f"\n📊 Cleanup Results:")
        print(f"   📊 Total records before: {total_before}")
        print(f"   📊 Total records after: {total_after}")
        print(f"   🗑️  Total removed: {total_removed}")
        
        print("\n🎉 All news content cleanup complete!")
        print("✅ Database should now contain only real events")
        
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
    asyncio.run(remove_all_news())
