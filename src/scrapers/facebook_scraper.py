"""Facebook Events scraper for the AI Event Scraper."""
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlencode, quote

from .base_scraper import BaseScraper
from core.models import Event, Location, ContactInfo, EventSource

logger = logging.getLogger(__name__)


class FacebookScraper(BaseScraper):
    """Scraper for Facebook Events."""
    
    def get_base_url(self) -> str:
        return "https://www.facebook.com"
    
    async def scrape_events(
        self, 
        city: str, 
        country: str, 
        radius_km: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """Scrape events from Facebook Events."""
        events = []
        
        try:
            # Facebook Events search URL
            search_url = "https://www.facebook.com/events/search"
            
            # Build search parameters
            params = {
                'q': f'{city} {country}',
                'sort': 'date'
            }
            
            # Add date filters if provided
            if start_date:
                params['start_date'] = start_date.strftime('%Y-%m-%d')
            if end_date:
                params['end_date'] = end_date.strftime('%Y-%m-%d')
            
            # Make request
            html = await self.make_request(search_url, params)
            if not html:
                return events
            
            # Parse HTML
            soup = self.parse_html(html)
            
            # Find event cards
            event_cards = soup.find_all('div', {'data-testid': 'event-card'})
            
            for card in event_cards:
                try:
                    event = await self._parse_event_card(card, city, country)
                    if event:
                        events.append(event)
                except Exception as e:
                    logger.error(f"Error parsing Facebook event card: {e}")
                    continue
            
            logger.info(f"Scraped {len(events)} events from Facebook")
            
        except Exception as e:
            logger.error(f"Error scraping Facebook: {e}")
        
        return events
    
    async def _parse_event_card(self, card, city: str, country: str) -> Optional[Event]:
        """Parse an individual event card."""
        try:
            # Extract title and URL
            title_element = card.find('h3')
            if not title_element:
                return None
            
            title = self.clean_text(title_element.get_text())
            event_link = title_element.find('a')
            event_url = self.extract_href(event_link) if event_link else None
            
            if not event_url:
                return None
            
            # Extract date and time
            date_element = card.find('time')
            start_date = None
            if date_element:
                datetime_attr = date_element.get('datetime')
                if datetime_attr:
                    start_date = self.parse_date(datetime_attr)
            
            if not start_date:
                return None
            
            # Extract location
            location_element = card.find('div', class_='event-location')
            venue_name = None
            address = None
            
            if location_element:
                venue_element = location_element.find('span', class_='event-venue')
                if venue_element:
                    venue_name = self.clean_text(venue_element.get_text())
                
                address_element = location_element.find('span', class_='event-address')
                if address_element:
                    address = self.clean_text(address_element.get_text())
            
            # Create location object
            location = Location(
                address=address or f"{city}, {country}",
                city=city,
                country=country,
                venue_name=venue_name
            )
            
            # Extract attendees count
            attendees_element = card.find('span', class_='event-attendees')
            attendees_count = None
            if attendees_element:
                attendees_text = self.clean_text(attendees_element.get_text())
                # Extract number from text like "15 interested"
                import re
                match = re.search(r'(\d+)', attendees_text)
                if match:
                    attendees_count = int(match.group(1))
            
            # Extract price (usually free for Facebook events)
            price_element = card.find('span', class_='event-price')
            price = "Free"  # Most Facebook events are free
            if price_element:
                price_text = self.clean_text(price_element.get_text())
                if price_text and price_text.lower() != "free":
                    price, _ = self.extract_price(price_text)
            
            # Extract description (basic)
            description_element = card.find('div', class_='event-description')
            description = None
            if description_element:
                description = self.clean_text(description_element.get_text())
            
            # Create event source
            source = self.create_event_source(event_url)
            
            # Create event object
            event = Event(
                title=title,
                description=description,
                start_date=start_date,
                location=location,
                price=price,
                sources=[source]
            )
            
            # Add attendees count to description if available
            if attendees_count:
                if not event.description:
                    event.description = ""
                event.description += f" ({attendees_count} interested)"
            
            return event
            
        except Exception as e:
            logger.error(f"Error parsing Facebook event card: {e}")
            return None
    
    async def get_event_details(self, event_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific event."""
        try:
            html = await self.make_request(event_url)
            if not html:
                return None
            
            soup = self.parse_html(html)
            
            details = {}
            
            # Extract full description
            description_element = soup.find('div', class_='event-description')
            if description_element:
                details['description'] = self.clean_text(description_element.get_text())
            
            # Extract organizer information
            organizer_element = soup.find('div', class_='event-organizer')
            if organizer_element:
                organizer_name = organizer_element.find('h3')
                if organizer_name:
                    details['organizer'] = self.clean_text(organizer_name.get_text())
            
            # Extract contact information
            contact_section = soup.find('div', class_='event-contact')
            if contact_section:
                contact_text = self.clean_text(contact_section.get_text())
                details['contact_info'] = self.extract_contact_info(contact_text)
            
            # Extract tags/categories
            tags_element = soup.find('div', class_='event-categories')
            if tags_element:
                tags = [self.clean_text(tag.get_text()) for tag in tags_element.find_all('span')]
                details['tags'] = tags
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting Facebook event details: {e}")
            return None

