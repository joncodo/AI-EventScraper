"""Base scraper class for all event scrapers."""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from core.models import Event, ContactInfo, EventSource
from core.config import settings

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all event scrapers."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.user_agent = UserAgent()
        self.platform_name = self.__class__.__name__.replace("Scraper", "").lower()
    
    async def __aenter__(self):
        """Async context manager entry."""
        headers = {
            'User-Agent': self.user_agent.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Configure connector with SSL settings
        connector = aiohttp.TCPConnector(
            limit=10,
            limit_per_host=5,
            ssl=False,  # Disable SSL verification for scraping
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_read=20)
        self.session = aiohttp.ClientSession(
            headers=headers, 
            timeout=timeout,
            connector=connector
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            try:
                await self.session.close()
            except Exception as e:
                logger.warning(f"Error closing session: {e}")
            finally:
                self.session = None
    
    @abstractmethod
    async def scrape_events(
        self, 
        city: str, 
        country: str, 
        radius_km: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """Scrape events from the platform."""
        pass
    
    async def make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Make an HTTP request with error handling."""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        try:
            await asyncio.sleep(settings.request_delay_seconds)
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error making request to {url}: {e}")
            return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content."""
        return BeautifulSoup(html, 'lxml')
    
    def extract_text(self, element) -> Optional[str]:
        """Extract text from BeautifulSoup element."""
        if element:
            return element.get_text(strip=True)
        return None
    
    def extract_href(self, element) -> Optional[str]:
        """Extract href from BeautifulSoup element."""
        if element and element.get('href'):
            href = element.get('href')
            if href.startswith('/'):
                return f"https://{self.get_base_url()}{href}"
            return href
        return None
    
    @abstractmethod
    def get_base_url(self) -> str:
        """Get the base URL for the platform."""
        pass
    
    def create_event_source(self, url: str, source_id: Optional[str] = None) -> EventSource:
        """Create an EventSource object."""
        return EventSource(
            platform=self.platform_name,
            url=url,
            scraped_at=datetime.utcnow(),
            source_id=source_id
        )
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Remove common unwanted characters
        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        return text.strip()
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
        
        # Common date formats to try
        date_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%m/%d/%Y %H:%M",
            "%m/%d/%Y",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
            "%B %d, %Y %H:%M",
            "%B %d, %Y",
            "%d %B %Y %H:%M",
            "%d %B %Y",
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def extract_price(self, price_text: str) -> tuple:
        """Extract price and currency from text."""
        if not price_text:
            return None, None
        
        price_text = price_text.lower().strip()
        
        # Check for free events
        if any(word in price_text for word in ["free", "no cost", "gratis"]):
            return "Free", None
        
        # Extract currency symbols
        currencies = {
            "$": "USD",
            "€": "EUR", 
            "£": "GBP",
            "¥": "JPY",
            "₹": "INR",
            "CAD": "CAD",
            "AUD": "AUD"
        }
        
        currency = None
        for symbol, code in currencies.items():
            if symbol in price_text:
                currency = code
                break
        
        # Extract numeric price
        import re
        price_match = re.search(r'[\d,]+\.?\d*', price_text)
        if price_match:
            price = price_match.group().replace(',', '')
            return price, currency
        
        return None, None
    
    def extract_contact_info(self, text: str) -> ContactInfo:
        """Extract contact information from text."""
        import re
        
        contact_info = ContactInfo()
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info.email = email_match.group()
        
        # Extract phone
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info.phone = phone_match.group()
        
        # Extract website
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        url_match = re.search(url_pattern, text)
        if url_match:
            contact_info.website = url_match.group()
        
        return contact_info
