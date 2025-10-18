"""
Enhanced AI Event Categorization System

Improved categorization using better prompts and multi-step analysis.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import openai
from dataclasses import dataclass

from ..core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class CategorizationResult:
    """Result of event categorization."""
    category: str
    subcategory: str
    tags: List[str]
    confidence: float
    reasoning: str
    price_range: str
    target_audience: str


class EnhancedEventCategorizer:
    """Enhanced AI-powered event categorization system."""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4"  # Use GPT-4 for better categorization
        
        # Enhanced category taxonomy
        self.categories = {
            "Technology & IT": {
                "subcategories": [
                    "Software Development", "Data Science", "AI/ML", "Cybersecurity",
                    "Web Development", "Mobile Development", "DevOps", "Cloud Computing"
                ],
                "keywords": ["tech", "programming", "coding", "software", "data", "ai", "ml", "cyber", "web", "mobile", "devops", "cloud"]
            },
            "Business & Networking": {
                "subcategories": [
                    "Startup Events", "Networking", "Entrepreneurship", "Investment",
                    "Business Development", "Sales & Marketing", "Leadership", "Consulting"
                ],
                "keywords": ["business", "startup", "entrepreneur", "networking", "investment", "sales", "marketing", "leadership"]
            },
            "Education & Training": {
                "subcategories": [
                    "Workshops", "Seminars", "Courses", "Certifications",
                    "Professional Development", "Skills Training", "Academic", "Research"
                ],
                "keywords": ["education", "training", "workshop", "seminar", "course", "certification", "learning", "academic"]
            },
            "Arts & Culture": {
                "subcategories": [
                    "Visual Arts", "Performing Arts", "Museums", "Galleries",
                    "Literature", "Film", "Photography", "Design"
                ],
                "keywords": ["art", "culture", "museum", "gallery", "theater", "film", "photography", "design", "literature"]
            },
            "Music & Entertainment": {
                "subcategories": [
                    "Concerts", "Festivals", "Live Music", "DJ Events",
                    "Comedy", "Theater", "Dance", "Nightlife"
                ],
                "keywords": ["music", "concert", "festival", "dj", "comedy", "theater", "dance", "nightlife", "entertainment"]
            },
            "Health & Wellness": {
                "subcategories": [
                    "Fitness", "Yoga", "Meditation", "Mental Health",
                    "Nutrition", "Wellness", "Sports", "Outdoor Activities"
                ],
                "keywords": ["health", "wellness", "fitness", "yoga", "meditation", "sports", "nutrition", "mental health"]
            },
            "Food & Drink": {
                "subcategories": [
                    "Restaurants", "Bars", "Food Festivals", "Wine Tasting",
                    "Cooking Classes", "Breweries", "Food Trucks", "Culinary"
                ],
                "keywords": ["food", "drink", "restaurant", "bar", "wine", "beer", "cooking", "culinary", "festival"]
            },
            "Community & Social": {
                "subcategories": [
                    "Meetups", "Social Events", "Volunteering", "Charity",
                    "Community", "Local Events", "Family", "Religious"
                ],
                "keywords": ["community", "social", "meetup", "volunteer", "charity", "local", "family", "religious"]
            },
            "Professional Development": {
                "subcategories": [
                    "Career Development", "Industry Events", "Conferences", "Seminars",
                    "Training", "Certifications", "Mentoring", "Coaching"
                ],
                "keywords": ["career", "professional", "industry", "conference", "mentoring", "coaching", "development"]
            }
        }
    
    async def categorize_event(self, event: Dict[str, Any]) -> CategorizationResult:
        """Categorize an event using enhanced AI analysis."""
        try:
            # Step 1: Basic categorization
            basic_result = await self._basic_categorization(event)
            
            # Step 2: Detailed analysis
            detailed_result = await self._detailed_analysis(event, basic_result)
            
            # Step 3: Validation and refinement
            final_result = await self._validate_and_refine(event, detailed_result)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error categorizing event: {e}")
            return self._fallback_categorization(event)
    
    async def _basic_categorization(self, event: Dict[str, Any]) -> CategorizationResult:
        """Perform basic categorization using AI."""
        try:
            title = event.get("title", "")
            description = event.get("description", "")
            location = event.get("location", {})
            venue = location.get("venue_name", "")
            
            prompt = f"""
            Analyze this event and categorize it accurately:

            Title: {title}
            Description: {description}
            Venue: {venue}
            City: {location.get('city', '')}

            Available categories:
            {self._format_categories()}

            Provide your analysis in this exact format:
            CATEGORY: [primary category]
            SUBCATEGORY: [specific subcategory]
            CONFIDENCE: [0.0-1.0]
            REASONING: [brief explanation]
            TAGS: [comma-separated relevant tags]
            PRICE_RANGE: [Free, $, $$, $$$, $$$$]
            AUDIENCE: [target audience description]
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert event categorization system. Analyze events accurately and provide detailed categorization."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content
            
            return self._parse_categorization_response(result_text)
            
        except Exception as e:
            logger.error(f"Error in basic categorization: {e}")
            return self._fallback_categorization(event)
    
    async def _detailed_analysis(self, event: Dict[str, Any], basic_result: CategorizationResult) -> CategorizationResult:
        """Perform detailed analysis for complex events."""
        try:
            # Check if event needs detailed analysis
            if basic_result.confidence >= 0.9:
                return basic_result
            
            title = event.get("title", "")
            description = event.get("description", "")
            
            prompt = f"""
            Perform detailed analysis of this event for better categorization:

            Title: {title}
            Description: {description}
            
            Current categorization:
            Category: {basic_result.category}
            Confidence: {basic_result.confidence}
            Reasoning: {basic_result.reasoning}

            Analyze the event more deeply and provide:
            1. Is the current category correct?
            2. What are the key themes and topics?
            3. Who is the target audience?
            4. What is the event format and style?
            5. Any special characteristics?

            Provide your analysis in this exact format:
            CATEGORY: [refined category]
            SUBCATEGORY: [specific subcategory]
            CONFIDENCE: [0.0-1.0]
            REASONING: [detailed explanation]
            TAGS: [comma-separated relevant tags]
            PRICE_RANGE: [Free, $, $$, $$$, $$$$]
            AUDIENCE: [target audience description]
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert event analyst. Provide detailed, accurate categorization with high confidence."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=600
            )
            
            result_text = response.choices[0].message.content
            
            return self._parse_categorization_response(result_text)
            
        except Exception as e:
            logger.error(f"Error in detailed analysis: {e}")
            return basic_result
    
    async def _validate_and_refine(self, event: Dict[str, Any], result: CategorizationResult) -> CategorizationResult:
        """Validate and refine the categorization result."""
        try:
            # Validate category exists
            if result.category not in self.categories:
                result.category = "Other"
                result.confidence = min(result.confidence, 0.7)
            
            # Validate subcategory
            if result.subcategory not in self.categories.get(result.category, {}).get("subcategories", []):
                # Find closest subcategory
                result.subcategory = self._find_closest_subcategory(result.category, result.subcategory)
            
            # Enhance tags
            result.tags = self._enhance_tags(result.tags, result.category)
            
            # Adjust confidence based on validation
            if result.category == "Other":
                result.confidence = min(result.confidence, 0.6)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in validation and refinement: {e}")
            return result
    
    def _format_categories(self) -> str:
        """Format categories for AI prompt."""
        formatted = ""
        for category, details in self.categories.items():
            formatted += f"\n{category}:\n"
            for subcategory in details["subcategories"]:
                formatted += f"  - {subcategory}\n"
        return formatted
    
    def _parse_categorization_response(self, response: str) -> CategorizationResult:
        """Parse AI response into CategorizationResult."""
        try:
            lines = response.strip().split('\n')
            result = CategorizationResult(
                category="Other",
                subcategory="General",
                tags=[],
                confidence=0.5,
                reasoning="",
                price_range="Free",
                target_audience="General"
            )
            
            for line in lines:
                if line.startswith("CATEGORY:"):
                    result.category = line.split(":", 1)[1].strip()
                elif line.startswith("SUBCATEGORY:"):
                    result.subcategory = line.split(":", 1)[1].strip()
                elif line.startswith("CONFIDENCE:"):
                    try:
                        result.confidence = float(line.split(":", 1)[1].strip())
                    except:
                        result.confidence = 0.5
                elif line.startswith("REASONING:"):
                    result.reasoning = line.split(":", 1)[1].strip()
                elif line.startswith("TAGS:"):
                    tags_text = line.split(":", 1)[1].strip()
                    result.tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
                elif line.startswith("PRICE_RANGE:"):
                    result.price_range = line.split(":", 1)[1].strip()
                elif line.startswith("AUDIENCE:"):
                    result.target_audience = line.split(":", 1)[1].strip()
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing categorization response: {e}")
            return self._fallback_categorization({})
    
    def _find_closest_subcategory(self, category: str, subcategory: str) -> str:
        """Find the closest subcategory for a given category."""
        available_subcategories = self.categories.get(category, {}).get("subcategories", [])
        
        if not available_subcategories:
            return "General"
        
        # Simple string matching for now
        subcategory_lower = subcategory.lower()
        for available in available_subcategories:
            if subcategory_lower in available.lower() or available.lower() in subcategory_lower:
                return available
        
        return available_subcategories[0]  # Return first available
    
    def _enhance_tags(self, tags: List[str], category: str) -> List[str]:
        """Enhance tags with category-specific keywords."""
        enhanced_tags = list(tags)
        
        # Add category-specific keywords
        category_keywords = self.categories.get(category, {}).get("keywords", [])
        for keyword in category_keywords[:3]:  # Add top 3 keywords
            if keyword not in enhanced_tags:
                enhanced_tags.append(keyword)
        
        return enhanced_tags[:10]  # Limit to 10 tags
    
    def _fallback_categorization(self, event: Dict[str, Any]) -> CategorizationResult:
        """Fallback categorization when AI fails."""
        title = event.get("title", "").lower()
        description = event.get("description", "").lower()
        content = f"{title} {description}"
        
        # Simple keyword-based categorization
        for category, details in self.categories.items():
            for keyword in details["keywords"]:
                if keyword in content:
                    return CategorizationResult(
                        category=category,
                        subcategory=details["subcategories"][0],
                        tags=[keyword],
                        confidence=0.6,
                        reasoning=f"Fallback categorization based on keyword: {keyword}",
                        price_range="Free",
                        target_audience="General"
                    )
        
        return CategorizationResult(
            category="Other",
            subcategory="General",
            tags=["event"],
            confidence=0.3,
            reasoning="Fallback categorization - unable to determine category",
            price_range="Free",
            target_audience="General"
        )
    
    async def batch_categorize_events(self, events: List[Dict[str, Any]]) -> List[CategorizationResult]:
        """Categorize multiple events in batch."""
        try:
            results = []
            
            # Process events in parallel (with rate limiting)
            semaphore = asyncio.Semaphore(5)  # Limit concurrent requests
            
            async def categorize_single(event):
                async with semaphore:
                    return await self.categorize_event(event)
            
            tasks = [categorize_single(event) for event in events]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error categorizing event {i}: {result}")
                    processed_results.append(self._fallback_categorization(events[i]))
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in batch categorization: {e}")
            return [self._fallback_categorization(event) for event in events]
