#!/usr/bin/env python3
"""
Cloud Database Population Script

This script populates the cloud database with fresh event data by scraping
events from multiple sources for specified cities.

Usage:
    python scripts/populate_cloud_db.py --cities "New York,Los Angeles" --limit 100
    python scripts/populate_cloud_db.py --all-major-cities --limit 500
    python scripts/populate_cloud_db.py --sample-cities --limit 200
"""

import asyncio
import sys
import os
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

# Add src directory to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from core.database import db
from core.models import Event
from scrapers.scraper_manager import scraper_manager

# Major US cities for scraping
MAJOR_CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
    "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
    "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis",
    "Seattle", "Denver", "Washington", "Boston", "El Paso", "Nashville",
    "Detroit", "Oklahoma City", "Portland", "Las Vegas", "Memphis", "Louisville",
    "Baltimore", "Milwaukee", "Albuquerque", "Tucson", "Fresno", "Sacramento",
    "Mesa", "Kansas City", "Atlanta", "Long Beach", "Colorado Springs", "Raleigh",
    "Miami", "Virginia Beach", "Omaha", "Oakland", "Minneapolis", "Tulsa",
    "Arlington", "Tampa", "New Orleans", "Wichita", "Cleveland", "Bakersfield",
    "Aurora", "Anaheim", "Honolulu", "Santa Ana", "Corpus Christi", "Riverside",
    "Lexington", "Stockton", "Henderson", "Saint Paul", "St. Louis", "Milwaukee"
]

SAMPLE_CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
    "San Antonio", "San Diego", "Dallas", "San Jose"
]

async def scrape_city_events(city: str, country: str = "United States", limit: int = 100) -> int:
    """Scrape events for a specific city."""
    print(f"🔄 Scraping events for {city}, {country}...")
    
    try:
        # Use the scraper manager to get events
        events = await scraper_manager.scrape_events(city, country, limit)
        
        if events:
            print(f"✅ Found {len(events)} events for {city}")
            return len(events)
        else:
            print(f"⚠️  No events found for {city}")
            return 0
            
    except Exception as e:
        print(f"❌ Error scraping {city}: {e}")
        return 0

async def populate_database(cities: List[str], limit_per_city: int = 100):
    """Populate the database with events from specified cities."""
    print(f"🚀 Starting database population...")
    print(f"📊 Cities: {len(cities)}")
    print(f"📊 Limit per city: {limit_per_city}")
    
    # Connect to database
    await db.connect()
    
    try:
        total_events = 0
        successful_cities = 0
        
        for i, city in enumerate(cities, 1):
            print(f"\n📍 Processing city {i}/{len(cities)}: {city}")
            
            # Scrape events for this city
            event_count = await scrape_city_events(city, "United States", limit_per_city)
            
            if event_count > 0:
                total_events += event_count
                successful_cities += 1
            
            # Add delay between cities to be respectful
            if i < len(cities):
                print("⏳ Waiting 2 seconds before next city...")
                await asyncio.sleep(2)
        
        print(f"\n🎉 Database population complete!")
        print(f"📊 Total events: {total_events}")
        print(f"📊 Successful cities: {successful_cities}/{len(cities)}")
        
        # Get final database stats
        final_count = await db.db.events.count_documents({})
        print(f"📊 Total events in database: {final_count}")
        
    except Exception as e:
        print(f"❌ Error during database population: {e}")
        raise
    finally:
        await db.disconnect()

async def get_database_stats():
    """Get current database statistics."""
    print("📊 Getting database statistics...")
    
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
        
        print(f"📊 Total events: {total_events}")
        print(f"📊 Top cities:")
        for city in top_cities:
            print(f"   {city}")
        print(f"📊 Top categories:")
        for category in top_categories:
            print(f"   {category}")
        
    except Exception as e:
        print(f"❌ Error getting database stats: {e}")
        raise
    finally:
        await db.disconnect()

async def clear_database():
    """Clear all events from the database."""
    print("🗑️  Clearing database...")
    
    await db.connect()
    
    try:
        result = await db.db.events.delete_many({})
        print(f"✅ Deleted {result.deleted_count} events from database")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        raise
    finally:
        await db.disconnect()

async def main():
    parser = argparse.ArgumentParser(description="Populate cloud database with event data")
    parser.add_argument("--cities", help="Comma-separated list of cities to scrape")
    parser.add_argument("--all-major-cities", action="store_true", help="Scrape all major US cities")
    parser.add_argument("--sample-cities", action="store_true", help="Scrape sample of major cities")
    parser.add_argument("--limit", type=int, default=100, help="Limit events per city")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    parser.add_argument("--clear", action="store_true", help="Clear all events from database")
    
    args = parser.parse_args()
    
    if args.clear:
        await clear_database()
    elif args.stats:
        await get_database_stats()
    elif args.all_major_cities:
        await populate_database(MAJOR_CITIES, args.limit)
    elif args.sample_cities:
        await populate_database(SAMPLE_CITIES, args.limit)
    elif args.cities:
        cities = [city.strip() for city in args.cities.split(",")]
        await populate_database(cities, args.limit)
    else:
        print("Please specify cities to scrape. Use --help for options.")
        print("\nExamples:")
        print("  python scripts/populate_cloud_db.py --cities 'New York,Los Angeles' --limit 100")
        print("  python scripts/populate_cloud_db.py --sample-cities --limit 200")
        print("  python scripts/populate_cloud_db.py --all-major-cities --limit 500")

if __name__ == "__main__":
    asyncio.run(main())
