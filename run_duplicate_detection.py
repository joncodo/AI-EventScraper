#!/usr/bin/env python3
"""
Run Duplicate Detection on Existing Events

This script processes all existing events in the database to detect and handle duplicates.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from core.database import db
from core.duplicate_detector import AdvancedDuplicateDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_duplicate_detection():
    """Run duplicate detection on all existing events."""
    
    print("🔍 Starting Duplicate Detection on 61K+ Events")
    print("=" * 60)
    
    # Connect to database
    await db.connect()
    
    try:
        # Initialize duplicate detector
        detector = AdvancedDuplicateDetector()
        
        # Get total event count
        total_events = await db.db.events.count_documents({})
        print(f"📊 Total events in database: {total_events:,}")
        
        # Check if already processed
        processed_count = await db.db.events.count_documents({"duplicate_processed": True})
        print(f"📊 Already processed: {processed_count:,}")
        
        remaining_count = total_events - processed_count
        print(f"📊 Remaining to process: {remaining_count:,}")
        
        if remaining_count == 0:
            print("✅ All events have already been processed for duplicate detection!")
            return
        
        # Ask for confirmation
        print(f"\n⚠️  This will process {remaining_count:,} events for duplicate detection.")
        print("This may take a while depending on the number of events.")
        
        # Process events in batches
        batch_size = 100
        skip = processed_count
        processed = 0
        duplicates_found = 0
        review_needed = 0
        
        print(f"\n🚀 Starting batch processing (batch size: {batch_size})...")
        
        while skip < total_events:
            # Get batch of events
            events = []
            async for event in db.db.events.find({"duplicate_processed": {"$ne": True}}).skip(skip - processed_count).limit(batch_size):
                events.append(event)
            
            if not events:
                break
            
            print(f"\n📦 Processing batch {skip//batch_size + 1} ({len(events)} events)...")
            
            # Process each event in the batch
            for i, event in enumerate(events):
                try:
                    # Detect duplicates
                    duplicates = await detector.detect_duplicates(event)
                    
                    # Handle duplicates
                    updated_event = await detector.handle_duplicates(event)
                    
                    # Update in database
                    update_data = {
                        "duplicate_processed": True,
                        "duplicate_processed_at": datetime.now()
                    }
                    
                    if updated_event.get("duplicate_of"):
                        update_data.update({
                            "duplicate_of": updated_event["duplicate_of"],
                            "duplicate_confidence": updated_event["duplicate_confidence"],
                            "duplicate_type": updated_event["duplicate_type"]
                        })
                        duplicates_found += 1
                    
                    if updated_event.get("duplicate_review"):
                        update_data.update({
                            "duplicate_review": True,
                            "duplicate_candidates": updated_event["duplicate_candidates"]
                        })
                        review_needed += 1
                    
                    await db.db.events.update_one(
                        {"_id": event["_id"]},
                        {"$set": update_data}
                    )
                    
                    processed += 1
                    
                    # Progress update
                    if (i + 1) % 10 == 0:
                        print(f"   Processed {i + 1}/{len(events)} events in batch...")
                
                except Exception as e:
                    logger.error(f"Error processing event {event.get('_id')}: {e}")
                    continue
            
            skip += batch_size
            
            # Batch summary
            print(f"✅ Batch complete. Total processed: {processed:,}")
            print(f"   Duplicates found: {duplicates_found:,}")
            print(f"   Review needed: {review_needed:,}")
        
        # Final summary
        print(f"\n🎉 Duplicate Detection Complete!")
        print("=" * 60)
        print(f"📊 Total events processed: {processed:,}")
        print(f"🔍 Duplicates found: {duplicates_found:,}")
        print(f"⚠️  Events needing review: {review_needed:,}")
        print(f"✅ Clean events: {processed - duplicates_found - review_needed:,}")
        
        # Get final statistics
        final_stats = await get_duplicate_statistics()
        print(f"\n📈 Final Statistics:")
        print(f"   Total events: {final_stats['total_events']:,}")
        print(f"   Duplicate events: {final_stats['duplicate_events']:,}")
        print(f"   Review needed: {final_stats['review_needed']:,}")
        print(f"   Clean events: {final_stats['clean_events']:,}")
        print(f"   Duplicate rate: {final_stats['duplicate_rate']:.2%}")
        
    except Exception as e:
        logger.error(f"Error in duplicate detection: {e}")
        raise
    finally:
        await db.disconnect()

async def get_duplicate_statistics():
    """Get statistics about duplicate detection results."""
    try:
        # Get total events
        total_events = await db.db.events.count_documents({})
        
        # Get duplicate events
        duplicate_events = await db.db.events.count_documents({"duplicate_of": {"$exists": True}})
        
        # Get events needing review
        review_needed = await db.db.events.count_documents({"duplicate_review": True})
        
        # Get clean events
        clean_events = await db.db.events.count_documents({
            "duplicate_of": {"$exists": False},
            "duplicate_review": {"$ne": True}
        })
        
        # Calculate duplicate rate
        duplicate_rate = duplicate_events / total_events if total_events > 0 else 0
        
        return {
            "total_events": total_events,
            "duplicate_events": duplicate_events,
            "review_needed": review_needed,
            "clean_events": clean_events,
            "duplicate_rate": duplicate_rate
        }
        
    except Exception as e:
        logger.error(f"Error getting duplicate statistics: {e}")
        return {
            "total_events": 0,
            "duplicate_events": 0,
            "review_needed": 0,
            "clean_events": 0,
            "duplicate_rate": 0
        }

async def show_duplicate_examples():
    """Show examples of detected duplicates."""
    try:
        print(f"\n🔍 Example Duplicates Found:")
        print("-" * 40)
        
        # Get some duplicate examples
        duplicates = []
        async for event in db.db.events.find({"duplicate_of": {"$exists": True}}).limit(5):
            duplicates.append(event)
        
        for i, event in enumerate(duplicates, 1):
            print(f"\nDuplicate {i}:")
            print(f"   Title: {event.get('title', 'N/A')}")
            print(f"   City: {event.get('location', {}).get('city', 'N/A')}")
            print(f"   Category: {event.get('category', 'N/A')}")
            print(f"   Duplicate of: {event.get('duplicate_of', 'N/A')}")
            print(f"   Confidence: {event.get('duplicate_confidence', 0):.2f}")
            print(f"   Type: {event.get('duplicate_type', 'N/A')}")
        
        # Get some review examples
        print(f"\n⚠️  Events Needing Review:")
        print("-" * 40)
        
        reviews = []
        async for event in db.db.events.find({"duplicate_review": True}).limit(3):
            reviews.append(event)
        
        for i, event in enumerate(reviews, 1):
            print(f"\nReview {i}:")
            print(f"   Title: {event.get('title', 'N/A')}")
            print(f"   City: {event.get('location', {}).get('city', 'N/A')}")
            print(f"   Category: {event.get('category', 'N/A')}")
            candidates = event.get('duplicate_candidates', [])
            print(f"   Candidates: {len(candidates)} potential duplicates")
            for j, candidate in enumerate(candidates[:2], 1):
                print(f"     {j}. Similarity: {candidate.get('similarity', 0):.2f}, Confidence: {candidate.get('confidence', 0):.2f}")
        
    except Exception as e:
        logger.error(f"Error showing duplicate examples: {e}")

async def main():
    """Main function."""
    try:
        await run_duplicate_detection()
        await show_duplicate_examples()
        
        print(f"\n🎉 Duplicate detection process complete!")
        print("Your database is now optimized with duplicate detection.")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
