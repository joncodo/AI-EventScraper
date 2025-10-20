#!/usr/bin/env python3
"""
Remove Specific Non-Events Script
Removes the exact non-events we identified from the API response
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the src directory to the path
sys.path.append('src')

from core.database import Database

async def remove_specific_non_events():
    """Remove the specific non-events we identified."""
    print("🧹 ============================================")
    print("🧹 REMOVING SPECIFIC NON-EVENTS")
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
        print(f"📊 Total records before cleanup: {total_before}")
        
        # Specific titles to remove (exact matches from the API response)
        titles_to_remove = [
            "Most Frequently Asked Questions About NFTs(Non-Fungible Tokens)",
            "Top 9 Free AI Tools That Make Your Life Easier",
            "ProWritingAid VS Grammarly: Which Grammar Checker is Better in (2022) ?",
            "LimeWire AI Studio Review 2023: Details, Pricing & Features",
            "Top 10 AI Tools That Will Transform Your Content Creation in 2025"
        ]
        
        total_removed = 0
        
        for title in titles_to_remove:
            print(f"🔍 Looking for: {title[:50]}...")
            
            # Find and remove events with this exact title
            result = await db.db.events.delete_many({"title": title})
            removed_count = result.deleted_count
            
            if removed_count > 0:
                print(f"   ✅ Removed {removed_count} events with this title")
                total_removed += removed_count
            else:
                print(f"   No events found with this title")
        
        # Also remove any events from techncruncher.blogspot.com
        print(f"🔍 Removing events from techncruncher.blogspot.com...")
        result = await db.db.events.delete_many({
            "contact_info.website": {"$regex": "techncruncher.blogspot.com", "$options": "i"}
        })
        removed_count = result.deleted_count
        if removed_count > 0:
            print(f"   ✅ Removed {removed_count} events from techncruncher.blogspot.com")
            total_removed += removed_count
        
        # Remove any events with very long descriptions (likely articles)
        print(f"🔍 Removing events with very long descriptions...")
        result = await db.db.events.delete_many({
            "description": {"$regex": ".{3000,}"}
        })
        removed_count = result.deleted_count
        if removed_count > 0:
            print(f"   ✅ Removed {removed_count} events with very long descriptions")
            total_removed += removed_count
        
        # Get final count
        total_after = await db.db.events.count_documents({})
        print(f"\n📊 Cleanup Results:")
        print(f"   📊 Total records before: {total_before}")
        print(f"   📊 Total records after: {total_after}")
        print(f"   🗑️  Total removed: {total_removed}")
        
        print("\n🎉 Specific non-events cleanup complete!")
        print("✅ Database should now contain only real events")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Disconnect
        await db.disconnect()
        print("🔌 Disconnected from database")

if __name__ == "__main__":
    asyncio.run(remove_specific_non_events())
