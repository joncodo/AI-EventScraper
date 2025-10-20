"""API-based scraper for official event APIs."""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
import json

from core.models import Event, Location, ContactInfo, EventSource
from core.config import settings

logger = logging.getLogger(__name__)


class APIEventScraper:
    """Scraper for official event APIs."""
    
    def __init__(self):
        self.platform_name = "api_feeds"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # API configurations
        self.api_configs = {
            'eventbrite': {
                'base_url': 'https://www.eventbriteapi.com/v3',
                'endpoint': '/events/search/',
                'api_key': getattr(settings, 'eventbrite_api_key', None),
                'enabled': True
            },
            'meetup': {
                'base_url': 'https://api.meetup.com',
                'endpoint': '/find/upcoming_events',
                'api_key': settings.meetup_api_key if hasattr(settings, 'meetup_api_key') else None,
                'enabled': True
            },
            'google_calendar': {
                'base_url': 'https://www.googleapis.com/calendar/v3',
                'endpoint': '/calendars/{calendar_id}/events',
                'api_key': settings.google_api_key if hasattr(settings, 'google_api_key') else None,
                'enabled': True
            },
            'facebook': {
                'base_url': 'https://graph.facebook.com/v18.0',
                'endpoint': '/search',
                'api_key': settings.facebook_api_key if hasattr(settings, 'facebook_api_key') else None,
                'enabled': True
            }
        }
        
        # Public calendar IDs for Google Calendar
        self.public_calendars = [
            'en.usa#holiday@group.v.calendar.google.com',  # US Holidays
            'en.usa#holiday@group.v.calendar.google.com',  # US Holidays
            'calendar@sfmoma.org',  # SFMOMA
            'events@metmuseum.org',  # Met Museum
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
        """Scrape events from various APIs."""
        events = []
        
        logger.info(f"🔍 API scraper starting for {city}, {country}")
        logger.info(f"📊 Available API configs: {list(self.api_configs.keys())}")
        
        # Check if session is initialized
        if not self.session:
            logger.error("❌ API scraper session not initialized!")
            return events
        
        # Scrape from each API
        for api_name, api_config in self.api_configs.items():
            logger.info(f"🔍 Checking {api_name} API...")
            logger.info(f"📋 API config: enabled={api_config.get('enabled')}, has_key={bool(api_config.get('api_key'))}")
            
            if not api_config.get('enabled', False):
                logger.info(f"⏭️ Skipping {api_name} API - disabled")
                continue
                
            if not api_config.get('api_key'):
                logger.info(f"⏭️ Skipping {api_name} API - not configured")
                continue
            
            try:
                logger.info(f"🚀 Scraping {api_name} API...")
                api_events = await self._scrape_api(
                    api_name, api_config, city, country, radius_km, start_date, end_date
                )
                events.extend(api_events)
                logger.info(f"✅ API {api_name} found {len(api_events)} events")
            except Exception as e:
                logger.error(f"❌ Error scraping {api_name} API: {e}")
                import traceback
                logger.error(f"📋 Traceback: {traceback.format_exc()}")
                continue
        
        logger.info(f"🎯 API scraper found {len(events)} total events")
        return events
    
    async def _scrape_api(
        self, 
        api_name: str, 
        api_config: Dict[str, Any], 
        city: str, 
        country: str, 
        radius_km: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """Scrape events from a specific API."""
        events = []
        
        if api_name == 'eventbrite':
            events = await self._scrape_eventbrite_api(api_config, city, country, radius_km, start_date, end_date)
        elif api_name == 'meetup':
            events = await self._scrape_meetup_api(api_config, city, country, radius_km, start_date, end_date)
        elif api_name == 'google_calendar':
            events = await self._scrape_google_calendar_api(api_config, city, country, start_date, end_date)
        elif api_name == 'facebook':
            events = await self._scrape_facebook_api(api_config, city, country, radius_km, start_date, end_date)
        
        return events
    
    async def _scrape_eventbrite_api(
        self, 
        api_config: Dict[str, Any], 
        city: str, 
        country: str, 
        radius_km: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """Scrape events from Eventbrite API."""
        events = []
        
        try:
            # Build request parameters
            params = {
                'token': api_config['api_key'],
                'q': f"{city} {country}",
                'expand': 'venue,organizer',
                'status': 'live',
                'order_by': 'start_asc'
            }
            
            if start_date:
                params['start_date.range_start'] = start_date.isoformat()
            if end_date:
                params['start_date.range_end'] = end_date.isoformat()
            
            # Try multiple possible endpoints
            endpoints = [
                "https://www.eventbriteapi.com/v3/events/search/",
                "https://www.eventbriteapi.com/v3/events/search",
                "https://www.eventbriteapi.com/v3/events/",
            ]
            
            for url in endpoints:
                try:
                    async with self.session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Parse events
                            for event_data in data.get('events', []):
                                try:
                                    event = self._parse_eventbrite_event(event_data, city, country)
                                    if event:
                                        events.append(event)
                                except Exception as e:
                                    logger.error(f"Error parsing Eventbrite event: {e}")
                                    continue
                            break  # Success, exit the loop
                        elif response.status == 404:
                            logger.warning(f"Eventbrite API endpoint {url} not found (404)")
                            continue  # Try next endpoint
                        else:
                            logger.warning(f"Eventbrite API returned status {response.status} for {url}")
                            continue  # Try next endpoint
                            
                except Exception as e:
                    logger.error(f"Error with Eventbrite API endpoint {url}: {e}")
                    continue  # Try next endpoint
            
            if not events:
                logger.warning("All Eventbrite API endpoints failed - API may have changed")
        
        except Exception as e:
            logger.error(f"Error scraping Eventbrite API: {e}")
        
        return events
    
    async def _scrape_meetup_api(
        self, 
        api_config: Dict[str, Any], 
        city: str, 
        country: str, 
        radius_km: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """Scrape events from Meetup API."""
        events = []
        
        try:
            # Build request parameters
            params = {
                'key': api_config['api_key'],
                'location': f"{city}, {country}",
                'radius': radius_km,
                'status': 'upcoming',
                'order': 'time'
            }
            
            if start_date:
                params['no_earlier_than'] = int(start_date.timestamp() * 1000)
            if end_date:
                params['no_later_than'] = int(end_date.timestamp() * 1000)
            
            # Make API request
            url = api_config['base_url'] + api_config['endpoint']
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.warning(f"Meetup API returned status {response.status}")
                    return events
                
                data = await response.json()
            
            # Parse events
            for event_data in data:
                try:
                    event = self._parse_meetup_event(event_data, city, country)
                    if event:
                        events.append(event)
                except Exception as e:
                    logger.error(f"Error parsing Meetup event: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping Meetup API: {e}")
        
        return events
    
    async def _scrape_google_calendar_api(
        self, 
        api_config: Dict[str, Any], 
        city: str, 
        country: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """Scrape events from Google Calendar API."""
        events = []
        
        try:
            # Use public calendars
            for calendar_id in self.public_calendars:
                try:
                    # Build request parameters
                    params = {
                        'key': api_config['api_key'],
                        'singleEvents': 'true',
                        'orderBy': 'startTime'
                    }
                    
                    if start_date:
                        params['timeMin'] = start_date.isoformat() + 'Z'
                    if end_date:
                        params['timeMax'] = end_date.isoformat() + 'Z'
                    
                    # Make API request
                    url = api_config['base_url'] + api_config['endpoint'].format(calendar_id=calendar_id)
                    async with self.session.get(url, params=params) as response:
                        if response.status != 200:
                            logger.warning(f"Google Calendar API returned status {response.status} for {calendar_id}")
                            continue
                        
                        data = await response.json()
                    
                    # Parse events
                    for event_data in data.get('items', []):
                        try:
                            event = self._parse_google_calendar_event(event_data, city, country)
                            if event:
                                events.append(event)
                        except Exception as e:
                            logger.error(f"Error parsing Google Calendar event: {e}")
                            continue
                
                except Exception as e:
                    logger.error(f"Error scraping Google Calendar {calendar_id}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping Google Calendar API: {e}")
        
        return events
    
    async def _scrape_facebook_api(
        self, 
        api_config: Dict[str, Any], 
        city: str, 
        country: str, 
        radius_km: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """Scrape events from Facebook API."""
        events = []
        
        try:
            # Build request parameters
            params = {
                'access_token': api_config['api_key'],
                'type': 'event',
                'q': f"events in {city}",
                'fields': 'name,description,start_time,end_time,place,attending_count'
            }
            
            # Make API request
            url = api_config['base_url'] + api_config['endpoint']
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.warning(f"Facebook API returned status {response.status}")
                    return events
                
                data = await response.json()
            
            # Parse events
            for event_data in data.get('data', []):
                try:
                    event = self._parse_facebook_event(event_data, city, country)
                    if event:
                        events.append(event)
                except Exception as e:
                    logger.error(f"Error parsing Facebook event: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping Facebook API: {e}")
        
        return events
    
    def _parse_eventbrite_event(self, event_data: Dict[str, Any], city: str, country: str) -> Optional[Event]:
        """Parse Eventbrite API event data."""
        try:
            # Extract basic info
            title = event_data.get('name', {}).get('text', '').strip()
            if not title:
                return None
            
            description = event_data.get('description', {}).get('text', '').strip()
            
            # Extract start date
            start_data = event_data.get('start', {})
            start_date_str = start_data.get('utc', '')
            if not start_date_str:
                return None
            
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            
            # Extract location
            venue_data = event_data.get('venue', {})
            venue_name = venue_data.get('name', '')
            address = venue_data.get('address', {}).get('localized_address_display', f"{city}, {country}")
            
            location = Location(
                address=address,
                city=city,
                country=country,
                venue_name=venue_name
            )
            
            # Extract price
            price_data = event_data.get('ticket_availability', {})
            price = None
            currency = None
            if price_data.get('is_free'):
                price = "Free"
            
            # Create event source
            source = EventSource(
                platform='eventbrite_api',
                url=event_data.get('url', ''),
                scraped_at=datetime.utcnow(),
                source_id=event_data.get('id', '')
            )
            
            # Create event
            event = Event(
                title=title,
                description=description,
                start_date=start_date,
                location=location,
                price=price,
                currency=currency,
                sources=[source]
            )
            
            return event
            
        except Exception as e:
            logger.error(f"Error parsing Eventbrite event: {e}")
            return None
    
    def _parse_meetup_event(self, event_data: Dict[str, Any], city: str, country: str) -> Optional[Event]:
        """Parse Meetup API event data."""
        try:
            # Extract basic info
            title = event_data.get('name', '').strip()
            if not title:
                return None
            
            description = event_data.get('description', '').strip()
            
            # Extract start date
            start_time = event_data.get('time')
            if not start_time:
                return None
            
            start_date = datetime.fromtimestamp(start_time / 1000)
            
            # Extract location
            venue_data = event_data.get('venue', {})
            venue_name = venue_data.get('name', '')
            address = f"{city}, {country}"
            if venue_data.get('address_1'):
                address = f"{venue_data['address_1']}, {city}, {country}"
            
            location = Location(
                address=address,
                city=city,
                country=country,
                venue_name=venue_name
            )
            
            # Extract price
            price = None
            if event_data.get('fee', {}).get('amount'):
                price = str(event_data['fee']['amount'] / 100)  # Convert cents to dollars
                currency = event_data['fee'].get('currency', 'USD')
            else:
                price = "Free"
                currency = None
            
            # Create event source
            source = EventSource(
                platform='meetup_api',
                url=event_data.get('event_url', ''),
                scraped_at=datetime.utcnow(),
                source_id=event_data.get('id', '')
            )
            
            # Create event
            event = Event(
                title=title,
                description=description,
                start_date=start_date,
                location=location,
                price=price,
                currency=currency,
                sources=[source]
            )
            
            return event
            
        except Exception as e:
            logger.error(f"Error parsing Meetup event: {e}")
            return None
    
    def _parse_google_calendar_event(self, event_data: Dict[str, Any], city: str, country: str) -> Optional[Event]:
        """Parse Google Calendar API event data."""
        try:
            # Extract basic info
            title = event_data.get('summary', '').strip()
            if not title:
                return None
            
            description = event_data.get('description', '').strip()
            
            # Extract start date
            start_data = event_data.get('start', {})
            start_date_str = start_data.get('dateTime') or start_data.get('date')
            if not start_date_str:
                return None
            
            if 'T' in start_date_str:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            else:
                start_date = datetime.fromisoformat(start_date_str)
            
            # Extract location
            location_text = event_data.get('location', '')
            venue_name = None
            address = f"{city}, {country}"
            
            if location_text:
                if ',' in location_text:
                    parts = location_text.split(',')
                    venue_name = parts[0].strip()
                    address = ','.join(parts[1:]).strip()
                else:
                    venue_name = location_text
            
            location = Location(
                address=address,
                city=city,
                country=country,
                venue_name=venue_name
            )
            
            # Create event source
            source = EventSource(
                platform='google_calendar_api',
                url=event_data.get('htmlLink', ''),
                scraped_at=datetime.utcnow(),
                source_id=event_data.get('id', '')
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
            logger.error(f"Error parsing Google Calendar event: {e}")
            return None
    
    def _parse_facebook_event(self, event_data: Dict[str, Any], city: str, country: str) -> Optional[Event]:
        """Parse Facebook API event data."""
        try:
            # Extract basic info
            title = event_data.get('name', '').strip()
            if not title:
                return None
            
            description = event_data.get('description', '').strip()
            
            # Extract start date
            start_time = event_data.get('start_time')
            if not start_time:
                return None
            
            start_date = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            
            # Extract location
            place_data = event_data.get('place', {})
            venue_name = place_data.get('name', '')
            address = f"{city}, {country}"
            
            if place_data.get('location'):
                location_data = place_data['location']
                if location_data.get('street'):
                    address = f"{location_data['street']}, {city}, {country}"
            
            location = Location(
                address=address,
                city=city,
                country=country,
                venue_name=venue_name
            )
            
            # Create event source
            source = EventSource(
                platform='facebook_api',
                url=f"https://www.facebook.com/events/{event_data.get('id', '')}",
                scraped_at=datetime.utcnow(),
                source_id=event_data.get('id', '')
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
            logger.error(f"Error parsing Facebook event: {e}")
            return None
