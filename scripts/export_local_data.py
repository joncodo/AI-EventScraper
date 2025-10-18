#!/usr/bin/env python3
"""
Export Local Data Script

This script exports all data from your local MongoDB database to JSON files
that can be imported into the cloud database.

Usage:
    python scripts/export_local_data.py
    python scripts/export_local_data.py --output data/backup/
"""

import asyncio
import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add src directory to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from core.database import db
from core.models import Event

async def export_events(output_file: str = "data/backup/events_backup.json"):
    """Export all events from local database."""
    print("🔄 Exporting events from local database...")
    
    # Connect to local database
    await db.connect()
    
    try:
        # Get all events
        events = []
        async for event_doc in db.db.events.find():
            # Convert ObjectId to string for JSON serialization
            event_doc['_id'] = str(event_doc['_id'])
            if 'duplicate_of' in event_doc and event_doc['duplicate_of']:
                event_doc['duplicate_of'] = str(event_doc['duplicate_of'])
            events.append(event_doc)
        
        # Create backup directory
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write to JSON file
        with open(output_file, 'w') as f:
            json.dump(events, f, indent=2, default=str)
        
        print(f"✅ Exported {len(events)} events to {output_file}")
        
        # Create summary
        summary = {
            "export_date": datetime.now().isoformat(),
            "total_events": len(events),
            "cities": list(set(event.get('location', {}).get('city', 'Unknown') for event in events)),
            "categories": list(set(event.get('category', 'Unknown') for event in events)),
            "platforms": list(set(source.get('platform', 'Unknown') for event in events for source in event.get('sources', [])))
        }
        
        summary_file = output_file.replace('.json', '_summary.json')
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Created summary file: {summary_file}")
        
        return len(events)
        
    except Exception as e:
        print(f"❌ Error exporting events: {e}")
        raise
    finally:
        await db.disconnect()

async def get_local_stats():
    """Get statistics about local database."""
    print("📊 Getting local database statistics...")
    
    await db.connect()
    
    try:
        # Basic counts
        total_events = await db.db.events.count_documents({})
        
        # City counts
        pipeline = [
            {"$group": {"_id": "$location.city", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        top_cities = []
        async for doc in db.db.events.aggregate(pipeline):
            top_cities.append(f"{doc['_id']}: {doc['count']} events")
        
        # Category counts
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        top_categories = []
        async for doc in db.db.events.aggregate(pipeline):
            top_categories.append(f"{doc['_id']}: {doc['count']} events")
        
        # Platform counts
        pipeline = [
            {"$unwind": "$sources"},
            {"$group": {"_id": "$sources.platform", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        platform_counts = []
        async for doc in db.db.events.aggregate(pipeline):
            platform_counts.append(f"{doc['_id']}: {doc['count']} events")
        
        print(f"📊 Total events: {total_events}")
        print(f"📊 Top cities:")
        for city in top_cities:
            print(f"   {city}")
        print(f"📊 Top categories:")
        for category in top_categories:
            print(f"   {category}")
        print(f"📊 Platform distribution:")
        for platform in platform_counts:
            print(f"   {platform}")
        
    except Exception as e:
        print(f"❌ Error getting local stats: {e}")
        raise
    finally:
        await db.disconnect()

async def main():
    parser = argparse.ArgumentParser(description="Export local database data")
    parser.add_argument("--output", default="data/backup/events_backup.json", help="Output file path")
    parser.add_argument("--stats", action="store_true", help="Show local database statistics")
    
    args = parser.parse_args()
    
    if args.stats:
        await get_local_stats()
    else:
        await export_events(args.output)

if __name__ == "__main__":
    asyncio.run(main())
