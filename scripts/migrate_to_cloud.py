#!/usr/bin/env python3
"""
Database Migration Script for Cloud Deployment

This script helps migrate data from local MongoDB to MongoDB Atlas cloud database.
It can export local data and import it to the cloud, or set up a fresh cloud database.

Usage:
    python scripts/migrate_to_cloud.py --export-local
    python scripts/migrate_to_cloud.py --import-cloud
    python scripts/migrate_to_cloud.py --setup-fresh
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
from core.config import settings

async def export_local_data(output_file: str = "data/backup/events_backup.json"):
    """Export all events from local database to JSON file."""
    print("🔄 Exporting local data...")
    
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
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
        raise
    finally:
        await db.disconnect()

async def import_to_cloud(backup_file: str = "data/backup/events_backup.json"):
    """Import events from JSON backup to cloud database."""
    print("🔄 Importing data to cloud database...")
    
    # Connect to cloud database
    await db.connect()
    
    try:
        # Read backup file
        with open(backup_file, 'r') as f:
            events = json.load(f)
        
        # Import events
        imported_count = 0
        for event_data in events:
            try:
                # Remove _id to let MongoDB generate new one
                if '_id' in event_data:
                    del event_data['_id']
                
                # Insert event
                await db.db.events.insert_one(event_data)
                imported_count += 1
                
            except Exception as e:
                print(f"⚠️  Error importing event: {e}")
                continue
        
        print(f"✅ Imported {imported_count} events to cloud database")
        
    except Exception as e:
        print(f"❌ Error importing data: {e}")
        raise
    finally:
        await db.disconnect()

async def setup_fresh_database():
    """Set up a fresh cloud database with indexes."""
    print("🔄 Setting up fresh cloud database...")
    
    # Connect to cloud database
    await db.connect()
    
    try:
        # Create indexes
        await db.db.events.create_index("location.city")
        await db.db.events.create_index("category")
        await db.db.events.create_index("start_date")
        await db.db.events.create_index("price")
        await db.db.events.create_index("ai_processed")
        await db.db.events.create_index([("location.city", 1), ("category", 1)])
        await db.db.events.create_index([("start_date", 1), ("location.city", 1)])
        await db.db.events.create_index([("category", 1), ("start_date", 1)])
        
        # Create text search index
        await db.db.events.create_index([
            ("title", "text"),
            ("description", "text"),
            ("category", "text"),
            ("tags", "text")
        ])
        
        print("✅ Fresh database setup complete with indexes")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        raise
    finally:
        await db.disconnect()

async def verify_cloud_connection():
    """Verify connection to cloud database."""
    print("🔄 Verifying cloud database connection...")
    
    try:
        await db.connect()
        
        # Test connection
        await db.client.admin.command('ping')
        
        # Get database info
        db_info = await db.db.command("dbStats")
        event_count = await db.db.events.count_documents({})
        
        print(f"✅ Connected to cloud database")
        print(f"📊 Database: {db_info['db']}")
        print(f"📊 Events: {event_count}")
        print(f"📊 Size: {db_info['dataSize']} bytes")
        
    except Exception as e:
        print(f"❌ Error connecting to cloud database: {e}")
        raise
    finally:
        await db.disconnect()

async def generate_sample_data(count: int = 100):
    """Generate sample events for testing."""
    print(f"🔄 Generating {count} sample events...")
    
    await db.connect()
    
    try:
        from faker import Faker
        import random
        from datetime import datetime, timedelta
        
        fake = Faker()
        
        # Sample data
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
        categories = ["Technology & IT", "Business & Networking", "Education & Training", "Community & Social", "Music & Entertainment", "Health & Wellness", "Sports & Fitness", "Food & Drink", "Arts & Culture", "Science & Nature"]
        platforms = ["Eventbrite", "Meetup", "Facebook Events", "LinkedIn Events"]
        
        events = []
        for i in range(count):
            start_date = fake.date_time_between(start_date='+1d', end_date='+30d')
            end_date = start_date + timedelta(hours=random.randint(1, 8))
            
            event = {
                "title": fake.sentence(nb_words=4),
                "description": fake.text(max_nb_chars=200),
                "start_date": start_date,
                "end_date": end_date,
                "location": {
                    "address": fake.street_address(),
                    "city": random.choice(cities),
                    "state": fake.state_abbr(),
                    "country": "United States",
                    "latitude": float(fake.latitude()),
                    "longitude": float(fake.longitude()),
                    "venue_name": fake.company()
                },
                "contact_info": {
                    "email": fake.email(),
                    "phone": fake.phone_number(),
                    "website": fake.url()
                },
                "price": str(random.randint(0, 100)),
                "category": random.choice(categories),
                "tags": random.sample(categories, random.randint(1, 3)),
                "sources": [{
                    "platform": random.choice(platforms),
                    "url": fake.url(),
                    "scraped_at": datetime.now()
                }],
                "ai_processed": random.choice([True, False]),
                "confidence_score": round(random.uniform(0.7, 1.0), 2),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            events.append(event)
        
        # Insert events
        await db.db.events.insert_many(events)
        print(f"✅ Generated and inserted {count} sample events")
        
    except ImportError:
        print("❌ Faker library not installed. Install with: pip install faker")
    except Exception as e:
        print(f"❌ Error generating sample data: {e}")
        raise
    finally:
        await db.disconnect()

async def main():
    parser = argparse.ArgumentParser(description="Database migration script for cloud deployment")
    parser.add_argument("--export-local", action="store_true", help="Export local data to JSON")
    parser.add_argument("--import-cloud", action="store_true", help="Import data from JSON to cloud")
    parser.add_argument("--setup-fresh", action="store_true", help="Set up fresh cloud database")
    parser.add_argument("--verify", action="store_true", help="Verify cloud database connection")
    parser.add_argument("--sample", type=int, help="Generate sample data (specify count)")
    parser.add_argument("--backup-file", default="data/backup/events_backup.json", help="Backup file path")
    
    args = parser.parse_args()
    
    if args.export_local:
        await export_local_data(args.backup_file)
    elif args.import_cloud:
        await import_to_cloud(args.backup_file)
    elif args.setup_fresh:
        await setup_fresh_database()
    elif args.verify:
        await verify_cloud_connection()
    elif args.sample:
        await generate_sample_data(args.sample)
    else:
        print("Please specify an action. Use --help for options.")

if __name__ == "__main__":
    asyncio.run(main())
