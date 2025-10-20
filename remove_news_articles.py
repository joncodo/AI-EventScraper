#!/usr/bin/env python3
"""
Remove News Articles from Railway Database
Removes news articles and keeps only actual events
"""

import asyncio
import os
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

async def remove_news_articles():
    """Remove news articles from Railway database."""
    print("🧹 ============================================")
    print("🧹 REMOVING NEWS ARTICLES FROM RAILWAY DB")
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
        
        # News article patterns to remove
        news_patterns = [
            # News sources
            {"contact_info.website": {"$regex": "npr.org", "$options": "i"}},
            {"contact_info.website": {"$regex": "cnn.com", "$options": "i"}},
            {"contact_info.website": {"$regex": "bbc.co.uk", "$options": "i"}},
            {"contact_info.website": {"$regex": "reuters.com", "$options": "i"}},
            {"contact_info.website": {"$regex": "techcrunch.com", "$options": "i"}},
            
            # News keywords in titles
            {"title": {"$regex": "trump", "$options": "i"}},
            {"title": {"$regex": "gaza", "$options": "i"}},
            {"title": {"$regex": "ceasefire", "$options": "i"}},
            {"title": {"$regex": "shutdown", "$options": "i"}},
            {"title": {"$regex": "tariffs", "$options": "i"}},
            {"title": {"$regex": "diwali", "$options": "i"}},
            {"title": {"$regex": "bolivia", "$options": "i"}},
            {"title": {"$regex": "president", "$options": "i"}},
            {"title": {"$regex": "election", "$options": "i"}},
            {"title": {"$regex": "college", "$options": "i"}},
            {"title": {"$regex": "university", "$options": "i"}},
            {"title": {"$regex": "administration", "$options": "i"}},
            {"title": {"$regex": "senator", "$options": "i"}},
            {"title": {"$regex": "vote", "$options": "i"}},
            {"title": {"$regex": "party", "$options": "i"}},
            {"title": {"$regex": "economic", "$options": "i"}},
            {"title": {"$regex": "turmoil", "$options": "i"}},
            {"title": {"$regex": "kenny loggins", "$options": "i"}},
            {"title": {"$regex": "danger zone", "$options": "i"}},
            {"title": {"$regex": "truth social", "$options": "i"}},
            {"title": {"$regex": "fake video", "$options": "i"}},
            {"title": {"$regex": "musician", "$options": "i"}},
            {"title": {"$regex": "scrubbed", "$options": "i"}},
            {"title": {"$regex": "featured", "$options": "i"}},
            {"title": {"$regex": "violated", "$options": "i"}},
            {"title": {"$regex": "enters day", "$options": "i"}},
            {"title": {"$regex": "lawmakers", "$options": "i"}},
            {"title": {"$regex": "government", "$options": "i"}},
            {"title": {"$regex": "israel", "$options": "i"}},
            {"title": {"$regex": "hamas", "$options": "i"}},
            {"title": {"$regex": "clashes", "$options": "i"}},
            {"title": {"$regex": "weekend", "$options": "i"}},
            {"title": {"$regex": "pressures", "$options": "i"}},
            {"title": {"$regex": "festival of lights", "$options": "i"}},
            {"title": {"$regex": "celebrated around the world", "$options": "i"}},
            {"title": {"$regex": "steep tariffs", "$options": "i"}},
            {"title": {"$regex": "indian goods", "$options": "i"}},
            {"title": {"$regex": "preparing for the holiday", "$options": "i"}},
            {"title": {"$regex": "costly", "$options": "i"}},
            {"title": {"$regex": "deadline", "$options": "i"}},
            {"title": {"$regex": "compact", "$options": "i"}},
            {"title": {"$regex": "looms", "$options": "i"}},
            {"title": {"$regex": "schools signal", "$options": "i"}},
            {"title": {"$regex": "dissent", "$options": "i"}},
            {"title": {"$regex": "original nine", "$options": "i"}},
            {"title": {"$regex": "received", "$options": "i"}},
            {"title": {"$regex": "academic excellence", "$options": "i"}},
            {"title": {"$regex": "higher education", "$options": "i"}},
            {"title": {"$regex": "majority have indicated", "$options": "i"}},
            {"title": {"$regex": "not planning", "$options": "i"}},
            {"title": {"$regex": "signing", "$options": "i"}},
            {"title": {"$regex": "centrist", "$options": "i"}},
            {"title": {"$regex": "rodrigo paz", "$options": "i"}},
            {"title": {"$regex": "wins", "$options": "i"}},
            {"title": {"$regex": "presidential runoff", "$options": "i"}},
            {"title": {"$regex": "topping", "$options": "i"}},
            {"title": {"$regex": "right-wing", "$options": "i"}},
            {"title": {"$regex": "rival", "$options": "i"}},
            {"title": {"$regex": "won bolivia", "$options": "i"}},
            {"title": {"$regex": "presidency", "$options": "i"}},
            {"title": {"$regex": "54% of the vote", "$options": "i"}},
            {"title": {"$regex": "ending 20 years", "$options": "i"}},
            {"title": {"$regex": "rule by", "$options": "i"}},
            {"title": {"$regex": "movement toward socialism", "$options": "i"}},
            {"title": {"$regex": "amid", "$options": "i"}},
        ]
        
        total_removed = 0
        
        for i, pattern in enumerate(news_patterns):
            print(f"🔍 Checking pattern {i+1}/{len(news_patterns)}: {str(pattern)[:50]}...")
            
            # Find and remove events matching this pattern
            result = await db.events.delete_many(pattern)
            removed_count = result.deleted_count
            
            if removed_count > 0:
                print(f"   ✅ Removed {removed_count} events")
                total_removed += removed_count
        
        # Get final count
        total_after = await db.events.count_documents({})
        print(f"\n📊 Cleanup Results:")
        print(f"   📊 Total records before: {total_before}")
        print(f"   📊 Total records after: {total_after}")
        print(f"   🗑️  Total removed: {total_removed}")
        
        print("\n🎉 News articles cleanup complete!")
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
    asyncio.run(remove_news_articles())
