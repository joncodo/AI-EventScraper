"""
Instagram Events Scraper

Scrapes event-related posts from Instagram using hashtags and location data.
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class InstagramScraper(BaseScraper):
    """Instagram events scraper."""
    
    def __init__(self):
        super().__init__()
        self.platform = "Instagram"
        self.base_url = "https://www.instagram.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        # Event-related hashtags
        self.event_hashtags = [
            "#event", "#events", "#meetup", "#conference", "#workshop",
            "#seminar", "#networking", "#tech", "#startup", "#business",
            "#music", "#concert", "#festival", "#exhibition", "#art",
            "#culture", "#food", "#drink", "#party", "#celebration"
        ]
    
    async def scrape_events(self, city: str, country: str = "United States", limit: int = 100) -> List[Dict[str, Any]]:
        """Scrape events from Instagram."""
        logger.info(f"Scraping Instagram events for {city}, {country}")
        
        events = []
        
        try:
            # Search for event-related posts
            for hashtag in self.event_hashtags[:5]:  # Limit to avoid rate limits
                try:
                    posts = await self._search_posts(f"{hashtag} {city}", limit=20)
                    
                    for post in posts:
                        event = await self._parse_post_to_event(post, city, country)
                        if event:
                            events.append(event)
                            
                    # Rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error scraping hashtag {hashtag}: {e}")
                    continue
            
            # Remove duplicates and limit results
            events = self._deduplicate_events(events)[:limit]
            
            logger.info(f"Found {len(events)} events from Instagram")
            return events
            
        except Exception as e:
            logger.error(f"Error scraping Instagram events: {e}")
            return []
    
    async def _search_posts(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for Instagram posts using query."""
        # Note: This is a mock implementation
        # In production, you would use Instagram Basic Display API or Graph API
        
        mock_posts = [
            {
                "id": "1234567890",
                "caption": f"Amazing art exhibition happening in {query.split()[-1]}! Don't miss it! #art #exhibition",
                "media_type": "IMAGE",
                "media_url": "https://example.com/image1.jpg",
                "timestamp": "2025-10-18T10:00:00Z",
                "username": "artgallery123",
                "like_count": 45,
                "comment_count": 8
            },
            {
                "id": "1234567891",
                "caption": f"Food festival this weekend in {query.split()[-1]}! Amazing local vendors! #food #festival",
                "media_type": "CAROUSEL_ALBUM",
                "media_url": "https://example.com/image2.jpg",
                "timestamp": "2025-10-17T15:30:00Z",
                "username": "foodie_events",
                "like_count": 120,
                "comment_count": 25
            }
        ]
        
        return mock_posts[:limit]
    
    async def _parse_post_to_event(self, post: Dict[str, Any], city: str, country: str) -> Optional[Dict[str, Any]]:
        """Parse an Instagram post into an event object."""
        try:
            caption = post.get("caption", "")
            timestamp = post.get("timestamp", "")
            username = post.get("username", "")
            
            # Extract event information
            event = {
                "title": self._extract_event_title(caption),
                "description": caption,
                "start_date": self._extract_event_date(caption, timestamp),
                "end_date": None,
                "location": {
                    "address": "",
                    "city": city,
                    "state": "",
                    "country": country,
                    "latitude": None,
                    "longitude": None,
                    "venue_name": ""
                },
                "contact_info": {
                    "email": "",
                    "phone": "",
                    "website": f"https://instagram.com/{username}"
                },
                "price": "Free",  # Default for social media posts
                "category": self._categorize_event(caption),
                "tags": self._extract_tags(caption),
                "sources": [{
                    "platform": "Instagram",
                    "url": f"https://instagram.com/p/{post.get('id', '')}",
                    "scraped_at": datetime.now()
                }],
                "ai_processed": False,
                "confidence_score": 0.6,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            return event
            
        except Exception as e:
            logger.error(f"Error parsing Instagram post to event: {e}")
            return None
    
    def _extract_event_title(self, caption: str) -> str:
        """Extract event title from Instagram caption."""
        # Simple extraction - in production, use AI
        words = caption.split()
        if len(words) > 8:
            return " ".join(words[:8]) + "..."
        return caption
    
    def _extract_event_date(self, caption: str, timestamp: str) -> datetime:
        """Extract event date from Instagram caption."""
        # Simple implementation - in production, use date parsing
        try:
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            return datetime.now() + timedelta(days=7)
    
    def _categorize_event(self, caption: str) -> str:
        """Categorize event based on caption content."""
        caption_lower = caption.lower()
        
        if any(word in caption_lower for word in ["art", "exhibition", "gallery", "museum"]):
            return "Arts & Culture"
        elif any(word in caption_lower for word in ["food", "drink", "restaurant", "bar"]):
            return "Food & Drink"
        elif any(word in caption_lower for word in ["music", "concert", "festival", "band"]):
            return "Music & Entertainment"
        elif any(word in caption_lower for word in ["fitness", "yoga", "workout", "health"]):
            return "Health & Wellness"
        elif any(word in caption_lower for word in ["party", "celebration", "birthday", "wedding"]):
            return "Community & Social"
        else:
            return "Arts & Culture"
    
    def _extract_tags(self, caption: str) -> List[str]:
        """Extract hashtags and keywords as tags."""
        tags = []
        
        # Extract hashtags
        words = caption.split()
        for word in words:
            if word.startswith("#"):
                tags.append(word[1:].lower())
        
        # Add category-based tags
        caption_lower = caption.lower()
        if "art" in caption_lower:
            tags.append("art")
        if "food" in caption_lower:
            tags.append("food")
        if "music" in caption_lower:
            tags.append("music")
        if "fitness" in caption_lower:
            tags.append("fitness")
        
        return list(set(tags))  # Remove duplicates
