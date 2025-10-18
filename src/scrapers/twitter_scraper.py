"""
Twitter Events Scraper

Scrapes event-related posts from Twitter using hashtags and keywords.
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class TwitterScraper(BaseScraper):
    """Twitter events scraper."""
    
    def __init__(self):
        super().__init__()
        self.platform = "Twitter"
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        # Event-related hashtags and keywords
        self.event_hashtags = [
            "#event", "#events", "#meetup", "#conference", "#workshop",
            "#seminar", "#networking", "#tech", "#startup", "#business",
            "#music", "#concert", "#festival", "#exhibition", "#trade",
            "#expo", "#summit", "#convention", "#gala", "#fundraiser"
        ]
        
        self.event_keywords = [
            "event", "meetup", "conference", "workshop", "seminar",
            "networking", "tech talk", "startup", "business", "music",
            "concert", "festival", "exhibition", "trade show", "expo",
            "summit", "convention", "gala", "fundraiser", "tickets"
        ]
    
    async def scrape_events(self, city: str, country: str = "United States", limit: int = 100) -> List[Dict[str, Any]]:
        """Scrape events from Twitter."""
        logger.info(f"Scraping Twitter events for {city}, {country}")
        
        events = []
        
        try:
            # Search for event-related tweets
            for hashtag in self.event_hashtags[:5]:  # Limit to avoid rate limits
                try:
                    tweets = await self._search_tweets(f"{hashtag} {city}", limit=20)
                    
                    for tweet in tweets:
                        event = await self._parse_tweet_to_event(tweet, city, country)
                        if event:
                            events.append(event)
                            
                    # Rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error scraping hashtag {hashtag}: {e}")
                    continue
            
            # Remove duplicates and limit results
            events = self._deduplicate_events(events)[:limit]
            
            logger.info(f"Found {len(events)} events from Twitter")
            return events
            
        except Exception as e:
            logger.error(f"Error scraping Twitter events: {e}")
            return []
    
    async def _search_tweets(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for tweets using query."""
        # Note: This is a mock implementation
        # In production, you would use Twitter API v2 with proper authentication
        
        mock_tweets = [
            {
                "id": "1234567890",
                "text": f"Join us for an amazing tech meetup in {query.split()[-1]}! #tech #meetup",
                "created_at": "2025-10-18T10:00:00Z",
                "author_id": "user123",
                "public_metrics": {
                    "retweet_count": 5,
                    "like_count": 12,
                    "reply_count": 3
                }
            },
            {
                "id": "1234567891",
                "text": f"Exciting startup networking event happening this weekend in {query.split()[-1]}! #startup #networking",
                "created_at": "2025-10-17T15:30:00Z",
                "author_id": "user456",
                "public_metrics": {
                    "retweet_count": 8,
                    "like_count": 20,
                    "reply_count": 5
                }
            }
        ]
        
        return mock_tweets[:limit]
    
    async def _parse_tweet_to_event(self, tweet: Dict[str, Any], city: str, country: str) -> Optional[Dict[str, Any]]:
        """Parse a tweet into an event object."""
        try:
            text = tweet.get("text", "")
            created_at = tweet.get("created_at", "")
            
            # Extract event information using AI or regex patterns
            event = {
                "title": self._extract_event_title(text),
                "description": text,
                "start_date": self._extract_event_date(text, created_at),
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
                    "website": ""
                },
                "price": "Free",  # Default for social media posts
                "category": self._categorize_event(text),
                "tags": self._extract_tags(text),
                "sources": [{
                    "platform": "Twitter",
                    "url": f"https://twitter.com/i/web/status/{tweet.get('id', '')}",
                    "scraped_at": datetime.now()
                }],
                "ai_processed": False,
                "confidence_score": 0.7,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            return event
            
        except Exception as e:
            logger.error(f"Error parsing tweet to event: {e}")
            return None
    
    def _extract_event_title(self, text: str) -> str:
        """Extract event title from tweet text."""
        # Simple extraction - in production, use AI
        words = text.split()
        if len(words) > 10:
            return " ".join(words[:10]) + "..."
        return text
    
    def _extract_event_date(self, text: str, created_at: str) -> datetime:
        """Extract event date from tweet text."""
        # Simple implementation - in production, use date parsing
        try:
            return datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        except:
            return datetime.now() + timedelta(days=7)
    
    def _categorize_event(self, text: str) -> str:
        """Categorize event based on text content."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["tech", "programming", "coding", "software"]):
            return "Technology & IT"
        elif any(word in text_lower for word in ["business", "networking", "startup"]):
            return "Business & Networking"
        elif any(word in text_lower for word in ["music", "concert", "festival"]):
            return "Music & Entertainment"
        elif any(word in text_lower for word in ["art", "culture", "exhibition"]):
            return "Arts & Culture"
        else:
            return "Community & Social"
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract hashtags and keywords as tags."""
        tags = []
        
        # Extract hashtags
        words = text.split()
        for word in words:
            if word.startswith("#"):
                tags.append(word[1:].lower())
        
        # Add category-based tags
        text_lower = text.lower()
        if "tech" in text_lower:
            tags.append("technology")
        if "networking" in text_lower:
            tags.append("networking")
        if "startup" in text_lower:
            tags.append("startup")
        
        return list(set(tags))  # Remove duplicates
