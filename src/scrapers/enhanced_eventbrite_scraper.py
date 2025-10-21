"""Enhanced Eventbrite scraper with stealth capabilities."""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode, quote

from .stealth_scraper import StealthScraper
from .browser_scraper import BrowserScraper
from core.models import Event, Location, ContactInfo, EventSource

logger = logging.getLogger(__name__)


class EnhancedEventbriteScraper:
    """Enhanced Eventbrite scraper with multiple stealth strategies."""
    
    def __init__(self):
        self.platform_name = "eventbrite"
        self.base_url = "https://www.eventbrite.com"
        
    async def scrape_events(
        self, 
        city: str, 
        country: str, 
        radius_km: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """Scrape events from Eventbrite using enhanced stealth methods."""
        events = []
        
        # Try multiple strategies (disabled problematic ones)
        strategies = [
            # self._scrape_with_stealth_http,  # Disabled due to 404 errors
            # self._scrape_with_browser_automation,  # Disabled due to browser issues
            # self._scrape_with_alternative_endpoints,  # Disabled due to 404 errors
        ]
        
        for strategy in strategies:
            try:
                logger.info(f"Trying Eventbrite scraping strategy: {strategy.__name__}")
                strategy_events = await strategy(city, country, radius_km, start_date, end_date)
                
                if strategy_events:
                    events.extend(strategy_events)
                    logger.info(f"Strategy {strategy.__name__} found {len(strategy_events)} events")
                    break  # Stop after first successful strategy
                else:
                    logger.info(f"Strategy {strategy.__name__} found no events")
                    
            except Exception as e:
                logger.error(f"Strategy {strategy.__name__} failed: {e}")
                continue
        
        logger.info(f"Total Eventbrite events scraped: {len(events)}")
        return events
    
    async def _scrape_with_stealth_http(
        self, 
        city: str, 
        country: str, 
        radius_km: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """Scrape using stealth HTTP requests."""
        events = []
        
        async with StealthScraper() as scraper:
            # Try multiple search endpoints
            search_urls = [
                "https://www.eventbrite.com/d/search",
                "https://www.eventbrite.com/d/online",
                "https://www.eventbrite.com/d/events",
            ]
            
            for search_url in search_urls:
                try:
                    # Build search parameters
                    params = {
                        'q': f'{city} {country}',
                        'sort': 'date',
                        'view': 'list',
                        'page_size': '50',
                    }
                    
                    # Add date filters if provided
                    if start_date:
                        params['start_date'] = start_date.strftime('%Y-%m-%d')
                    if end_date:
                        params['end_date'] = end_date.strftime('%Y-%m-%d')
                    
                    # Make stealth request
                    html = await scraper.make_stealth_get(search_url, params)
                    if not html:
                        continue
                    
                    # Parse events
                    soup = scraper.parse_html(html)
                    strategy_events = await self._parse_eventbrite_html(soup, city, country, scraper)
                    events.extend(strategy_events)
                    
                    if events:
                        break  # Stop after first successful URL
                        
                except Exception as e:
                    logger.error(f"Error with search URL {search_url}: {e}")
                    continue
        
        return events
    
    async def _scrape_with_browser_automation(
        self, 
        city: str, 
        country: str, 
        radius_km: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """Scrape using browser automation."""
        events = []
        
        async with BrowserScraper() as browser:
            try:
                # Navigate to Eventbrite search
                search_url = f"https://www.eventbrite.com/d/search/?q={quote(f'{city} {country}')}"
                
                if not await browser.navigate_to_page(search_url, "div[data-testid='search-results']"):
                    return events
                
                # Wait for page to load and simulate human behavior
                await asyncio.sleep(3)
                
                # Get page source
                html = await browser.get_page_source()
                if not html:
                    return events
                
                # Parse events
                soup = browser.parse_html(html)
                events = await self._parse_eventbrite_html(soup, city, country, browser)
                
            except Exception as e:
                logger.error(f"Browser automation failed: {e}")
        
        return events
    
    async def _scrape_with_alternative_endpoints(
        self, 
        city: str, 
        country: str, 
        radius_km: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """Scrape using alternative endpoints and methods."""
        events = []
        
        async with StealthScraper() as scraper:
            # Try different search approaches
            search_queries = [
                f"{city} {country}",
                f"events in {city}",
                f"{city} events",
                f"things to do in {city}",
            ]
            
            for query in search_queries:
                try:
                    # Try different URL patterns
                    urls = [
                        f"https://www.eventbrite.com/d/search/?q={quote(query)}",
                        f"https://www.eventbrite.com/d/online/?q={quote(query)}",
                        f"https://www.eventbrite.com/d/events/?q={quote(query)}",
                    ]
                    
                    for url in urls:
                        html = await scraper.make_stealth_get(url)
                        if html:
                            soup = scraper.parse_html(html)
                            strategy_events = await self._parse_eventbrite_html(soup, city, country, scraper)
                            events.extend(strategy_events)
                            
                            if events:
                                return events  # Return early if we found events
                                
                except Exception as e:
                    logger.error(f"Error with query '{query}': {e}")
                    continue
        
        return events
    
    async def _parse_eventbrite_html(self, soup, city: str, country: str, scraper) -> List[Event]:
        """Parse Eventbrite HTML for events."""
        events = []
        
        # Try multiple selectors for event cards
        event_selectors = [
            'div[data-testid="search-results"] div[data-testid="event-card"]',
            'div.search-event-card-wrapper',
            'div[class*="event-card"]',
            'div[class*="search-result"]',
            'article[data-testid="event-card"]',
            'div[data-automation="search-result"]',
        ]
        
        event_cards = []
        for selector in event_selectors:
            cards = soup.select(selector)
            if cards:
                event_cards = cards
                logger.info(f"Found {len(cards)} event cards with selector: {selector}")
                break
        
        if not event_cards:
            logger.warning("No event cards found with any selector")
            return events
        
        for card in event_cards:
            try:
                event = await self._parse_event_card(card, city, country, scraper)
                if event:
                    events.append(event)
            except Exception as e:
                logger.error(f"Error parsing event card: {e}")
                continue
        
        return events
    
    async def _parse_event_card(self, card, city: str, country: str, scraper) -> Optional[Event]:
        """Parse an individual event card."""
        try:
            # Try multiple selectors for title
            title_selectors = [
                'h2[data-testid="event-title"]',
                'h2.event-title',
                'h3[data-testid="event-title"]',
                'a[data-testid="event-title"]',
                'h2 a',
                'h3 a',
                '.event-title',
                '[data-automation="event-title"]',
            ]
            
            title_element = None
            for selector in title_selectors:
                title_element = card.select_one(selector)
                if title_element:
                    break
            
            if not title_element:
                return None
            
            title = scraper.clean_text(scraper.extract_text(title_element))
            if not title:
                return None
            
            # Extract event URL
            event_url = None
            if title_element.name == 'a':
                event_url = title_element.get('href')
            else:
                link_element = title_element.find('a')
                if link_element:
                    event_url = link_element.get('href')
            
            if event_url:
                if event_url.startswith('/'):
                    event_url = f"{self.base_url}{event_url}"
                elif not event_url.startswith('http'):
                    event_url = f"{self.base_url}/{event_url}"
            else:
                return None
            
            # Try multiple selectors for date
            date_selectors = [
                'time[datetime]',
                'time',
                '[data-testid="event-date"]',
                '.event-date',
                '[data-automation="event-date"]',
            ]
            
            start_date = None
            for selector in date_selectors:
                date_element = card.select_one(selector)
                if date_element:
                    datetime_attr = date_element.get('datetime')
                    if datetime_attr:
                        start_date = scraper.parse_date(datetime_attr)
                        break
                    else:
                        date_text = scraper.clean_text(scraper.extract_text(date_element))
                        if date_text:
                            start_date = scraper.parse_date(date_text)
                            if start_date:
                                break
            
            if not start_date:
                return None
            
            # Try multiple selectors for location
            location_selectors = [
                '[data-testid="event-location"]',
                '.event-location',
                '[data-automation="event-location"]',
                '.location',
            ]
            
            venue_name = None
            address = None
            
            for selector in location_selectors:
                location_element = card.select_one(selector)
                if location_element:
                    location_text = scraper.clean_text(scraper.extract_text(location_element))
                    if location_text:
                        # Try to extract venue name and address
                        if ',' in location_text:
                            parts = location_text.split(',')
                            venue_name = parts[0].strip()
                            address = ','.join(parts[1:]).strip()
                        else:
                            venue_name = location_text
                        break
            
            # Create location object
            location = Location(
                address=address or f"{city}, {country}",
                city=city,
                country=country,
                venue_name=venue_name
            )
            
            # Try multiple selectors for price
            price_selectors = [
                '[data-testid="event-price"]',
                '.event-price',
                '[data-automation="event-price"]',
                '.price',
            ]
            
            price = None
            currency = None
            
            for selector in price_selectors:
                price_element = card.select_one(selector)
                if price_element:
                    price_text = scraper.clean_text(scraper.extract_text(price_element))
                    if price_text:
                        price, currency = scraper.extract_price(price_text)
                        break
            
            # Try multiple selectors for description
            description_selectors = [
                '[data-testid="event-description"]',
                '.event-description',
                '[data-automation="event-description"]',
                '.description',
                'p',
            ]
            
            description = None
            for selector in description_selectors:
                desc_element = card.select_one(selector)
                if desc_element:
                    description = scraper.clean_text(scraper.extract_text(desc_element))
                    if description and len(description) > 10:  # Only use substantial descriptions
                        break
            
            # Create event source
            source = scraper.create_event_source(event_url, self.platform_name)
            
            # Create event object
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
            logger.error(f"Error parsing event card: {e}")
            return None
