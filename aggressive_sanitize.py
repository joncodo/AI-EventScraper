#!/usr/bin/env python3
"""
Aggressive Database Sanitization Script
Removes specific non-event patterns we've identified
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the src directory to the path
sys.path.append('src')

from core.database import Database

async def aggressive_sanitize():
    """Remove specific non-event patterns from the database."""
    print("🧹 ============================================")
    print("🧹 AGGRESSIVE DATABASE SANITIZATION")
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
        
        # Specific patterns to remove
        patterns_to_remove = [
            # NFT and crypto articles
            {"title": {"$regex": "nft", "$options": "i"}},
            {"title": {"$regex": "blockchain", "$options": "i"}},
            {"title": {"$regex": "cryptocurrency", "$options": "i"}},
            {"title": {"$regex": "frequently asked questions", "$options": "i"}},
            
            # Grammar tool comparisons
            {"title": {"$regex": "grammarly", "$options": "i"}},
            {"title": {"$regex": "prowritingaid", "$options": "i"}},
            {"title": {"$regex": "vs ", "$options": "i"}},
            {"title": {"$regex": "comparison", "$options": "i"}},
            
            # AI tools articles
            {"title": {"$regex": "free ai tools", "$options": "i"}},
            {"title": {"$regex": "ai tools that make", "$options": "i"}},
            {"title": {"$regex": "make your life easier", "$options": "i"}},
            
            # Health and wellness articles
            {"title": {"$regex": "collagen", "$options": "i"}},
            {"title": {"$regex": "supplements", "$options": "i"}},
            {"title": {"$regex": "skin care", "$options": "i"}},
            
            # Marketing and affiliate articles
            {"title": {"$regex": "affiliate", "$options": "i"}},
            {"title": {"$regex": "commission", "$options": "i"}},
            {"title": {"$regex": "marketing tools", "$options": "i"}},
            
            # Blog domains
            {"contact_info.website": {"$regex": "blogspot", "$options": "i"}},
            {"contact_info.website": {"$regex": "techncruncher", "$options": "i"}},
            
            # Very long descriptions (likely articles)
            {"description": {"$regex": ".{2000,}"}},
        ]
        
        total_removed = 0
        
        for i, pattern in enumerate(patterns_to_remove):
            print(f"🔍 Checking pattern {i+1}/{len(patterns_to_remove)}: {pattern}")
            
            # Find matching events
            matching_events = []
            async for event in db.db.events.find(pattern):
                matching_events.append(event)
            
            if matching_events:
                print(f"   Found {len(matching_events)} matching events")
                
                # Show examples
                for j, event in enumerate(matching_events[:3]):
                    print(f"   Example {j+1}: {event.get('title', 'No title')[:60]}...")
                
                # Remove them
                result = await db.db.events.delete_many(pattern)
                removed_count = result.deleted_count
                total_removed += removed_count
                print(f"   ✅ Removed {removed_count} events")
            else:
                print(f"   No matching events found")
        
        # Get final count
        total_after = await db.db.events.count_documents({})
        print(f"\n📊 Sanitization Results:")
        print(f"   📊 Total records before: {total_before}")
        print(f"   📊 Total records after: {total_after}")
        print(f"   🗑️  Total removed: {total_removed}")
        
        print("\n🎉 Aggressive sanitization complete!")
        print("✅ Database should now contain only real events")
        
    except Exception as e:
        print(f"❌ Error during sanitization: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Disconnect
        await db.disconnect()
        print("🔌 Disconnected from database")

if __name__ == "__main__":
    asyncio.run(aggressive_sanitize())
