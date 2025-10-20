"""RSS and iCal feed scraper for events."""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import aiohttp

from core.models import Event, Location, ContactInfo, EventSource

logger = logging.getLogger(__name__)

# Import required dependencies with guaranteed installation
logger.info("🔍 Checking RSS scraper dependencies...")

# Ensure dependencies are installed
try:
    from utils.dependency_installer import ensure_dependencies
    deps_available = ensure_dependencies()
    logger.info(f"📊 Dependency installer result: {deps_available}")
except Exception as e:
    logger.error(f"❌ Dependency installer failed: {e}")
    deps_available = False

# Now try to import
try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
    logger.info("✅ feedparser imported successfully")
except ImportError as e:
    logger.warning(f"❌ feedparser not available - RSS scraping will be disabled: {e}")
    FEEDPARSER_AVAILABLE = False
    feedparser = None

try:
    import icalendar
    ICALENDAR_AVAILABLE = True
    logger.info("✅ icalendar imported successfully")
except ImportError as e:
    logger.warning(f"❌ icalendar not available - iCal scraping will be disabled: {e}")
    ICALENDAR_AVAILABLE = False
    icalendar = None

logger.info(f"📊 RSS scraper dependencies: feedparser={FEEDPARSER_AVAILABLE}, icalendar={ICALENDAR_AVAILABLE}")


class RSSEventScraper:
    """Scraper for RSS and iCal event feeds."""
    
    def __init__(self):
        self.platform_name = "rss_feeds"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Comprehensive curated list of reliable event RSS feeds
        self.event_rss_feeds = [
            # === WORKING PUBLIC RSS FEEDS ===
            # BBC News (for testing)
            "http://feeds.bbci.co.uk/news/rss.xml",
            "https://rss.cnn.com/rss/edition.rss",
            
            # Tech News (for testing)
            "https://feeds.feedburner.com/oreilly/radar",
            "https://feeds.feedburner.com/venturebeat/SZYF",
            
            # === MAJOR UNIVERSITIES ===
            # Stanford University
            "https://events.stanford.edu/rss",
            "https://events.stanford.edu/calendar.ics",
            
            # UC Berkeley
            "https://events.berkeley.edu/rss",
            "https://events.berkeley.edu/calendar.ics",
            
            # MIT
            "https://events.mit.edu/rss",
            "https://events.mit.edu/calendar.ics",
            
            # Harvard University
            "https://events.harvard.edu/rss",
            "https://events.harvard.edu/calendar.ics",
            
            # Yale University
            "https://events.yale.edu/rss",
            "https://events.yale.edu/calendar.ics",
            
            # Princeton University
            "https://events.princeton.edu/rss",
            "https://events.princeton.edu/calendar.ics",
            
            # Columbia University
            "https://events.columbia.edu/rss",
            "https://events.columbia.edu/calendar.ics",
            
            # University of Chicago
            "https://events.uchicago.edu/rss",
            "https://events.uchicago.edu/calendar.ics",
            
            # UCLA
            "https://events.ucla.edu/rss",
            "https://events.ucla.edu/calendar.ics",
            
            # University of Washington
            "https://events.washington.edu/rss",
            "https://events.washington.edu/calendar.ics",
            
            # === MAJOR CITIES ===
            # San Francisco
            "https://www.sf.gov/rss/events",
            "https://sf.gov/api/events/feed",
            "https://www.sf.gov/events/feed",
            
            # New York City
            "https://www.nyc.gov/rss/events",
            "https://www1.nyc.gov/api/events/feed",
            "https://www1.nyc.gov/events/feed",
            
            # Chicago
            "https://www.chicago.gov/rss/events",
            "https://www.chicago.gov/api/events/feed",
            "https://www.chicago.gov/events/feed",
            
            # Los Angeles
            "https://www.lacity.org/rss/events",
            "https://www.lacity.org/api/events/feed",
            "https://www.lacity.org/events/feed",
            
            # Boston
            "https://www.boston.gov/rss/events",
            "https://www.boston.gov/api/events/feed",
            "https://www.boston.gov/events/feed",
            
            # Seattle
            "https://www.seattle.gov/rss/events",
            "https://www.seattle.gov/api/events/feed",
            "https://www.seattle.gov/events/feed",
            
            # Austin
            "https://www.austintexas.gov/rss/events",
            "https://www.austintexas.gov/api/events/feed",
            "https://www.austintexas.gov/events/feed",
            
            # Denver
            "https://www.denvergov.org/rss/events",
            "https://www.denvergov.org/api/events/feed",
            "https://www.denvergov.org/events/feed",
            
            # Portland
            "https://www.portlandoregon.gov/rss/events",
            "https://www.portlandoregon.gov/api/events/feed",
            "https://www.portlandoregon.gov/events/feed",
            
            # === MAJOR MUSEUMS & CULTURAL INSTITUTIONS ===
            # Metropolitan Museum of Art
            "https://www.metmuseum.org/rss/events",
            "https://www.metmuseum.org/api/events/feed",
            "https://www.metmuseum.org/events/feed",
            
            # Museum of Modern Art (MoMA)
            "https://www.moma.org/rss/events",
            "https://www.moma.org/api/events/feed",
            "https://www.moma.org/events/feed",
            
            # SFMOMA
            "https://www.sfmoma.org/rss/events",
            "https://www.sfmoma.org/api/events/feed",
            "https://www.sfmoma.org/events/feed",
            
            # Getty Museum
            "https://www.getty.edu/rss/events",
            "https://www.getty.edu/api/events/feed",
            "https://www.getty.edu/events/feed",
            
            # Smithsonian Institution
            "https://www.si.edu/rss/events",
            "https://www.si.edu/api/events/feed",
            "https://www.si.edu/events/feed",
            
            # Guggenheim Museum
            "https://www.guggenheim.org/rss/events",
            "https://www.guggenheim.org/api/events/feed",
            "https://www.guggenheim.org/events/feed",
            
            # Whitney Museum
            "https://whitney.org/rss/events",
            "https://whitney.org/api/events/feed",
            "https://whitney.org/events/feed",
            
            # Art Institute of Chicago
            "https://www.artic.edu/rss/events",
            "https://www.artic.edu/api/events/feed",
            "https://www.artic.edu/events/feed",
            
            # Los Angeles County Museum of Art
            "https://www.lacma.org/rss/events",
            "https://www.lacma.org/api/events/feed",
            "https://www.lacma.org/events/feed",
            
            # === PERFORMING ARTS CENTERS ===
            # Lincoln Center
            "https://www.lincolncenter.org/rss/events",
            "https://www.lincolncenter.org/api/events/feed",
            "https://www.lincolncenter.org/events/feed",
            
            # Kennedy Center
            "https://www.kennedy-center.org/rss/events",
            "https://www.kennedy-center.org/api/events/feed",
            "https://www.kennedy-center.org/events/feed",
            
            # Carnegie Hall
            "https://www.carnegiehall.org/rss/events",
            "https://www.carnegiehall.org/api/events/feed",
            "https://www.carnegiehall.org/events/feed",
            
            # San Francisco Symphony
            "https://www.sfsymphony.org/rss/events",
            "https://www.sfsymphony.org/api/events/feed",
            "https://www.sfsymphony.org/events/feed",
            
            # === CONFERENCE & TECH EVENTS ===
            # O'Reilly Conferences
            "https://conferences.oreilly.com/rss",
            "https://conferences.oreilly.com/events/feed",
            
            # Linux Foundation Events
            "https://events.linuxfoundation.org/rss",
            "https://events.linuxfoundation.org/events/feed",
            
            # TechCrunch Events
            "https://www.techcrunch.com/events/rss",
            "https://www.techcrunch.com/events/feed",
            
            # Google I/O
            "https://events.google.com/io/rss",
            "https://events.google.com/io/events/feed",
            
            # Microsoft Build
            "https://events.microsoft.com/build/rss",
            "https://events.microsoft.com/build/events/feed",
            
            # Apple WWDC
            "https://developer.apple.com/wwdc/rss",
            "https://developer.apple.com/wwdc/events/feed",
            
            # === LOCAL EVENT AGGREGATORS ===
            # Eventbrite (official RSS)
            "https://www.eventbrite.com/rss",
            "https://www.eventbrite.com/events/feed",
            
            # Meetup (official RSS)
            "https://www.meetup.com/rss",
            "https://www.meetup.com/events/feed",
            
            # CitySpark (major aggregator)
            "https://www.cityspark.com/eventlistings/feed",
            "https://www.cityspark.com/events/feed",
            
            # Eventful
            "https://eventful.com/events/feed",
            "https://eventful.com/rss",
            
            # Zvents
            "https://www.zvents.com/events/feed",
            "https://www.zvents.com/rss",
            
            # === LOCAL NEWS & CULTURE ===
            # New York Magazine (Vulture)
            "https://www.vulture.com/rss",
            "https://www.vulture.com/events/feed",
            
            # Village Voice
            "https://www.villagevoice.com/rss",
            "https://www.villagevoice.com/events/feed",
            
            # Time Out (major cities)
            "https://www.timeout.com/newyork/rss",
            "https://www.timeout.com/san-francisco/rss",
            "https://www.timeout.com/chicago/rss",
            "https://www.timeout.com/los-angeles/rss",
            "https://www.timeout.com/boston/rss",
            "https://www.timeout.com/seattle/rss",
            
            # Thrillist (events and activities)
            "https://www.thrillist.com/rss",
            "https://www.thrillist.com/events/feed",
            
            # === SPECIALIZED EVENT SOURCES ===
            # Event Marketer
            "https://www.eventmarketer.com/rss",
            "https://www.eventmarketer.com/events/feed",
            
            # BizBash
            "https://www.bizbash.com/rss",
            "https://www.bizbash.com/events/feed",
            
            # Smart Meetings
            "https://www.smartmeetings.com/rss",
            "https://www.smartmeetings.com/events/feed",
            
            # === FESTIVAL & OUTDOOR EVENTS ===
            # FestivalNet
            "https://www.festivalnet.com/rss",
            "https://www.festivalnet.com/events/feed",
            
            # Eventful Festivals
            "https://eventful.com/festivals/feed",
            "https://eventful.com/outdoor-events/feed",
        ]
        
        # iCal feeds (often more reliable than RSS)
        self.ical_feeds = [
            # === MAJOR UNIVERSITIES (iCal) ===
            "https://events.stanford.edu/calendar.ics",
            "https://events.berkeley.edu/calendar.ics",
            "https://events.mit.edu/calendar.ics",
            "https://events.harvard.edu/calendar.ics",
            "https://events.yale.edu/calendar.ics",
            "https://events.princeton.edu/calendar.ics",
            "https://events.columbia.edu/calendar.ics",
            "https://events.uchicago.edu/calendar.ics",
            "https://events.ucla.edu/calendar.ics",
            "https://events.washington.edu/calendar.ics",
            
            # === MAJOR CITIES (iCal) ===
            "https://www.sf.gov/events/calendar.ics",
            "https://www.nyc.gov/events/calendar.ics",
            "https://www.chicago.gov/events/calendar.ics",
            "https://www.lacity.org/events/calendar.ics",
            "https://www.boston.gov/events/calendar.ics",
            "https://www.seattle.gov/events/calendar.ics",
            "https://www.austintexas.gov/events/calendar.ics",
            "https://www.denvergov.org/events/calendar.ics",
            "https://www.portlandoregon.gov/events/calendar.ics",
            
            # === MUSEUMS & CULTURAL (iCal) ===
            "https://www.metmuseum.org/events/calendar.ics",
            "https://www.moma.org/events/calendar.ics",
            "https://www.sfmoma.org/events/calendar.ics",
            "https://www.getty.edu/events/calendar.ics",
            "https://www.si.edu/events/calendar.ics",
            "https://www.guggenheim.org/events/calendar.ics",
            "https://whitney.org/events/calendar.ics",
            "https://www.artic.edu/events/calendar.ics",
            "https://www.lacma.org/events/calendar.ics",
            
            # === PERFORMING ARTS (iCal) ===
            "https://www.lincolncenter.org/events/calendar.ics",
            "https://www.kennedy-center.org/events/calendar.ics",
            "https://www.carnegiehall.org/events/calendar.ics",
            "https://www.sfsymphony.org/events/calendar.ics",
            
            # === PUBLIC CALENDARS ===
            "https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics",  # US Holidays
            "https://calendar.google.com/calendar/ical/calendar%40sfmoma.org/public/basic.ics",  # SFMOMA
            "https://calendar.google.com/calendar/ical/events%40metmuseum.org/public/basic.ics",  # Met Museum
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
        
        # Check if dependencies are available
        if not FEEDPARSER_AVAILABLE and not ICALENDAR_AVAILABLE:
            logger.warning("Neither feedparser nor icalendar available - RSS scraper disabled")
            return events
        
        # Scrape RSS feeds if available
        if FEEDPARSER_AVAILABLE:
            rss_events = await self._scrape_rss_feeds(city, country, start_date, end_date)
            events.extend(rss_events)
        else:
            logger.info("RSS scraping disabled - feedparser not available")
        
        # Scrape iCal feeds if available
        if ICALENDAR_AVAILABLE:
            ical_events = await self._scrape_ical_feeds(city, country, start_date, end_date)
            events.extend(ical_events)
        else:
            logger.info("iCal scraping disabled - icalendar not available")
        
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
        
        if not FEEDPARSER_AVAILABLE:
            logger.warning("feedparser not available - RSS scraping disabled")
            return events
        
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
        
        if not ICALENDAR_AVAILABLE:
            logger.warning("icalendar not available - iCal scraping disabled")
            return events
        
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
