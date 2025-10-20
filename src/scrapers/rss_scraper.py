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
    import atoma
    ATOMA_AVAILABLE = True
    logger.info("✅ atoma imported successfully")
except ImportError as e:
    logger.warning(f"❌ atoma not available - RSS scraping will be disabled: {e}")
    ATOMA_AVAILABLE = False
    atoma = None

try:
    import icalendar
    ICALENDAR_AVAILABLE = True
    logger.info("✅ icalendar imported successfully")
except ImportError as e:
    logger.warning(f"❌ icalendar not available - iCal scraping will be disabled: {e}")
    ICALENDAR_AVAILABLE = False
    icalendar = None

logger.info(f"📊 RSS scraper dependencies: atoma={ATOMA_AVAILABLE}, icalendar={ICALENDAR_AVAILABLE}")


class RSSEventScraper:
    """Scraper for RSS and iCal event feeds."""
    
    def __init__(self):
        self.platform_name = "rss_feeds"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # TEMPORARILY DISABLED - Only use verified working event feeds
        self.event_rss_feeds = [
            # === VERIFIED WORKING EVENT FEEDS ONLY ===
            # Only keeping feeds that we know work and contain real events
            "https://www.eventbrite.com/rss/events/",  # General Eventbrite events
            "https://www.meetup.com/events/rss/",  # General Meetup events
        ]
        
        # iCal feeds (often more reliable than RSS)
        self.ical_feeds = [
            # Empty for now - will add reliable iCal feeds later
        ]
    
    async def __aenter__(self):
        """Async context manager entry."""
        # Headers to mimic a real browser and avoid 403 errors
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=10, limit_per_host=5)
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
        
        logger.info(f"🔍 Starting RSS/iCal scraping for {city}, {country}")
        logger.info(f"📅 Date range: {start_date} to {end_date}")
        logger.info(f"📍 Radius: {radius_km}km")
        logger.info(f"📊 Available feeds: {len(self.event_rss_feeds)} RSS, {len(self.ical_feeds)} iCal")
        
        # Check if dependencies are available
        if not ATOMA_AVAILABLE and not ICALENDAR_AVAILABLE:
            logger.warning("Neither atoma nor icalendar available - RSS scraper disabled")
            return events
        
        # Scrape RSS feeds if available
        if ATOMA_AVAILABLE:
            logger.info(f"🚀 Starting RSS scraping with {len(self.event_rss_feeds)} feeds...")
            rss_events = await self._scrape_rss_feeds(city, country, start_date, end_date)
            events.extend(rss_events)
            logger.info(f"✅ RSS scraping completed: {len(rss_events)} events found")
        else:
            logger.info("RSS scraping disabled - atoma not available")
        
        # Scrape iCal feeds if available
        if ICALENDAR_AVAILABLE:
            logger.info(f"🚀 Starting iCal scraping with {len(self.ical_feeds)} feeds...")
            ical_events = await self._scrape_ical_feeds(city, country, start_date, end_date)
            events.extend(ical_events)
            logger.info(f"✅ iCal scraping completed: {len(ical_events)} events found")
        else:
            logger.info("iCal scraping disabled - icalendar not available")
        
        logger.info(f"🎯 RSS/iCal scraper total: {len(events)} events")
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
        
        if not ATOMA_AVAILABLE:
            logger.warning("atoma not available - RSS scraping disabled")
            return events
        
        logger.info(f"🔍 Processing {len(self.event_rss_feeds)} RSS feeds...")
        successful_feeds = 0
        failed_feeds = 0
        
        for i, feed_url in enumerate(self.event_rss_feeds, 1):
            try:
                logger.info(f"📡 [{i}/{len(self.event_rss_feeds)}] Scraping RSS feed: {feed_url}")
                
                # Add small delay to avoid rate limiting
                await asyncio.sleep(0.5)
                
                # Fetch RSS feed with retry logic
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        async with self.session.get(feed_url) as response:
                            if response.status == 200:
                                content = await response.text()
                                break
                            elif response.status == 403:
                                logger.warning(f"RSS feed {feed_url} returned 403 Forbidden - may be blocking automated requests")
                                continue
                            elif response.status == 404:
                                logger.warning(f"RSS feed {feed_url} returned 404 Not Found - feed may not exist")
                                continue
                            else:
                                logger.warning(f"RSS feed {feed_url} returned status {response.status}")
                                if attempt < max_retries - 1:
                                    await asyncio.sleep(1)  # Wait before retry
                                    continue
                                else:
                                    continue
                    except asyncio.TimeoutError:
                        logger.warning(f"Timeout accessing RSS feed: {feed_url}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(1)
                            continue
                        else:
                            continue
                    except Exception as e:
                        logger.warning(f"Error accessing RSS feed {feed_url}: {e}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(1)
                            continue
                        else:
                            continue
                else:
                    # If we get here, all retries failed
                    continue
                
                # Parse RSS feed with atoma
                try:
                    feed = atoma.parse_rss_bytes(content.encode('utf-8'))
                except Exception as e:
                    logger.error(f"Error parsing RSS feed {feed_url}: {e}")
                    continue
                
                # Process each entry - handle both 'entries' and 'items' attributes
                entries = getattr(feed, 'entries', None) or getattr(feed, 'items', [])
                for entry in entries:
                    try:
                        event = await self._parse_rss_entry(entry, city, country, feed_url)
                        if event and self._is_event_in_date_range(event, start_date, end_date):
                            events.append(event)
                    except Exception as e:
                        logger.error(f"Error parsing RSS entry: {e}")
                        continue
                
                logger.info(f"Found {len([e for e in events if e.sources[0].url == feed_url])} events in {feed_url}")
                successful_feeds += 1
                
            except Exception as e:
                logger.error(f"❌ Error scraping RSS feed {feed_url}: {e}")
                failed_feeds += 1
                continue
        
        logger.info(f"📊 RSS feed processing complete:")
        logger.info(f"   ✅ Successful feeds: {successful_feeds}")
        logger.info(f"   ❌ Failed feeds: {failed_feeds}")
        logger.info(f"   📈 Total events found: {len(events)}")
        
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
        
        logger.info(f"🔍 Processing {len(self.ical_feeds)} iCal feeds...")
        successful_feeds = 0
        failed_feeds = 0
        
        for i, ical_url in enumerate(self.ical_feeds, 1):
            try:
                logger.info(f"📅 [{i}/{len(self.ical_feeds)}] Scraping iCal feed: {ical_url}")
                
                # Add small delay to avoid rate limiting
                await asyncio.sleep(0.5)
                
                # Fetch iCal feed with retry logic
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        async with self.session.get(ical_url) as response:
                            if response.status == 200:
                                content = await response.text()
                                break
                            elif response.status == 403:
                                logger.warning(f"iCal feed {ical_url} returned 403 Forbidden - may be blocking automated requests")
                                continue
                            elif response.status == 404:
                                logger.warning(f"iCal feed {ical_url} returned 404 Not Found - feed may not exist")
                                continue
                            else:
                                logger.warning(f"iCal feed {ical_url} returned status {response.status}")
                                if attempt < max_retries - 1:
                                    await asyncio.sleep(1)  # Wait before retry
                                    continue
                                else:
                                    continue
                    except asyncio.TimeoutError:
                        logger.warning(f"Timeout accessing iCal feed: {ical_url}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(1)
                            continue
                        else:
                            continue
                    except Exception as e:
                        logger.warning(f"Error accessing iCal feed {ical_url}: {e}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(1)
                            continue
                        else:
                            continue
                else:
                    # If we get here, all retries failed
                    continue
                
                # Parse iCal feed with icalendar
                try:
                    calendar = icalendar.Calendar.from_ical(content)
                except Exception as e:
                    logger.error(f"Error parsing iCal feed {ical_url}: {e}")
                    continue
                
                # Process each event
                for component in calendar.walk():
                    if component.name == "VEVENT":
                        try:
                            event = await self._parse_ical_event(component, city, country, ical_url)
                            if event and self._is_event_in_date_range(event, start_date, end_date):
                                events.append(event)
                        except Exception as e:
                            logger.error(f"Error parsing iCal event: {e}")
                            continue
                
                logger.info(f"Found {len([e for e in events if e.sources[0].url == ical_url])} events in {ical_url}")
                successful_feeds += 1
                
            except Exception as e:
                logger.error(f"❌ Error scraping iCal feed {ical_url}: {e}")
                failed_feeds += 1
                continue
        
        logger.info(f"📊 iCal feed processing complete:")
        logger.info(f"   ✅ Successful feeds: {successful_feeds}")
        logger.info(f"   ❌ Failed feeds: {failed_feeds}")
        logger.info(f"   📈 Total events found: {len(events)}")
        
        return events
    
    def _is_likely_event(self, title: str, description: str) -> bool:
        """Check if the content is likely an actual event (not a blog post or news article)."""
        title_lower = title.lower()
        desc_lower = description.lower()
        combined_text = f"{title_lower} {desc_lower}"
        
        # Keywords that indicate this is NOT an event
        non_event_keywords = [
            # Blog/article indicators
            'faq', 'frequently asked questions', 'q&a',
            'vs ', 'comparison', 'review', 'guide', 'tutorial',
            'how to', 'what is', 'everything you need to know',
            'top ', 'best ', 'list of', 'beginner guide',
            'ultimate guide', 'marketing tools', 'ai tools',
            'supplements', 'health', 'wellness', 'blockchain',
            'cryptocurrency', 'nft', 'grammarly', 'prowritingaid',
            'collagen', 'skin care', 'affiliate', 'commission',
            'copy.ai', 'hotpot.ai', 'deep-nostalgia', 'pfpmaker',
            'brandmark', 'lumen5', 'namelix', 'bigjpg',
            
            # News indicators
            'breaking news', 'reports', 'announces', 'launches',
            'acquires', 'merges', 'partnership', 'investment',
            'funding', 'ipo', 'earnings', 'quarterly results',
            
            # Article indicators
            'read more', 'continue reading', 'full article',
            'blog post', 'opinion', 'analysis', 'commentary',
            'techncruncher.blogspot.com', 'blogspot', 'blog',
            
            # Tech article indicators
            'free ai tools', 'ai tools that make', 'tools that make your life',
            'make your life easier', 'free tools', 'ai based'
        ]
        
        # Check for non-event keywords
        for keyword in non_event_keywords:
            if keyword in combined_text:
                return False
        
        # Keywords that indicate this IS an event
        event_keywords = [
            'event', 'meeting', 'conference', 'workshop', 'seminar',
            'meetup', 'networking', 'party', 'celebration', 'festival',
            'convention', 'summit', 'expo', 'exhibition', 'show',
            'concert', 'performance', 'theater', 'movie', 'film',
            'class', 'course', 'training', 'session', 'webinar',
            'tour', 'walk', 'run', 'race', 'competition', 'contest',
            'auction', 'sale', 'market', 'fair', 'carnival',
            'date:', 'time:', 'location:', 'venue:', 'address:',
            'register', 'ticket', 'rsvp', 'attend', 'join us',
            'happening', 'taking place', 'occurring', 'scheduled'
        ]
        
        # Check for event keywords
        for keyword in event_keywords:
            if keyword in combined_text:
                return True
        
        # If it's very long (likely an article), probably not an event
        if len(description) > 1000:
            return False
        
        # If it has a specific date/time pattern, likely an event
        import re
        date_patterns = [
            r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2}',
            r'\b\d{1,2}/\d{1,2}/\d{2,4}',
            r'\b\d{1,2}-\d{1,2}-\d{2,4}',
            r'\b\d{1,2}:\d{2}\s*(am|pm)',
            r'\b\d{1,2}:\d{2}',
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                return True
        
        # Default to False if we can't determine
        return False
    
    async def _parse_rss_entry(self, entry, city: str, country: str, feed_url: str) -> Optional[Event]:
        """Parse an RSS entry into an Event object."""
        try:
            # Extract title
            title = entry.title.strip() if entry.title else ''
            if not title:
                return None
            
            # Extract description
            description = entry.description.strip() if entry.description else ''
            if description:
                # Clean up HTML tags
                import re
                description = re.sub(r'<[^>]+>', '', description)
                description = description.strip()
            
            # Validate this is actually an event (not a blog post or news article)
            if not self._is_likely_event(title, description):
                logger.debug(f"Skipping non-event: {title[:50]}...")
                return None
            
            # Extract link
            link = entry.link.strip() if entry.link else ''
            
            # Extract date
            event_date = None
            if hasattr(entry, 'published') and entry.published:
                try:
                    event_date = entry.published
                except:
                    pass
            
            # If no date found, use current date as fallback
            if event_date is None:
                event_date = datetime.utcnow()
            
            # Extract location from description or title
            location_text = self._extract_location_from_text(f"{title} {description}")
            venue_name = location_text if location_text else "TBD"
            address = f"{city}, {country}"
            
            # Create location object
            location = Location(
                venue_name=venue_name,
                address=address,
                city=city,
                country=country,
                latitude=None,
                longitude=None
            )
            
            # Create event source
            source = EventSource(
                platform="rss",
                url=feed_url,
                event_id=link or title,
                scraped_at=datetime.utcnow()
            )
            
            # Create event
            event = Event(
                title=title,
                description=description,
                start_date=event_date,
                end_date=event_date,  # Assume same day if no end date
                location=location,
                category="General",
                tags=[],
                price=None,
                contact_info=ContactInfo(
                    email=None,
                    phone=None,
                    website=link
                ),
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
            start_date = component.get('dtstart')
            if start_date:
                if hasattr(start_date, 'dt'):
                    start_date = start_date.dt
                if isinstance(start_date, datetime):
                    pass  # Already a datetime
                else:
                    start_date = datetime.combine(start_date, datetime.min.time())
            else:
                start_date = None
            
            # Extract end date
            end_date = component.get('dtend')
            if end_date:
                if hasattr(end_date, 'dt'):
                    end_date = end_date.dt
                if isinstance(end_date, datetime):
                    pass  # Already a datetime
                else:
                    end_date = datetime.combine(end_date, datetime.min.time())
            else:
                end_date = start_date  # Assume same day if no end date
            
            # Extract location
            location_text = str(component.get('location', '')).strip()
            venue_name = location_text if location_text else "TBD"
            address = f"{city}, {country}"
            
            # Create location object
            location = Location(
                venue_name=venue_name,
                address=address,
                city=city,
                country=country,
                latitude=None,
                longitude=None
            )
            
            # Create event source
            source = EventSource(
                platform="ical",
                url=feed_url,
                event_id=str(component.get('uid', title)),
                scraped_at=datetime.utcnow()
            )
            
            # Create event
            event = Event(
                title=title,
                description=description,
                start_date=start_date,
                end_date=end_date,
                location=location,
                category="General",
                tags=[],
                price=None,
                contact_info=ContactInfo(
                    email=None,
                    phone=None,
                    website=None
                ),
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
                    if '/' in pattern:
                        month, day, year = match.groups()
                        return datetime(int(year), int(month), int(day))
                    elif '-' in pattern:
                        year, month, day = match.groups()
                        return datetime(int(year), int(month), int(day))
                    else:
                        month_name, day, year = match.groups()
                        month_num = self._month_name_to_number(month_name)
                        if month_num:
                            return datetime(int(year), month_num, int(day))
                except:
                    continue
        
        return None
    
    def _month_name_to_number(self, month_name: str) -> Optional[int]:
        """Convert month name to number."""
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        return months.get(month_name.lower())
    
    def _extract_location_from_text(self, text: str) -> Optional[str]:
        """Extract location from text."""
        import re
        
        # Common location patterns
        patterns = [
            r'at\s+([^,]+)',
            r'@\s+([^,]+)',
            r'venue:\s*([^,]+)',
            r'location:\s*([^,]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _is_event_in_date_range(
        self, 
        event: Event, 
        start_date: Optional[datetime], 
        end_date: Optional[datetime]
    ) -> bool:
        """Check if event is within the specified date range."""
        if not event.start_date:
            return True  # Include events without dates
        
        # Handle timezone-aware and naive datetimes
        event_start = event.start_date
        if event_start.tzinfo is None:
            # Make naive datetime timezone-aware (assume UTC)
            event_start = event_start.replace(tzinfo=None)
        
        if start_date and end_date:
            # Make sure both dates are timezone-aware or both are naive
            if start_date.tzinfo is None and event_start.tzinfo is not None:
                start_date = start_date.replace(tzinfo=None)
            elif start_date.tzinfo is not None and event_start.tzinfo is None:
                start_date = start_date.replace(tzinfo=None)
            
            if end_date.tzinfo is None and event_start.tzinfo is not None:
                end_date = end_date.replace(tzinfo=None)
            elif end_date.tzinfo is not None and event_start.tzinfo is None:
                end_date = end_date.replace(tzinfo=None)
            
            return start_date <= event_start <= end_date
        
        return True
