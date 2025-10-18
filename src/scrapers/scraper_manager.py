"""Scraper manager for coordinating multiple scrapers."""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .base_scraper import BaseScraper
from .eventbrite_scraper import EventbriteScraper
from .meetup_scraper import MeetupScraper
from .facebook_scraper import FacebookScraper
from core.models import Event, ScrapeRequest
from ai.ai_processor import ai_processor
from core.database import db

logger = logging.getLogger(__name__)


class ScraperManager:
    """Manager for coordinating multiple event scrapers."""
    
    def __init__(self):
        self.scrapers: List[BaseScraper] = [
            EventbriteScraper(),
            MeetupScraper(),
            FacebookScraper()
        ]
    
    async def scrape_all_events(self, request: ScrapeRequest) -> List[Event]:
        """Scrape events from all available sources."""
        all_events = []
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(3)  # Max 3 scrapers running at once
        
        async def scrape_with_semaphore(scraper: BaseScraper):
            async with semaphore:
                try:
                    async with scraper:
                        events = await scraper.scrape_events(
                            city=request.city,
                            country=request.country,
                            radius_km=request.radius_km,
                            start_date=request.start_date,
                            end_date=request.end_date
                        )
                        logger.info(f"Scraped {len(events)} events from {scraper.platform_name}")
                        return events
                except Exception as e:
                    logger.error(f"Error scraping {scraper.platform_name}: {e}")
                    return []
        
        # Run all scrapers concurrently
        tasks = [scrape_with_semaphore(scraper) for scraper in self.scrapers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect all events
        for result in results:
            if isinstance(result, list):
                all_events.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Scraper task failed: {result}")
        
        logger.info(f"Total events scraped: {len(all_events)}")
        
        # Process events with AI
        processed_events = await self._process_events_with_ai(all_events)
        
        # Find and merge duplicates
        deduplicated_events = await self._deduplicate_events(processed_events)
        
        return deduplicated_events
    
    async def _process_events_with_ai(self, events: List[Event]) -> List[Event]:
        """Process events with AI to enhance data quality."""
        logger.info(f"Processing {len(events)} events with AI...")
        
        processed_events = []
        
        # Process events in batches to avoid overwhelming the API
        batch_size = 10
        for i in range(0, len(events), batch_size):
            batch = events[i:i + batch_size]
            
            # Process batch concurrently
            tasks = [ai_processor.process_event(event) for event in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Event):
                    processed_events.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"AI processing failed: {result}")
        
        logger.info(f"AI processing completed. {len(processed_events)} events processed.")
        return processed_events
    
    async def _deduplicate_events(self, events: List[Event]) -> List[Event]:
        """Find and merge duplicate events."""
        logger.info(f"Deduplicating {len(events)} events...")
        
        if len(events) <= 1:
            return events
        
        # Find duplicates
        duplicates = await ai_processor.find_duplicates(events, similarity_threshold=0.8)
        
        # Create a set of events to remove
        events_to_remove = set()
        merged_events = []
        
        # Process duplicates
        for event1, event2, similarity in duplicates:
            if event1 in events_to_remove or event2 in events_to_remove:
                continue
            
            # Merge events (keep the one with more sources or better data)
            if len(event1.sources) >= len(event2.sources):
                primary_event = event1
                secondary_event = event2
            else:
                primary_event = event2
                secondary_event = event1
            
            # Merge the events
            merged_event = await ai_processor.merge_events(primary_event, secondary_event)
            merged_events.append(merged_event)
            
            # Mark both original events for removal
            events_to_remove.add(event1)
            events_to_remove.add(event2)
        
        # Add non-duplicate events
        for event in events:
            if event not in events_to_remove:
                merged_events.append(event)
        
        logger.info(f"Deduplication completed. {len(merged_events)} unique events remaining.")
        return merged_events
    
    async def save_events_to_database(self, events: List[Event]) -> List[str]:
        """Save events to the database."""
        if not events:
            return []
        
        try:
            # Check for existing events to avoid duplicates
            existing_events = []
            new_events = []
            
            for event in events:
                # Check if event already exists
                existing = await db.find_duplicate_events(event, similarity_threshold=0.9)
                
                if existing:
                    # Update existing event with new sources
                    existing_event = existing[0]
                    existing_event.sources.extend(event.sources)
                    existing_event.updated_at = datetime.utcnow()
                    
                    # Update in database
                    await db.update_event(str(existing_event.id), existing_event.dict())
                    existing_events.append(str(existing_event.id))
                else:
                    new_events.append(event)
            
            # Insert new events
            new_event_ids = []
            if new_events:
                new_event_ids = await db.insert_events(new_events)
            
            all_event_ids = existing_events + new_event_ids
            
            logger.info(f"Saved {len(new_events)} new events and updated {len(existing_events)} existing events.")
            return all_event_ids
            
        except Exception as e:
            logger.error(f"Error saving events to database: {e}")
            return []
    
    async def get_scraper_status(self) -> Dict[str, Any]:
        """Get status of all scrapers."""
        status = {}
        
        for scraper in self.scrapers:
            try:
                # Test scraper connectivity
                async with scraper:
                    # Make a simple request to test connectivity
                    test_url = scraper.get_base_url()
                    response = await scraper.make_request(test_url)
                    
                    status[scraper.platform_name] = {
                        "status": "online" if response else "offline",
                        "base_url": test_url
                    }
            except Exception as e:
                status[scraper.platform_name] = {
                    "status": "error",
                    "error": str(e),
                    "base_url": scraper.get_base_url()
                }
        
        return status


# Global scraper manager instance
scraper_manager = ScraperManager()

