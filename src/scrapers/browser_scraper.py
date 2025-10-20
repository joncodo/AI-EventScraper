"""Browser automation scraper using Selenium with stealth capabilities."""
import asyncio
import random
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    import undetected_chromedriver as uc
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from core.models import Event, ContactInfo, EventSource
from core.config import settings

logger = logging.getLogger(__name__)


class BrowserScraper:
    """Browser automation scraper with stealth capabilities."""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.is_headless = True  # Set to False for debugging
        
    async def __aenter__(self):
        """Async context manager entry."""
        if not SELENIUM_AVAILABLE:
            logger.error("Selenium not available. Install selenium and undetected-chromedriver.")
            return self
        
        try:
            # Use undetected-chromedriver for better stealth
            options = uc.ChromeOptions()
            
            # Stealth options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Performance options
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')  # Faster loading
            options.add_argument('--disable-javascript')  # Some sites don't need JS
            
            # User agent
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            if self.is_headless:
                options.add_argument('--headless=new')
            
            # Create driver
            self.driver = uc.Chrome(options=options)
            
            # Execute stealth script
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set realistic window size
            self.driver.set_window_size(1920, 1080)
            
            # Set timeouts
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, 20)
            
            logger.info("Browser scraper initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize browser scraper: {e}")
            self.driver = None
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
            finally:
                self.driver = None
                self.wait = None
    
    async def navigate_to_page(self, url: str, wait_for_element: Optional[str] = None) -> bool:
        """Navigate to a page with stealth behavior."""
        if not self.driver:
            return False
        
        try:
            # Random delay before navigation
            await asyncio.sleep(random.uniform(1.0, 3.0))
            
            # Navigate to page
            self.driver.get(url)
            
            # Random delay after page load
            await asyncio.sleep(random.uniform(2.0, 4.0))
            
            # Wait for specific element if provided
            if wait_for_element:
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element)))
                except TimeoutException:
                    logger.warning(f"Timeout waiting for element: {wait_for_element}")
                    return False
            
            # Simulate human behavior - random mouse movements
            await self._simulate_human_behavior()
            
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            return False
    
    async def _simulate_human_behavior(self):
        """Simulate human browsing behavior."""
        try:
            # Random scroll
            if random.random() < 0.7:  # 70% chance
                scroll_amount = random.randint(100, 500)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Random pause
            if random.random() < 0.3:  # 30% chance
                await asyncio.sleep(random.uniform(1.0, 3.0))
                
        except Exception as e:
            logger.debug(f"Error simulating human behavior: {e}")
    
    async def get_page_source(self) -> Optional[str]:
        """Get the page source."""
        if not self.driver:
            return None
        
        try:
            return self.driver.page_source
        except Exception as e:
            logger.error(f"Error getting page source: {e}")
            return None
    
    async def find_elements(self, selector: str) -> List[Any]:
        """Find elements by CSS selector."""
        if not self.driver:
            return []
        
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            return elements
        except Exception as e:
            logger.error(f"Error finding elements with selector {selector}: {e}")
            return []
    
    async def find_element(self, selector: str) -> Optional[Any]:
        """Find single element by CSS selector."""
        if not self.driver:
            return None
        
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element
        except Exception as e:
            logger.debug(f"Element not found with selector {selector}: {e}")
            return None
    
    async def click_element(self, selector: str) -> bool:
        """Click an element."""
        if not self.driver:
            return False
        
        try:
            element = await self.find_element(selector)
            if element:
                # Scroll to element first
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
                # Click element
                element.click()
                await asyncio.sleep(random.uniform(1.0, 2.0))
                return True
        except Exception as e:
            logger.error(f"Error clicking element {selector}: {e}")
        
        return False
    
    async def fill_input(self, selector: str, text: str) -> bool:
        """Fill an input field with text."""
        if not self.driver:
            return False
        
        try:
            element = await self.find_element(selector)
            if element:
                # Clear field first
                element.clear()
                await asyncio.sleep(random.uniform(0.2, 0.5))
                
                # Type text with human-like delays
                for char in text:
                    element.send_keys(char)
                    await asyncio.sleep(random.uniform(0.05, 0.15))
                
                await asyncio.sleep(random.uniform(0.5, 1.0))
                return True
        except Exception as e:
            logger.error(f"Error filling input {selector}: {e}")
        
        return False
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content."""
        return BeautifulSoup(html, 'lxml')
    
    def extract_text(self, element) -> Optional[str]:
        """Extract text from element."""
        if element:
            try:
                return element.text.strip()
            except:
                return None
        return None
    
    def extract_attribute(self, element, attribute: str) -> Optional[str]:
        """Extract attribute value from element."""
        if element:
            try:
                return element.get_attribute(attribute)
            except:
                return None
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
