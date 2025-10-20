#!/usr/bin/env python3
"""
Quick database status checker to see if events are being collected.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
project_root = Path(__file__).resolve().parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from core.database import db

async def check_database_status():
    """Check the current status of the database and event collection."""
    print("🔍 Checking Database Status...")
    print("=" * 50)
    
    try:
        # Connect to database
        await db.connect()
        print("✅ Connected to database successfully")
        
        # Get basic stats
        total_events = await db.db.events.count_documents({})
        print(f"📊 Total events in database: {total_events}")
        
        if total_events > 0:
            # Get recent events (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_events = await db.db.events.count_documents({
                "created_at": {"$gte": yesterday}
            })
            print(f"📈 Events added in last 24 hours: {recent_events}")
            
            # Get events by city
            pipeline = [
                {"$group": {"_id": "$location.city", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            city_stats = []
            async for doc in db.db.events.aggregate(pipeline):
                city_stats.append(f"  {doc['_id']}: {doc['count']} events")
            
            if city_stats:
                print("🏙️  Top cities by event count:")
                for stat in city_stats:
                    print(stat)
            
            # Get events by platform
            pipeline = [
                {"$unwind": "$sources"},
                {"$group": {"_id": "$sources.platform", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            platform_stats = []
            async for doc in db.db.events.aggregate(pipeline):
                platform_stats.append(f"  {doc['_id']}: {doc['count']} events")
            
            if platform_stats:
                print("🔗 Events by platform:")
                for stat in platform_stats:
                    print(stat)
            
            # Get sample recent events
            print("\n📅 Sample recent events:")
            recent_events_cursor = db.db.events.find().sort("created_at", -1).limit(5)
            async for event in recent_events_cursor:
                title = event.get('title', 'No title')[:50]
                city = event.get('location', {}).get('city', 'Unknown')
                created = event.get('created_at', 'Unknown')
                print(f"  • {title}... ({city}) - {created}")
        
        else:
            print("⚠️  No events found in database")
            print("   This could mean:")
            print("   - Scraping hasn't started yet")
            print("   - All scrapers are failing")
            print("   - Database connection issues")
        
        # Check if background worker is configured
        worker_loop_seconds = os.getenv("WORKER_LOOP_SECONDS", "600")
        scraping_cities = os.getenv("SCRAPING_CITIES", "New York,Los Angeles,Chicago,Houston,Phoenix")
        
        print(f"\n⚙️  Configuration:")
        print(f"   Worker loop interval: {worker_loop_seconds} seconds")
        print(f"   Target cities: {scraping_cities}")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(check_database_status())
