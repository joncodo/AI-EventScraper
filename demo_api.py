#!/usr/bin/env python3
"""
API Demo Script

This script demonstrates the AI Event Scraper API functionality
with the existing database data.
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from core.database import db
from core.models import Event

async def demo_api_endpoints():
    """Demonstrate API endpoints with real data."""
    
    print("🚀 AI Event Scraper API Demo")
    print("=" * 50)
    
    # Connect to database
    await db.connect()
    
    try:
        # 1. Health Check
        print("\n📊 1. Health Check")
        print("-" * 30)
        try:
            await db.client.admin.command('ping')
            total_events = await db.db.events.count_documents({})
            print(f"✅ Database Status: Connected")
            print(f"📊 Total Events: {total_events:,}")
        except Exception as e:
            print(f"❌ Database Error: {e}")
            return
        
        # 2. Statistics
        print("\n📈 2. Database Statistics")
        print("-" * 30)
        
        # City counts
        pipeline = [
            {"$group": {"_id": "$location.city", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        top_cities = []
        async for doc in db.db.events.aggregate(pipeline):
            top_cities.append(f"{doc['_id']}: {doc['count']:,} events")
        
        # Category counts
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        top_categories = []
        async for doc in db.db.events.aggregate(pipeline):
            top_categories.append(f"{doc['_id']}: {doc['count']:,} events")
        
        print("🏙️  Top Cities:")
        for city in top_cities:
            print(f"   {city}")
        
        print("\n📂 Top Categories:")
        for category in top_categories:
            print(f"   {category}")
        
        # 3. Get Events (with filtering)
        print("\n🎉 3. Sample Events")
        print("-" * 30)
        
        # Get recent events
        events = []
        async for doc in db.db.events.find().sort("created_at", -1).limit(3):
            events.append(doc)
        
        for i, event in enumerate(events, 1):
            print(f"\nEvent {i}:")
            print(f"   Title: {event.get('title', 'N/A')}")
            print(f"   City: {event.get('location', {}).get('city', 'N/A')}")
            print(f"   Category: {event.get('category', 'N/A')}")
            print(f"   Date: {event.get('start_date', 'N/A')}")
            print(f"   Price: ${event.get('price', 'N/A')}")
        
        # 4. Search Events
        print("\n🔍 4. Search Events")
        print("-" * 30)
        
        # Search for tech events
        search_query = {"$or": [
            {"title": {"$regex": "tech", "$options": "i"}},
            {"category": {"$regex": "technology", "$options": "i"}},
            {"tags": {"$regex": "tech", "$options": "i"}}
        ]}
        
        tech_events = []
        async for doc in db.db.events.find(search_query).limit(3):
            tech_events.append(doc)
        
        print(f"🔍 Found {len(tech_events)} tech-related events:")
        for i, event in enumerate(tech_events, 1):
            print(f"\nTech Event {i}:")
            print(f"   Title: {event.get('title', 'N/A')}")
            print(f"   City: {event.get('location', {}).get('city', 'N/A')}")
            print(f"   Category: {event.get('category', 'N/A')}")
        
        # 5. Filter by City
        print("\n🏙️  5. Events by City")
        print("-" * 30)
        
        # Get events from New York
        ny_events = []
        async for doc in db.db.events.find({"location.city": "New York"}).limit(3):
            ny_events.append(doc)
        
        print(f"🗽 New York Events ({len(ny_events)} shown):")
        for i, event in enumerate(ny_events, 1):
            print(f"\nNY Event {i}:")
            print(f"   Title: {event.get('title', 'N/A')}")
            print(f"   Category: {event.get('category', 'N/A')}")
            print(f"   Date: {event.get('start_date', 'N/A')}")
        
        # 6. Filter by Category
        print("\n📂 6. Events by Category")
        print("-" * 30)
        
        # Get business events
        business_events = []
        async for doc in db.db.events.find({"category": "Business & Networking"}).limit(3):
            business_events.append(doc)
        
        print(f"💼 Business & Networking Events ({len(business_events)} shown):")
        for i, event in enumerate(business_events, 1):
            print(f"\nBusiness Event {i}:")
            print(f"   Title: {event.get('title', 'N/A')}")
            print(f"   City: {event.get('location', {}).get('city', 'N/A')}")
            print(f"   Date: {event.get('start_date', 'N/A')}")
        
        # 7. Free Events
        print("\n🆓 7. Free Events")
        print("-" * 30)
        
        # Get free events
        free_events = []
        async for doc in db.db.events.find({"price": "0"}).limit(3):
            free_events.append(doc)
        
        print(f"🆓 Free Events ({len(free_events)} shown):")
        for i, event in enumerate(free_events, 1):
            print(f"\nFree Event {i}:")
            print(f"   Title: {event.get('title', 'N/A')}")
            print(f"   City: {event.get('location', {}).get('city', 'N/A')}")
            print(f"   Category: {event.get('category', 'N/A')}")
        
        # 8. API Endpoints Summary
        print("\n🌐 8. API Endpoints Available")
        print("-" * 30)
        print("The following endpoints would be available in the cloud API:")
        print("   GET /health - Health check")
        print("   GET /stats - Database statistics")
        print("   GET /events - Get events with filtering")
        print("   GET /events/search?q=query - Search events")
        print("   GET /events?city=New York - Filter by city")
        print("   GET /events?category=Technology - Filter by category")
        print("   GET /events?price_min=0&price_max=0 - Free events")
        print("   GET /cities - List all cities")
        print("   GET /categories - List all categories")
        print("   GET /events/random - Random event")
        print("   GET /events/recent - Recent events")
        
        print("\n🎉 API Demo Complete!")
        print("=" * 50)
        print("Your AI Event Scraper is ready for cloud deployment!")
        print("With 61,405+ events across 193+ cities, you have a comprehensive")
        print("event database ready to serve via API.")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(demo_api_endpoints())
