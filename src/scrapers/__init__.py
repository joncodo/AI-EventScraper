"""
Scrapers module for AI Event Scraper

Multi-platform event data collection from:
- Eventbrite: Professional events and conferences
- Meetup: Community meetups and networking events  
- Facebook: Social events and local gatherings
- [Future]: Additional platforms as needed

Architecture:
- BaseScraper: Abstract base class with common functionality
- Platform-specific scrapers: EventbriteScraper, MeetupScraper, FacebookScraper
- ScraperManager: Coordinates multiple scrapers with concurrency control
"""

from .base_scraper import BaseScraper
from .eventbrite_scraper import EventbriteScraper
from .meetup_scraper import MeetupScraper
from .facebook_scraper import FacebookScraper
from .scraper_manager import ScraperManager, scraper_manager

__all__ = [
    "BaseScraper",
    "EventbriteScraper", 
    "MeetupScraper",
    "FacebookScraper",
    "ScraperManager",
    "scraper_manager"
]
