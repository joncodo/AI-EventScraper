"""AI processing module for event data analysis and deduplication."""
import json
import os
from typing import List, Tuple
from datetime import datetime
import logging
from difflib import SequenceMatcher

from openai import AsyncOpenAI
from core.config import settings
from core.models import Event, ContactInfo

logger = logging.getLogger(__name__)


class AIProcessor:
    """AI processor for event data analysis and deduplication."""
    
    def __init__(self):
        # Try multiple environment variable names for OpenAI API key
        api_key = (
            settings.openai_api_key or 
            os.getenv("OPENAI_API_KEY") or 
            os.getenv("EVENT_SCRAPER_OPENAI_API_KEY")
        )
        
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key)
        else:
            self.client = None
            logger.warning("OpenAI API key not provided. AI features will be limited.")
    
    async def process_event(self, event: Event) -> Event:
        """Process an event with AI to enhance and validate data."""
        try:
            # Enhance event data with AI
            enhanced_event = await self._enhance_event_data(event)
            
            # Categorize the event
            enhanced_event.category = await self._categorize_event(enhanced_event)
            
            # Extract and enhance tags
            enhanced_event.tags = await self._extract_tags(enhanced_event)
            
            # Validate and clean contact information
            enhanced_event.contact_info = await self._process_contact_info(enhanced_event.contact_info)
            
            # Mark as AI processed
            enhanced_event.ai_processed = True
            
            return enhanced_event
            
        except Exception as e:
            logger.error(f"Error processing event with AI: {e}")
            return event
    
    async def _enhance_event_data(self, event: Event) -> Event:
        """Enhance event data using AI."""
        if not self.client:
            return event
        
        try:
            prompt = f"""
            Analyze and enhance the following event data. Return a JSON response with enhanced information:
            
            Event Title: {event.title}
            Description: {event.description or 'No description'}
            Location: {event.location.city}, {event.location.country}
            Start Date: {event.start_date}
            
            Please provide:
            1. A cleaned and standardized title
            2. An enhanced description (if the original is poor or missing)
            3. Suggested category
            4. Relevant tags
            5. Confidence score (0-1) for the data quality
            
            Return only valid JSON in this format:
            {{
                "title": "enhanced title",
                "description": "enhanced description",
                "category": "category name",
                "tags": ["tag1", "tag2", "tag3"],
                "confidence_score": 0.85
            }}
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Update event with AI enhancements
            if result.get("title"):
                event.title = result["title"]
            if result.get("description"):
                event.description = result["description"]
            if result.get("confidence_score"):
                event.confidence_score = result["confidence_score"]
            
            return event
            
        except Exception as e:
            logger.error(f"Error enhancing event data: {e}")
            return event
    
    async def _categorize_event(self, event: Event) -> str:
        """Categorize an event using AI."""
        if not self.client:
            return self._simple_categorize(event)
        
        try:
            prompt = f"""
            Categorize this event into one of these categories:
            - Business & Networking
            - Technology & IT
            - Arts & Culture
            - Sports & Fitness
            - Education & Training
            - Food & Drink
            - Music & Entertainment
            - Health & Wellness
            - Community & Social
            - Professional Development
            - Other
            
            Event: {event.title}
            Description: {event.description or 'No description'}
            Location: {event.location.city}, {event.location.country}
            
            Return only the category name.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error categorizing event: {e}")
            return self._simple_categorize(event)
    
    def _simple_categorize(self, event: Event) -> str:
        """Simple rule-based categorization as fallback."""
        title_lower = event.title.lower()
        description_lower = (event.description or "").lower()
        text = f"{title_lower} {description_lower}"
        
        if any(word in text for word in ["tech", "software", "programming", "coding", "ai", "data"]):
            return "Technology & IT"
        elif any(word in text for word in ["business", "networking", "startup", "entrepreneur"]):
            return "Business & Networking"
        elif any(word in text for word in ["music", "concert", "band", "dj"]):
            return "Music & Entertainment"
        elif any(word in text for word in ["art", "gallery", "museum", "culture"]):
            return "Arts & Culture"
        elif any(word in text for word in ["sport", "fitness", "gym", "running", "yoga"]):
            return "Sports & Fitness"
        elif any(word in text for word in ["food", "restaurant", "cooking", "wine", "beer"]):
            return "Food & Drink"
        elif any(word in text for word in ["education", "course", "training", "workshop", "seminar"]):
            return "Education & Training"
        elif any(word in text for word in ["health", "wellness", "medical", "therapy"]):
            return "Health & Wellness"
        else:
            return "Other"
    
    async def _extract_tags(self, event: Event) -> List[str]:
        """Extract relevant tags from event data."""
        if not self.client:
            return self._simple_extract_tags(event)
        
        try:
            prompt = f"""
            Extract 3-5 relevant tags for this event. Return them as a JSON array of strings.
            
            Event: {event.title}
            Description: {event.description or 'No description'}
            Category: {event.category or 'Unknown'}
            
            Focus on:
            - Event type/format
            - Target audience
            - Key topics
            - Industry/sector
            
            Return only a JSON array like: ["tag1", "tag2", "tag3"]
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result if isinstance(result, list) else []
            
        except Exception as e:
            logger.error(f"Error extracting tags: {e}")
            return self._simple_extract_tags(event)
    
    def _simple_extract_tags(self, event: Event) -> List[str]:
        """Simple tag extraction as fallback."""
        tags = []
        text = f"{event.title} {event.description or ''}".lower()
        
        # Common event types
        if any(word in text for word in ["meetup", "meeting"]):
            tags.append("meetup")
        if any(word in text for word in ["conference", "summit"]):
            tags.append("conference")
        if any(word in text for word in ["workshop", "training"]):
            tags.append("workshop")
        if any(word in text for word in ["networking", "social"]):
            tags.append("networking")
        if any(word in text for word in ["free", "no cost"]):
            tags.append("free")
        
        return tags[:5]  # Limit to 5 tags
    
    async def _process_contact_info(self, contact_info: ContactInfo) -> ContactInfo:
        """Process and validate contact information."""
        # Clean email
        if contact_info.email:
            contact_info.email = contact_info.email.strip().lower()
        
        # Clean phone
        if contact_info.phone:
            # Remove common phone formatting
            phone = contact_info.phone.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
            contact_info.phone = phone
        
        # Clean website
        if contact_info.website:
            website = contact_info.website.strip()
            if not website.startswith(("http://", "https://")):
                website = f"https://{website}"
            contact_info.website = website
        
        return contact_info
    
    def calculate_similarity(self, event1: Event, event2: Event) -> float:
        """Calculate similarity score between two events."""
        # Title similarity
        title_similarity = SequenceMatcher(None, event1.title.lower(), event2.title.lower()).ratio()
        
        # Date similarity (events on same day get higher score)
        date_diff = abs((event1.start_date - event2.start_date).total_seconds())
        date_similarity = max(0, 1 - (date_diff / (24 * 3600)))  # 1 day = 0 similarity
        
        # Location similarity
        location_similarity = 0
        if event1.location.city.lower() == event2.location.city.lower():
            location_similarity += 0.5
        if event1.location.country.lower() == event2.location.country.lower():
            location_similarity += 0.3
        if event1.location.venue_name and event2.location.venue_name:
            venue_similarity = SequenceMatcher(
                None, 
                event1.location.venue_name.lower(), 
                event2.location.venue_name.lower()
            ).ratio()
            location_similarity += venue_similarity * 0.2
        
        # Weighted average
        total_similarity = (
            title_similarity * 0.4 +
            date_similarity * 0.3 +
            location_similarity * 0.3
        )
        
        return total_similarity
    
    async def find_duplicates(self, events: List[Event], similarity_threshold: float = 0.8) -> List[Tuple[Event, Event, float]]:
        """Find duplicate events in a list."""
        duplicates = []
        
        for i in range(len(events)):
            for j in range(i + 1, len(events)):
                similarity = self.calculate_similarity(events[i], events[j])
                if similarity >= similarity_threshold:
                    duplicates.append((events[i], events[j], similarity))
        
        return duplicates
    
    async def merge_events(self, primary_event: Event, secondary_event: Event) -> Event:
        """Merge two events, keeping the primary event as base."""
        # Merge sources
        primary_event.sources.extend(secondary_event.sources)
        
        # Merge tags (avoid duplicates)
        all_tags = set(primary_event.tags + secondary_event.tags)
        primary_event.tags = list(all_tags)
        
        # Use better description if available
        if not primary_event.description and secondary_event.description:
            primary_event.description = secondary_event.description
        elif len(secondary_event.description or "") > len(primary_event.description or ""):
            primary_event.description = secondary_event.description
        
        # Use better contact info if available
        if not primary_event.contact_info.email and secondary_event.contact_info.email:
            primary_event.contact_info.email = secondary_event.contact_info.email
        if not primary_event.contact_info.website and secondary_event.contact_info.website:
            primary_event.contact_info.website = secondary_event.contact_info.website
        
        # Update timestamp
        primary_event.updated_at = datetime.utcnow()
        
        return primary_event


# Global AI processor instance
ai_processor = AIProcessor()
