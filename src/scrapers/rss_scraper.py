"""RSS and iCal feed scraper for events."""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import feedparser
import icalendar
from urllib.parse import urljoin, urlparse
import aiohttp

from core.models import Event, Location, ContactInfo, EventSource

logger = logging.getLogger(__name__)


class RSSEventScraper:
    """Scraper for RSS and iCal event feeds."""
    
    def __init__(self):
        self.platform_name = "rss_feeds"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Curated list of reliable event RSS feeds
        self.event_rss_feeds = [
            # University event feeds
            "https://events.stanford.edu/rss",
            "https://events.berkeley.edu/rss",
            "https://events.mit.edu/rss",
            "https://events.harvard.edu/rss",
            "https://events.yale.edu/rss",
            
            # City government feeds
            "https://www.sf.gov/rss/events",
            "https://www.nyc.gov/rss/events",
            "https://www.lacity.org/rss/events",
            "https://www.chicago.gov/rss/events",
            
            # Museum and cultural feeds
            "https://www.metmuseum.org/rss/events",
            "https://www.moma.org/rss/events",
            "https://www.sfmoma.org/rss/events",
            "https://www.getty.edu/rss/events",
            
            # Conference and tech event feeds
            "https://conferences.oreilly.com/rss",
            "https://events.linuxfoundation.org/rss",
            "https://www.techcrunch.com/events/rss",
            
            # Local event aggregators
            "https://www.eventbrite.com/rss",
            "https://www.meetup.com/rss",
        ]
        
        # iCal feeds (often more reliable than RSS)
        self.ical_feeds = [
            "https://calendar.google.com/calendar/ical/your-calendar/public/basic.ics",
            "https://events.stanford.edu/calendar.ics",
            "https://events.berkeley.edu/calendar.ics",
        ]
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def scrape_events(
        self, 
        city: str, 
        country: str, 
        radius_km: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """Scrape events from RSS and iCal feeds."""
        events = []
        
        # Scrape RSS feeds
        rss_events = await self._scrape_rss_feeds(city, country, start_date, end_date)
        events.extend(rss_events)
        
        # Scrape iCal feeds
        ical_events = await self._scrape_ical_feeds(city, country, start_date, end_date)
        events.extend(ical_events)
        
        logger.info(f"RSS/iCal scraper found {len(events)} events")
        return events
    
    async def _scrape_rss_feeds(
        self, 
        city: str, 
        country: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """Scrape events from RSS feeds."""
        events = []
        
        for feed_url in self.event_rss_feeds:
            try:
                logger.info(f"Scraping RSS feed: {feed_url}")
                
                # Fetch RSS feed
                async with self.session.get(feed_url) as response:
                    if response.status != 200:
                        logger.warning(f"RSS feed {feed_url} returned status {response.status}")
                        continue
                    
                    content = await response.text()
                
                # Parse RSS feed
                feed = feedparser.parse(content)
                
                if not feed.entries:
                    logger.info(f"No entries found in RSS feed: {feed_url}")
                    continue
                
                # Process each entry
                for entry in feed.entries:
                    try:
                        event = await self._parse_rss_entry(entry, city, country, feed_url)
                        if event and self._is_event_in_date_range(event, start_date, end_date):
                            events.append(event)
                    except Exception as e:
                        logger.error(f"Error parsing RSS entry: {e}")
                        continue
                
                logger.info(f"Found {len([e for e in events if e.sources[0].url == feed_url])} events in {feed_url}")
                
            except Exception as e:
                logger.error(f"Error scraping RSS feed {feed_url}: {e}")
                continue
        
        return events
    
    async def _scrape_ical_feeds(
        self, 
        city: str, 
        country: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """Scrape events from iCal feeds."""
        events = []
        
        for ical_url in self.ical_feeds:
            try:
                logger.info(f"Scraping iCal feed: {ical_url}")
                
                # Fetch iCal feed
                async with self.session.get(ical_url) as response:
                    if response.status != 200:
                        logger.warning(f"iCal feed {ical_url} returned status {response.status}")
                        continue
                    
                    content = await response.text()
                
                # Parse iCal feed
                calendar = icalendar.Calendar.from_ical(content)
                
                # Process each event
                for component in calendar.walk('vevent'):
                    try:
                        event = await self._parse_ical_event(component, city, country, ical_url)
                        if event and self._is_event_in_date_range(event, start_date, end_date):
                            events.append(event)
                    except Exception as e:
                        logger.error(f"Error parsing iCal event: {e}")
                        continue
                
                logger.info(f"Found {len([e for e in events if e.sources[0].url == ical_url])} events in {ical_url}")
                
            except Exception as e:
                logger.error(f"Error scraping iCal feed {ical_url}: {e}")
                continue
        
        return events
    
    async def _parse_rss_entry(self, entry, city: str, country: str, feed_url: str) -> Optional[Event]:
        """Parse an RSS entry into an Event object."""
        try:
            # Extract title
            title = entry.get('title', '').strip()
            if not title:
                return None
            
            # Extract description
            description = entry.get('description', '').strip()
            if description:
                # Clean HTML from description
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(description, 'html.parser')
                description = soup.get_text().strip()
            
            # Extract link
            link = entry.get('link', '')
            if not link:
                return None
            
            # Extract date
            start_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                start_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                start_date = datetime(*entry.updated_parsed[:6])
            
            if not start_date:
                # Try to parse date from title or description
                start_date = self._extract_date_from_text(title + " " + description)
            
            if not start_date:
                return None
            
            # Extract location (try to find city/country in description)
            location_text = self._extract_location_from_text(description + " " + title)
            venue_name = None
            address = f"{city}, {country}"
            
            if location_text:
                if ',' in location_text:
                    parts = location_text.split(',')
                    venue_name = parts[0].strip()
                    address = ','.join(parts[1:]).strip()
                else:
                    venue_name = location_text
            
            # Create location
            location = Location(
                address=address,
                city=city,
                country=country,
                venue_name=venue_name
            )
            
            # Create event source
            source = EventSource(
                platform=self.platform_name,
                url=link,
                scraped_at=datetime.utcnow(),
                source_id=entry.get('id', link)
            )
            
            # Create event
            event = Event(
                title=title,
                description=description,
                start_date=start_date,
                location=location,
                sources=[source]
            )
            
            return event
            
        except Exception as e:
            logger.error(f"Error parsing RSS entry: {e}")
            return None
    
    async def _parse_ical_event(self, component, city: str, country: str, feed_url: str) -> Optional[Event]:
        """Parse an iCal event component into an Event object."""
        try:
            # Extract title
            title = str(component.get('summary', '')).strip()
            if not title:
                return None
            
            # Extract description
            description = str(component.get('description', '')).strip()
            
            # Extract start date
            start_date = None
            if component.get('dtstart'):
                dt_start = component.get('dtstart').dt
                if isinstance(dt_start, datetime):
                    start_date = dt_start
                else:
                    # All-day event
                    start_date = datetime.combine(dt_start, datetime.min.time())
            
            if not start_date:
                return None
            
            # Extract location
            location_text = str(component.get('location', '')).strip()
            venue_name = None
            address = f"{city}, {country}"
            
            if location_text:
                if ',' in location_text:
                    parts = location_text.split(',')
                    venue_name = parts[0].strip()
                    address = ','.join(parts[1:]).strip()
                else:
                    venue_name = location_text
            
            # Create location
            location = Location(
                address=address,
                city=city,
                country=country,
                venue_name=venue_name
            )
            
            # Create event source
            source = EventSource(
                platform=self.platform_name,
                url=feed_url,
                scraped_at=datetime.utcnow(),
                source_id=str(component.get('uid', ''))
            )
            
            # Create event
            event = Event(
                title=title,
                description=description,
                start_date=start_date,
                location=location,
                sources=[source]
            )
            
            return event
            
        except Exception as e:
            logger.error(f"Error parsing iCal event: {e}")
            return None
    
    def _extract_date_from_text(self, text: str) -> Optional[datetime]:
        """Extract date from text using common patterns."""
        import re
        
        # Common date patterns
        patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',  # Month DD, YYYY
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if '/' in match.group(0):
                        month, day, year = match.groups()
                        return datetime(int(year), int(month), int(day))
                    elif '-' in match.group(0):
                        year, month, day = match.groups()
                        return datetime(int(year), int(month), int(day))
                    else:
                        # Month name format
                        month_name, day, year = match.groups()
                        month_num = self._month_name_to_number(month_name)
                        if month_num:
                            return datetime(int(year), month_num, int(day))
                except ValueError:
                    continue
        
        return None
    
    def _month_name_to_number(self, month_name: str) -> Optional[int]:
        """Convert month name to number."""
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        return months.get(month_name.lower())
    
    def _extract_location_from_text(self, text: str) -> Optional[str]:
        """Extract location information from text."""
        import re
        
        # Look for venue patterns
        venue_patterns = [
            r'at\s+([^,]+)',
            r'@\s+([^,]+)',
            r'venue:\s*([^,]+)',
            r'location:\s*([^,]+)',
        ]
        
        for pattern in venue_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                venue = match.group(1).strip()
                if len(venue) > 3 and len(venue) < 100:  # Reasonable venue name length
                    return venue
        
        return None
    
    def _is_event_in_date_range(
        self, 
        event: Event, 
        start_date: Optional[datetime], 
        end_date: Optional[datetime]
    ) -> bool:
        """Check if event is within the specified date range."""
        if not start_date and not end_date:
            return True
        
        event_date = event.start_date
        
        if start_date and event_date < start_date:
            return False
        
        if end_date and event_date > end_date:
            return False
        
        return True
