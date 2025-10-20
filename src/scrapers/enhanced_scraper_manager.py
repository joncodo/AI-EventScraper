"""Enhanced scraper manager with stealth capabilities."""
import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime

from .base_scraper import BaseScraper
from .meetup_scraper import MeetupScraper
from .facebook_scraper import FacebookScraper
from core.models import Event, ScrapeRequest
from ai.ai_processor import ai_processor
from core.database import db

# Initialize logger after imports
logger = logging.getLogger(__name__)

# Import enhanced scrapers
from .enhanced_eventbrite_scraper import EnhancedEventbriteScraper
from .rss_scraper import RSSEventScraper
from .api_scraper import APIEventScraper
from .local_events_scraper import LocalEventsScraper


class EnhancedScraperManager:
    """Enhanced manager for coordinating multiple event scrapers with stealth capabilities."""
    
    def __init__(self):
        # Alternative data sources (most reliable)
        self.alternative_scrapers = [
            RSSEventScraper(),
            APIEventScraper(),
            LocalEventsScraper(),
        ]
        
        # Enhanced web scrapers (stealth)
        self.enhanced_scrapers = [
            EnhancedEventbriteScraper(),
        ]
        
        # Regular web scrapers (fallback)
        self.regular_scrapers: List[BaseScraper] = [
            MeetupScraper(),
            FacebookScraper()
        ]
        
        # All scrapers combined (prioritized by reliability)
        self.all_scrapers = self.alternative_scrapers + self.enhanced_scrapers + self.regular_scrapers
    
    async def scrape_all_events(self, request: ScrapeRequest) -> List[Event]:
        """Scrape events from all available sources with enhanced stealth."""
        all_events = []
        
        logger.info(f"🚀 Enhanced scraper manager starting for {request.city}, {request.country}")
        logger.info(f"📊 Available scrapers: {len(self.alternative_scrapers)} alternative, {len(self.enhanced_scrapers)} enhanced, {len(self.regular_scrapers)} regular")
        logger.info(f"📅 Date range: {request.start_date} to {request.end_date}")
        logger.info(f"📍 Location: {request.city}, {request.country} (radius: {request.radius_km}km)")
        
        # Create semaphore to limit concurrent requests (more conservative)
        semaphore = asyncio.Semaphore(3)  # Max 3 scrapers running at once
        
        async def scrape_alternative_with_semaphore(scraper):
            async with semaphore:
                try:
                    logger.info(f"🔍 Starting alternative scraper: {scraper.platform_name}")
                    # Initialize session for alternative scrapers that need it
                    if hasattr(scraper, '__aenter__') and hasattr(scraper, '__aexit__'):
                        async with scraper:
                            events = await scraper.scrape_events(
                                city=request.city,
                                country=request.country,
                                radius_km=request.radius_km,
                                start_date=request.start_date,
                                end_date=request.end_date
                            )
                    else:
                        events = await scraper.scrape_events(
                            city=request.city,
                            country=request.country,
                            radius_km=request.radius_km,
                            start_date=request.start_date,
                            end_date=request.end_date
                        )
                    logger.info(f"✅ Alternative scraper {scraper.platform_name} found {len(events)} events")
                    if events:
                        logger.info(f"📋 Sample event from {scraper.platform_name}: {events[0].title if events[0].title else 'No title'}")
                    return events
                except Exception as e:
                    logger.error(f"❌ Error with alternative scraper {scraper.platform_name}: {e}")
                    logger.error(f"❌ Error type: {type(e).__name__}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                    return []
        
        async def scrape_enhanced_with_semaphore(scraper):
            async with semaphore:
                try:
                    # Initialize session for enhanced scrapers that need it
                    if hasattr(scraper, '__aenter__') and hasattr(scraper, '__aexit__'):
                        async with scraper:
                            events = await scraper.scrape_events(
                                city=request.city,
                                country=request.country,
                                radius_km=request.radius_km,
                                start_date=request.start_date,
                                end_date=request.end_date
                            )
                    else:
                        events = await scraper.scrape_events(
                            city=request.city,
                            country=request.country,
                            radius_km=request.radius_km,
                            start_date=request.start_date,
                            end_date=request.end_date
                        )
                    logger.info(f"Enhanced scraper found {len(events)} events from {scraper.platform_name}")
                    return events
                except Exception as e:
                    logger.error(f"Error with enhanced scraper {scraper.platform_name}: {e}")
                    return []
        
        async def scrape_regular_with_semaphore(scraper: BaseScraper):
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
                        logger.info(f"Regular scraper found {len(events)} events from {scraper.platform_name}")
                        return events
                except Exception as e:
                    logger.error(f"Error with regular scraper {scraper.platform_name}: {e}")
                    return []
        
        # Run alternative scrapers first (most reliable)
        logger.info(f"🚀 Starting {len(self.alternative_scrapers)} alternative scrapers...")
        alternative_tasks = [scrape_alternative_with_semaphore(scraper) for scraper in self.alternative_scrapers]
        alternative_results = await asyncio.gather(*alternative_tasks, return_exceptions=True)
        
        # Collect alternative scraper results
        alternative_events = 0
        for i, result in enumerate(alternative_results):
            scraper_name = self.alternative_scrapers[i].platform_name if i < len(self.alternative_scrapers) else f"Unknown-{i}"
            if isinstance(result, list):
                all_events.extend(result)
                alternative_events += len(result)
                logger.info(f"📊 Alternative scraper {scraper_name} contributed {len(result)} events")
            elif isinstance(result, Exception):
                logger.error(f"❌ Alternative scraper {scraper_name} task failed: {result}")
        
        logger.info(f"📈 Alternative scrapers total: {alternative_events} events")
        
        # Run enhanced scrapers (stealth web scraping)
        enhanced_tasks = [scrape_enhanced_with_semaphore(scraper) for scraper in self.enhanced_scrapers]
        enhanced_results = await asyncio.gather(*enhanced_tasks, return_exceptions=True)
        
        # Collect enhanced scraper results
        for result in enhanced_results:
            if isinstance(result, list):
                all_events.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Enhanced scraper task failed: {result}")
        
        # If we got some events from alternative/enhanced scrapers, we can be more selective with regular scrapers
        if all_events:
            logger.info(f"Alternative/Enhanced scrapers found {len(all_events)} events, running regular scrapers with reduced concurrency")
            # Reduce concurrency for regular scrapers
            semaphore = asyncio.Semaphore(1)
        
        # Run regular scrapers
        regular_tasks = [scrape_regular_with_semaphore(scraper) for scraper in self.regular_scrapers]
        regular_results = await asyncio.gather(*regular_tasks, return_exceptions=True)
        
        # Collect regular scraper results
        for result in regular_results:
            if isinstance(result, list):
                all_events.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Regular scraper task failed: {result}")
        
        logger.info(f"🎯 Total events scraped from all sources: {len(all_events)}")
        
        if not all_events:
            logger.warning("⚠️ No events found from any scraper - this may indicate:")
            logger.warning("   - All data sources are blocked or returning errors")
            logger.warning("   - Date range is too restrictive")
            logger.warning("   - Location parameters are invalid")
            logger.warning("   - Network connectivity issues")
            return []
        
        # Process events with AI
        logger.info(f"🤖 Processing {len(all_events)} events with AI...")
        processed_events = await self._process_events_with_ai(all_events)
        
        # Find and merge duplicates
        logger.info(f"🔍 Deduplicating {len(processed_events)} processed events...")
        deduplicated_events = await self._deduplicate_events(processed_events)
        
        logger.info(f"✅ Final result: {len(deduplicated_events)} unique events ready for database")
        return deduplicated_events
    
    async def _process_events_with_ai(self, events: List[Event]) -> List[Event]:
        """Process events with AI to enhance data quality."""
        logger.info(f"Processing {len(events)} events with AI...")
        
        processed_events = []
        
        # Process events in smaller batches to avoid overwhelming the API
        batch_size = 5  # Reduced batch size
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
            
            # Add delay between batches to be respectful
            if i + batch_size < len(events):
                await asyncio.sleep(1)
        
        logger.info(f"AI processing completed. {len(processed_events)} events processed.")
        return processed_events
    
    async def _deduplicate_events(self, events: List[Event]) -> List[Event]:
        """Find and merge duplicate events."""
        logger.info(f"Deduplicating {len(events)} events...")
        
        if len(events) <= 1:
            return events
        
        # Find duplicates
        duplicates = await ai_processor.find_duplicates(events, similarity_threshold=0.8)
        
        # Create a set of event indices to remove (since Event objects are not hashable)
        events_to_remove = set()
        merged_events = []
        
        # Create a mapping from events to their indices
        event_to_index = {id(event): i for i, event in enumerate(events)}
        
        # Process duplicates
        for event1, event2, similarity in duplicates:
            event1_idx = event_to_index.get(id(event1))
            event2_idx = event_to_index.get(id(event2))
            
            if event1_idx in events_to_remove or event2_idx in events_to_remove:
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
            events_to_remove.add(event1_idx)
            events_to_remove.add(event2_idx)
        
        # Add non-duplicate events
        for i, event in enumerate(events):
            if i not in events_to_remove:
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
                    await db.update_event(str(existing_event.id), existing_event.model_dump())
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
        
        # Test alternative scrapers
        for scraper in self.alternative_scrapers:
            try:
                status[scraper.platform_name] = {
                    "status": "alternative",
                    "type": "api/rss",
                    "reliability": "high"
                }
            except Exception as e:
                status[scraper.platform_name] = {
                    "status": "error",
                    "error": str(e),
                    "type": "alternative"
                }
        
        # Test enhanced scrapers
        for scraper in self.enhanced_scrapers:
            try:
                # Enhanced scrapers don't have the same interface, so we'll mark them as available
                status[scraper.platform_name] = {
                    "status": "enhanced",
                    "type": "stealth",
                    "reliability": "medium"
                }
            except Exception as e:
                status[scraper.platform_name] = {
                    "status": "error",
                    "error": str(e),
                    "type": "enhanced"
                }
        
        # Test regular scrapers
        for scraper in self.regular_scrapers:
            try:
                # Test scraper connectivity
                async with scraper:
                    # Make a simple request to test connectivity
                    test_url = scraper.get_base_url()
                    response = await scraper.make_request(test_url)
                    
                    status[scraper.platform_name] = {
                        "status": "online" if response else "offline",
                        "base_url": test_url,
                        "type": "regular"
                    }
            except Exception as e:
                status[scraper.platform_name] = {
                    "status": "error",
                    "error": str(e),
                    "base_url": scraper.get_base_url(),
                    "type": "regular"
                }
        
        return status
    
    async def test_stealth_capabilities(self) -> Dict[str, Any]:
        """Test the stealth capabilities of enhanced scrapers."""
        results = {}
        
        for scraper in self.enhanced_scrapers:
            try:
                logger.info(f"Testing stealth capabilities for {scraper.platform_name}")
                
                # Test with a simple search
                test_events = await scraper.scrape_events(
                    city="New York",
                    country="United States",
                    radius_km=50
                )
                
                results[scraper.platform_name] = {
                    "status": "success",
                    "events_found": len(test_events),
                    "stealth_level": "high"
                }
                
            except Exception as e:
                results[scraper.platform_name] = {
                    "status": "error",
                    "error": str(e),
                    "stealth_level": "unknown"
                }
        
        return results


# Global enhanced scraper manager instance
enhanced_scraper_manager = EnhancedScraperManager()
