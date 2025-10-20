"""Enhanced stealth scraper with anti-detection features."""
import asyncio
import random
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from core.models import Event, ContactInfo, EventSource
from core.config import settings

logger = logging.getLogger(__name__)


class StealthScraper:
    """Enhanced scraper with stealth capabilities."""
    
    def __init__(self):
        self.user_agent = UserAgent()
        self.session: Optional[aiohttp.ClientSession] = None
        self.cookie_jar = aiohttp.CookieJar()
        
        # Real browser headers for different browsers
        self.browser_headers = {
            'chrome': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'max-age=0',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"macOS"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'Connection': 'keep-alive',
            },
            'firefox': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'max-age=0',
                'Upgrade-Insecure-Requests': '1',
                'Connection': 'keep-alive',
            },
            'safari': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
            }
        }
        
        # Common referrers to make requests look more natural
        self.referrers = [
            'https://www.google.com/',
            'https://www.bing.com/',
            'https://duckduckgo.com/',
            'https://www.yahoo.com/',
            'https://www.facebook.com/',
            'https://www.linkedin.com/',
            'https://www.twitter.com/',
        ]
    
    async def __aenter__(self):
        """Async context manager entry with enhanced stealth setup."""
        # Choose random browser type
        browser_type = random.choice(list(self.browser_headers.keys()))
        base_headers = self.browser_headers[browser_type].copy()
        
        # Add random user agent
        base_headers['User-Agent'] = self.user_agent.random
        
        # Add random referrer
        base_headers['Referer'] = random.choice(self.referrers)
        
        # Configure connector with realistic settings
        connector = aiohttp.TCPConnector(
            limit=10,
            limit_per_host=3,  # More conservative
            ssl=False,
            enable_cleanup_closed=True,
            keepalive_timeout=30,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        # Realistic timeout settings
        timeout = aiohttp.ClientTimeout(
            total=60,  # Longer total timeout
            connect=15,  # Longer connect timeout
            sock_read=30,  # Longer read timeout
        )
        
        self.session = aiohttp.ClientSession(
            headers=base_headers,
            timeout=timeout,
            connector=connector,
            cookie_jar=self.cookie_jar,
            trust_env=True,  # Use system proxy settings
        )
        
        logger.info(f"Initialized stealth scraper with {browser_type} headers")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            try:
                await self.session.close()
            except Exception as e:
                logger.warning(f"Error closing stealth session: {e}")
            finally:
                self.session = None
    
    async def make_stealth_request(
        self, 
        url: str, 
        params: Optional[Dict[str, Any]] = None,
        method: str = 'GET',
        **kwargs
    ) -> Optional[str]:
        """Make a stealth HTTP request with anti-detection features."""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        try:
            # Random delay between requests (human-like behavior)
            delay = random.uniform(1.0, 3.0)  # 1-3 seconds
            await asyncio.sleep(delay)
            
            # Occasionally add longer delays (human browsing patterns)
            if random.random() < 0.1:  # 10% chance
                long_delay = random.uniform(5.0, 10.0)
                logger.info(f"Adding human-like delay: {long_delay:.1f}s")
                await asyncio.sleep(long_delay)
            
            # Rotate user agent occasionally
            if random.random() < 0.2:  # 20% chance
                new_ua = self.user_agent.random
                self.session.headers['User-Agent'] = new_ua
                logger.debug(f"Rotated user agent: {new_ua[:50]}...")
            
            # Add random referrer occasionally
            if random.random() < 0.3:  # 30% chance
                new_referrer = random.choice(self.referrers)
                self.session.headers['Referer'] = new_referrer
                logger.debug(f"Updated referrer: {new_referrer}")
            
            # Make the request
            async with self.session.request(method, url, params=params, **kwargs) as response:
                logger.debug(f"Request to {url}: {response.status}")
                
                if response.status == 200:
                    return await response.text()
                elif response.status == 429:  # Rate limited
                    logger.warning(f"Rate limited by {url}, waiting longer...")
                    await asyncio.sleep(random.uniform(10.0, 20.0))
                    return None
                elif response.status in [403, 404, 500, 503]:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
                else:
                    logger.warning(f"Unexpected HTTP {response.status} for {url}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.warning(f"Timeout for {url}")
            return None
        except Exception as e:
            logger.error(f"Error making stealth request to {url}: {e}")
            return None
    
    async def make_stealth_get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Make a stealth GET request."""
        return await self.make_stealth_request(url, params, method='GET')
    
    async def make_stealth_post(self, url: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Make a stealth POST request."""
        return await self.make_stealth_request(url, params, method='POST', data=data)
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content."""
        return BeautifulSoup(html, 'lxml')
    
    def extract_text(self, element) -> Optional[str]:
        """Extract text from BeautifulSoup element."""
        if element:
            return element.get_text(strip=True)
        return None
    
    def extract_href(self, element, base_url: str = "") -> Optional[str]:
        """Extract href from BeautifulSoup element."""
        if element and element.get('href'):
            href = element.get('href')
            if href.startswith('/'):
                return f"{base_url}{href}"
            elif href.startswith('http'):
                return href
            else:
                return f"{base_url}/{href}"
        return None
    
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
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ",
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
        if any(word in price_text for word in ["free", "no cost", "gratis", "complimentary"]):
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
    
    def create_event_source(self, url: str, platform: str, source_id: Optional[str] = None) -> EventSource:
        """Create an EventSource object."""
        return EventSource(
            platform=platform,
            url=url,
            scraped_at=datetime.utcnow(),
            source_id=source_id
        )
