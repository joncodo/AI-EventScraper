"""Local events scraper for city and university APIs."""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
import json

from core.models import Event, Location, ContactInfo, EventSource

logger = logging.getLogger(__name__)


class LocalEventsScraper:
    """Scraper for local government and university event APIs."""
    
    def __init__(self):
        self.platform_name = "local_events"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Comprehensive city and university event APIs
        self.local_apis = {
            # === MAJOR US CITIES (Socrata Open Data) ===
            'sf_events': {
                'name': 'San Francisco Events',
                'url': 'https://data.sfgov.org/resource/event-data.json',
                'type': 'socrata',
                'enabled': True
            },
            'nyc_events': {
                'name': 'NYC Events',
                'url': 'https://data.cityofnewyork.us/resource/event-data.json',
                'type': 'socrata',
                'enabled': True
            },
            'chicago_events': {
                'name': 'Chicago Events',
                'url': 'https://data.cityofchicago.org/resource/event-data.json',
                'type': 'socrata',
                'enabled': True
            },
            'la_events': {
                'name': 'Los Angeles Events',
                'url': 'https://data.lacity.org/resource/event-data.json',
                'type': 'socrata',
                'enabled': True
            },
            'boston_events': {
                'name': 'Boston Events',
                'url': 'https://data.boston.gov/resource/event-data.json',
                'type': 'socrata',
                'enabled': True
            },
            'seattle_events': {
                'name': 'Seattle Events',
                'url': 'https://data.seattle.gov/resource/event-data.json',
                'type': 'socrata',
                'enabled': True
            },
            'austin_events': {
                'name': 'Austin Events',
                'url': 'https://data.austintexas.gov/resource/event-data.json',
                'type': 'socrata',
                'enabled': True
            },
            'denver_events': {
                'name': 'Denver Events',
                'url': 'https://data.denvergov.org/resource/event-data.json',
                'type': 'socrata',
                'enabled': True
            },
            'portland_events': {
                'name': 'Portland Events',
                'url': 'https://data.portlandoregon.gov/resource/event-data.json',
                'type': 'socrata',
                'enabled': True
            },
            'philadelphia_events': {
                'name': 'Philadelphia Events',
                'url': 'https://data.phila.gov/resource/event-data.json',
                'type': 'socrata',
                'enabled': True
            },
            'dallas_events': {
                'name': 'Dallas Events',
                'url': 'https://data.dallasopendata.com/resource/event-data.json',
                'type': 'socrata',
                'enabled': True
            },
            'houston_events': {
                'name': 'Houston Events',
                'url': 'https://data.houstontx.gov/resource/event-data.json',
                'type': 'socrata',
                'enabled': True
            },
            'miami_events': {
                'name': 'Miami Events',
                'url': 'https://data.miamidade.gov/resource/event-data.json',
                'type': 'socrata',
                'enabled': True
            },
            'atlanta_events': {
                'name': 'Atlanta Events',
                'url': 'https://data.atlantaga.gov/resource/event-data.json',
                'type': 'socrata',
                'enabled': True
            },
            'phoenix_events': {
                'name': 'Phoenix Events',
                'url': 'https://data.phoenix.gov/resource/event-data.json',
                'type': 'socrata',
                'enabled': True
            },
            
            # === MAJOR UNIVERSITIES ===
            'stanford_events': {
                'name': 'Stanford Events',
                'url': 'https://events.stanford.edu/api/events',
                'type': 'json',
                'enabled': True
            },
            'berkeley_events': {
                'name': 'UC Berkeley Events',
                'url': 'https://events.berkeley.edu/api/events',
                'type': 'json',
                'enabled': True
            },
            'mit_events': {
                'name': 'MIT Events',
                'url': 'https://events.mit.edu/api/events',
                'type': 'json',
                'enabled': True
            },
            'harvard_events': {
                'name': 'Harvard Events',
                'url': 'https://events.harvard.edu/api/events',
                'type': 'json',
                'enabled': True
            },
            'yale_events': {
                'name': 'Yale Events',
                'url': 'https://events.yale.edu/api/events',
                'type': 'json',
                'enabled': True
            },
            'princeton_events': {
                'name': 'Princeton Events',
                'url': 'https://events.princeton.edu/api/events',
                'type': 'json',
                'enabled': True
            },
            'columbia_events': {
                'name': 'Columbia Events',
                'url': 'https://events.columbia.edu/api/events',
                'type': 'json',
                'enabled': True
            },
            'uchicago_events': {
                'name': 'University of Chicago Events',
                'url': 'https://events.uchicago.edu/api/events',
                'type': 'json',
                'enabled': True
            },
            'ucla_events': {
                'name': 'UCLA Events',
                'url': 'https://events.ucla.edu/api/events',
                'type': 'json',
                'enabled': True
            },
            'uw_events': {
                'name': 'University of Washington Events',
                'url': 'https://events.washington.edu/api/events',
                'type': 'json',
                'enabled': True
            },
            'nyu_events': {
                'name': 'NYU Events',
                'url': 'https://events.nyu.edu/api/events',
                'type': 'json',
                'enabled': True
            },
            'usc_events': {
                'name': 'USC Events',
                'url': 'https://events.usc.edu/api/events',
                'type': 'json',
                'enabled': True
            },
            
            # === MAJOR MUSEUMS & CULTURAL INSTITUTIONS ===
            'met_events': {
                'name': 'Metropolitan Museum Events',
                'url': 'https://www.metmuseum.org/api/events',
                'type': 'json',
                'enabled': True
            },
            'moma_events': {
                'name': 'MoMA Events',
                'url': 'https://www.moma.org/api/events',
                'type': 'json',
                'enabled': True
            },
            'sfmoma_events': {
                'name': 'SFMOMA Events',
                'url': 'https://www.sfmoma.org/api/events',
                'type': 'json',
                'enabled': True
            },
            'getty_events': {
                'name': 'Getty Museum Events',
                'url': 'https://www.getty.edu/api/events',
                'type': 'json',
                'enabled': True
            },
            'smithsonian_events': {
                'name': 'Smithsonian Events',
                'url': 'https://www.si.edu/api/events',
                'type': 'json',
                'enabled': True
            },
            'guggenheim_events': {
                'name': 'Guggenheim Events',
                'url': 'https://www.guggenheim.org/api/events',
                'type': 'json',
                'enabled': True
            },
            'whitney_events': {
                'name': 'Whitney Museum Events',
                'url': 'https://whitney.org/api/events',
                'type': 'json',
                'enabled': True
            },
            'artic_events': {
                'name': 'Art Institute of Chicago Events',
                'url': 'https://www.artic.edu/api/events',
                'type': 'json',
                'enabled': True
            },
            'lacma_events': {
                'name': 'LACMA Events',
                'url': 'https://www.lacma.org/api/events',
                'type': 'json',
                'enabled': True
            },
            
            # === PERFORMING ARTS CENTERS ===
            'lincoln_center_events': {
                'name': 'Lincoln Center Events',
                'url': 'https://www.lincolncenter.org/api/events',
                'type': 'json',
                'enabled': True
            },
            'kennedy_center_events': {
                'name': 'Kennedy Center Events',
                'url': 'https://www.kennedy-center.org/api/events',
                'type': 'json',
                'enabled': True
            },
            'carnegie_hall_events': {
                'name': 'Carnegie Hall Events',
                'url': 'https://www.carnegiehall.org/api/events',
                'type': 'json',
                'enabled': True
            },
            'sfsymphony_events': {
                'name': 'San Francisco Symphony Events',
                'url': 'https://www.sfsymphony.org/api/events',
                'type': 'json',
                'enabled': True
            },
            'bso_events': {
                'name': 'Boston Symphony Orchestra Events',
                'url': 'https://www.bso.org/api/events',
                'type': 'json',
                'enabled': True
            },
            'nyphil_events': {
                'name': 'New York Philharmonic Events',
                'url': 'https://nyphil.org/api/events',
                'type': 'json',
                'enabled': True
            },
        }
        
        # Alternative endpoints for when primary APIs fail
        self.fallback_endpoints = {
            'sf_events': [
                'https://sf.gov/api/events',
                'https://www.sf.gov/events/feed',
                'https://data.sfgov.org/resource/events.json',
            ],
            'nyc_events': [
                'https://www1.nyc.gov/api/events',
                'https://www1.nyc.gov/events/feed',
                'https://data.cityofnewyork.us/resource/events.json',
            ],
            'chicago_events': [
                'https://www.chicago.gov/api/events',
                'https://www.chicago.gov/events/feed',
                'https://data.cityofchicago.org/resource/events.json',
            ],
            'la_events': [
                'https://www.lacity.org/api/events',
                'https://www.lacity.org/events/feed',
                'https://data.lacity.org/resource/events.json',
            ],
            'boston_events': [
                'https://www.boston.gov/api/events',
                'https://www.boston.gov/events/feed',
                'https://data.boston.gov/resource/events.json',
            ],
            'seattle_events': [
                'https://www.seattle.gov/api/events',
                'https://www.seattle.gov/events/feed',
                'https://data.seattle.gov/resource/events.json',
            ],
            'austin_events': [
                'https://www.austintexas.gov/api/events',
                'https://www.austintexas.gov/events/feed',
                'https://data.austintexas.gov/resource/events.json',
            ],
            'denver_events': [
                'https://www.denvergov.org/api/events',
                'https://www.denvergov.org/events/feed',
                'https://data.denvergov.org/resource/events.json',
            ],
            'portland_events': [
                'https://www.portlandoregon.gov/api/events',
                'https://www.portlandoregon.gov/events/feed',
                'https://data.portlandoregon.gov/resource/events.json',
            ],
            'philadelphia_events': [
                'https://www.phila.gov/api/events',
                'https://www.phila.gov/events/feed',
                'https://data.phila.gov/resource/events.json',
            ],
            'dallas_events': [
                'https://www.dallas.gov/api/events',
                'https://www.dallas.gov/events/feed',
                'https://data.dallasopendata.com/resource/events.json',
            ],
            'houston_events': [
                'https://www.houstontx.gov/api/events',
                'https://www.houstontx.gov/events/feed',
                'https://data.houstontx.gov/resource/events.json',
            ],
            'miami_events': [
                'https://www.miamidade.gov/api/events',
                'https://www.miamidade.gov/events/feed',
                'https://data.miamidade.gov/resource/events.json',
            ],
            'atlanta_events': [
                'https://www.atlantaga.gov/api/events',
                'https://www.atlantaga.gov/events/feed',
                'https://data.atlantaga.gov/resource/events.json',
            ],
            'phoenix_events': [
                'https://www.phoenix.gov/api/events',
                'https://www.phoenix.gov/events/feed',
                'https://data.phoenix.gov/resource/events.json',
            ],
        }
    
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
        """Scrape events from local APIs."""
        events = []
        
        logger.info(f"🏛️ Local events scraper starting for {city}, {country}")
        
        # Check if session is initialized
        if not self.session:
            logger.error("❌ Local events scraper session not initialized!")
            return events
        
        # Filter APIs based on city
        relevant_apis = self._get_relevant_apis(city, country)
        logger.info(f"📊 Found {len(relevant_apis)} relevant APIs for {city}")
        
        for api_key, api_config in relevant_apis.items():
            if not api_config['enabled']:
                logger.info(f"⏭️ Skipping {api_config['name']} - disabled")
                continue
            
            try:
                logger.info(f"🔍 Scraping {api_config['name']}: {api_config.get('url', 'unknown')}")
                api_events = await self._scrape_local_api(
                    api_key, api_config, city, country, start_date, end_date
                )
                events.extend(api_events)
                logger.info(f"✅ Local API {api_config['name']} found {len(api_events)} events")
            except Exception as e:
                logger.error(f"❌ Error scraping {api_config['name']}: {e}")
                import traceback
                logger.error(f"📋 Traceback: {traceback.format_exc()}")
                continue
        
        logger.info(f"🎯 Local events scraper found {len(events)} total events")
        return events
    
    def _get_relevant_apis(self, city: str, country: str) -> Dict[str, Dict[str, Any]]:
        """Get APIs relevant to the specified city/country."""
        relevant = {}
        
        city_lower = city.lower()
        country_lower = country.lower()
        
        # Map cities to their APIs
        city_api_mapping = {
            'san francisco': ['sf_events', 'stanford_events', 'sfmoma_events', 'sfsymphony_events'],
            'new york': ['nyc_events', 'met_events', 'moma_events', 'guggenheim_events', 'whitney_events', 'lincoln_center_events', 'carnegie_hall_events', 'nyphil_events', 'columbia_events', 'nyu_events'],
            'chicago': ['chicago_events', 'uchicago_events', 'artic_events'],
            'los angeles': ['la_events', 'ucla_events', 'usc_events', 'getty_events', 'lacma_events'],
            'boston': ['boston_events', 'mit_events', 'harvard_events', 'bso_events'],
            'berkeley': ['berkeley_events'],
            'seattle': ['seattle_events', 'uw_events'],
            'austin': ['austin_events'],
            'denver': ['denver_events'],
            'portland': ['portland_events'],
            'philadelphia': ['philadelphia_events'],
            'dallas': ['dallas_events'],
            'houston': ['houston_events'],
            'miami': ['miami_events'],
            'atlanta': ['atlanta_events'],
            'phoenix': ['phoenix_events'],
            'washington': ['kennedy_center_events', 'smithsonian_events'],
            'dc': ['kennedy_center_events', 'smithsonian_events'],
            'washington dc': ['kennedy_center_events', 'smithsonian_events'],
        }
        
        # Add city-specific APIs
        if city_lower in city_api_mapping:
            for api_key in city_api_mapping[city_lower]:
                if api_key in self.local_apis:
                    relevant[api_key] = self.local_apis[api_key]
        
        # Add university APIs for major cities
        if any(uni in city_lower for uni in ['university', 'college', 'campus']):
            relevant.update({
                k: v for k, v in self.local_apis.items() 
                if 'events' in k and 'university' in v['name'].lower()
            })
        
        # Add museum APIs for major cities
        if city_lower in ['new york', 'san francisco', 'chicago', 'los angeles']:
            relevant.update({
                k: v for k, v in self.local_apis.items() 
                if 'museum' in v['name'].lower() or 'met' in v['name'].lower()
            })
        
        return relevant
    
    async def _scrape_local_api(
        self, 
        api_key: str, 
        api_config: Dict[str, Any], 
        city: str, 
        country: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """Scrape events from a local API."""
        events = []
        
        # Try primary endpoint
        try:
            events = await self._scrape_api_endpoint(
                api_config['url'], api_config['type'], city, country, start_date, end_date
            )
        except Exception as e:
            logger.warning(f"Primary endpoint failed for {api_config['name']}: {e}")
            
            # Try fallback endpoints
            if api_key in self.fallback_endpoints:
                for fallback_url in self.fallback_endpoints[api_key]:
                    try:
                        events = await self._scrape_api_endpoint(
                            fallback_url, 'json', city, country, start_date, end_date
                        )
                        if events:
                            break
                    except Exception as fallback_e:
                        logger.warning(f"Fallback endpoint {fallback_url} failed: {fallback_e}")
                        continue
        
        return events
    
    async def _scrape_api_endpoint(
        self, 
        url: str, 
        api_type: str, 
        city: str, 
        country: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """Scrape events from a specific API endpoint."""
        events = []
        
        try:
            # Build request parameters
            params = {}
            if start_date:
                params['start_date'] = start_date.isoformat()
            if end_date:
                params['end_date'] = end_date.isoformat()
            
            # Add location filter if supported
            if api_type == 'socrata':
                params['$where'] = f"city='{city}'"
            
            # Make API request
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.warning(f"API endpoint {url} returned status {response.status}")
                    return events
                
                if api_type == 'socrata':
                    data = await response.json()
                else:
                    data = await response.json()
            
            # Parse events based on API type
            if api_type == 'socrata':
                events = self._parse_socrata_events(data, city, country)
            else:
                events = self._parse_json_events(data, city, country)
        
        except Exception as e:
            logger.error(f"Error scraping API endpoint {url}: {e}")
        
        return events
    
    def _parse_socrata_events(self, data: List[Dict[str, Any]], city: str, country: str) -> List[Event]:
        """Parse events from Socrata-based APIs."""
        events = []
        
        for event_data in data:
            try:
                event = self._parse_socrata_event(event_data, city, country)
                if event:
                    events.append(event)
            except Exception as e:
                logger.error(f"Error parsing Socrata event: {e}")
                continue
        
        return events
    
    def _parse_json_events(self, data: Dict[str, Any], city: str, country: str) -> List[Event]:
        """Parse events from JSON APIs."""
        events = []
        
        # Handle different JSON structures
        event_list = []
        if isinstance(data, list):
            event_list = data
        elif isinstance(data, dict):
            # Try common keys
            for key in ['events', 'data', 'items', 'results']:
                if key in data and isinstance(data[key], list):
                    event_list = data[key]
                    break
        
        for event_data in event_list:
            try:
                event = self._parse_json_event(event_data, city, country)
                if event:
                    events.append(event)
            except Exception as e:
                logger.error(f"Error parsing JSON event: {e}")
                continue
        
        return events
    
    def _parse_socrata_event(self, event_data: Dict[str, Any], city: str, country: str) -> Optional[Event]:
        """Parse a Socrata event."""
        try:
            # Extract title
            title = event_data.get('title') or event_data.get('name') or event_data.get('event_name', '').strip()
            if not title:
                return None
            
            # Extract description
            description = event_data.get('description') or event_data.get('summary', '').strip()
            
            # Extract start date
            start_date = None
            date_fields = ['start_date', 'event_date', 'date', 'datetime', 'start_time']
            for field in date_fields:
                if field in event_data and event_data[field]:
                    try:
                        date_str = str(event_data[field])
                        start_date = self._parse_date_string(date_str)
                        if start_date:
                            break
                    except:
                        continue
            
            if not start_date:
                return None
            
            # Extract location
            venue_name = event_data.get('venue') or event_data.get('location_name', '')
            address = event_data.get('address') or event_data.get('location', f"{city}, {country}")
            
            location = Location(
                address=address,
                city=city,
                country=country,
                venue_name=venue_name
            )
            
            # Extract price
            price = None
            currency = None
            price_text = event_data.get('price') or event_data.get('cost', '')
            if price_text:
                if 'free' in price_text.lower():
                    price = "Free"
                else:
                    price = str(price_text)
            
            # Create event source
            source = EventSource(
                platform=self.platform_name,
                url=event_data.get('url') or event_data.get('link', ''),
                scraped_at=datetime.utcnow(),
                source_id=event_data.get('id') or event_data.get('event_id', '')
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
            logger.error(f"Error parsing Socrata event: {e}")
            return None
    
    def _parse_json_event(self, event_data: Dict[str, Any], city: str, country: str) -> Optional[Event]:
        """Parse a JSON event."""
        try:
            # Extract title
            title = event_data.get('title') or event_data.get('name') or event_data.get('event_name', '').strip()
            if not title:
                return None
            
            # Extract description
            description = event_data.get('description') or event_data.get('summary', '').strip()
            
            # Extract start date
            start_date = None
            date_fields = ['start_date', 'event_date', 'date', 'datetime', 'start_time', 'start']
            for field in date_fields:
                if field in event_data and event_data[field]:
                    try:
                        date_value = event_data[field]
                        if isinstance(date_value, str):
                            start_date = self._parse_date_string(date_value)
                        elif isinstance(date_value, (int, float)):
                            start_date = datetime.fromtimestamp(date_value)
                        if start_date:
                            break
                    except:
                        continue
            
            if not start_date:
                return None
            
            # Extract location
            venue_name = event_data.get('venue') or event_data.get('location_name') or event_data.get('place', '')
            address = event_data.get('address') or event_data.get('location') or f"{city}, {country}"
            
            # Handle nested location objects
            if isinstance(address, dict):
                address = address.get('address') or address.get('name') or f"{city}, {country}"
            
            location = Location(
                address=str(address),
                city=city,
                country=country,
                venue_name=str(venue_name) if venue_name else None
            )
            
            # Extract price
            price = None
            currency = None
            price_data = event_data.get('price') or event_data.get('cost') or event_data.get('ticket_price')
            if price_data:
                if isinstance(price_data, dict):
                    price = price_data.get('amount')
                    currency = price_data.get('currency')
                else:
                    price_text = str(price_data)
                    if 'free' in price_text.lower():
                        price = "Free"
                    else:
                        price = price_text
            
            # Create event source
            source = EventSource(
                platform=self.platform_name,
                url=event_data.get('url') or event_data.get('link') or event_data.get('event_url', ''),
                scraped_at=datetime.utcnow(),
                source_id=str(event_data.get('id') or event_data.get('event_id', ''))
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
            logger.error(f"Error parsing JSON event: {e}")
            return None
    
    def _parse_date_string(self, date_str: str) -> Optional[datetime]:
        """Parse various date string formats."""
        if not date_str:
            return None
        
        # Common date formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M',
            '%m/%d/%Y',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%d/%m/%Y',
            '%B %d, %Y %H:%M:%S',
            '%B %d, %Y %H:%M',
            '%B %d, %Y',
            '%d %B %Y %H:%M:%S',
            '%d %B %Y %H:%M',
            '%d %B %Y',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        # Try ISO format
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            pass
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
