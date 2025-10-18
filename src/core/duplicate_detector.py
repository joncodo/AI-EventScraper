"""
Advanced Duplicate Detection System

Improved algorithms for detecting and handling duplicate events.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from difflib import SequenceMatcher
import hashlib
import re
from dataclasses import dataclass

from .database import db

logger = logging.getLogger(__name__)


@dataclass
class DuplicateMatch:
    """Represents a duplicate match between events."""
    event1_id: str
    event2_id: str
    similarity_score: float
    match_type: str
    confidence: float


class AdvancedDuplicateDetector:
    """Advanced duplicate detection system."""
    
    def __init__(self):
        self.similarity_threshold = 0.8
        self.title_weight = 0.4
        self.location_weight = 0.3
        self.date_weight = 0.2
        self.description_weight = 0.1
    
    async def detect_duplicates(self, event: Dict[str, Any]) -> List[DuplicateMatch]:
        """Detect potential duplicates for a given event."""
        try:
            # Get candidate events for comparison
            candidates = await self._get_candidate_events(event)
            
            duplicates = []
            
            for candidate in candidates:
                similarity_score = await self._calculate_similarity(event, candidate)
                
                if similarity_score >= self.similarity_threshold:
                    match_type = self._determine_match_type(event, candidate, similarity_score)
                    confidence = self._calculate_confidence(event, candidate, similarity_score)
                    
                    duplicate = DuplicateMatch(
                        event1_id=str(event["_id"]),
                        event2_id=str(candidate["_id"]),
                        similarity_score=similarity_score,
                        match_type=match_type,
                        confidence=confidence
                    )
                    
                    duplicates.append(duplicate)
            
            return duplicates
            
        except Exception as e:
            logger.error(f"Error detecting duplicates: {e}")
            return []
    
    async def _get_candidate_events(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get candidate events for duplicate comparison."""
        try:
            # Build query for candidate events
            query = {}
            
            # Same city
            if event.get("location", {}).get("city"):
                query["location.city"] = event["location"]["city"]
            
            # Similar date range (±7 days)
            start_date = event.get("start_date")
            if start_date:
                if isinstance(start_date, str):
                    start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                
                date_range_start = start_date - timedelta(days=7)
                date_range_end = start_date + timedelta(days=7)
                
                query["start_date"] = {
                    "$gte": date_range_start,
                    "$lte": date_range_end
                }
            
            # Same category
            if event.get("category"):
                query["category"] = event["category"]
            
            # Exclude the event itself
            query["_id"] = {"$ne": event["_id"]}
            
            # Get candidates
            candidates = []
            async for candidate in db.db.events.find(query).limit(50):
                candidates.append(candidate)
            
            return candidates
            
        except Exception as e:
            logger.error(f"Error getting candidate events: {e}")
            return []
    
    async def _calculate_similarity(self, event1: Dict[str, Any], event2: Dict[str, Any]) -> float:
        """Calculate similarity score between two events."""
        try:
            # Title similarity
            title_sim = self._text_similarity(
                event1.get("title", ""),
                event2.get("title", "")
            )
            
            # Location similarity
            location_sim = self._location_similarity(
                event1.get("location", {}),
                event2.get("location", {})
            )
            
            # Date similarity
            date_sim = self._date_similarity(
                event1.get("start_date"),
                event2.get("start_date")
            )
            
            # Description similarity
            description_sim = self._text_similarity(
                event1.get("description", ""),
                event2.get("description", "")
            )
            
            # Calculate weighted similarity
            total_similarity = (
                title_sim * self.title_weight +
                location_sim * self.location_weight +
                date_sim * self.date_weight +
                description_sim * self.description_weight
            )
            
            return total_similarity
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using multiple methods."""
        if not text1 or not text2:
            return 0.0
        
        # Normalize text
        text1 = self._normalize_text(text1)
        text2 = self._normalize_text(text2)
        
        # Sequence matcher similarity
        seq_similarity = SequenceMatcher(None, text1, text2).ratio()
        
        # Jaccard similarity (word-based)
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        jaccard_similarity = len(intersection) / len(union) if union else 0.0
        
        # Combine similarities
        return (seq_similarity + jaccard_similarity) / 2
    
    def _location_similarity(self, location1: Dict[str, Any], location2: Dict[str, Any]) -> float:
        """Calculate location similarity."""
        if not location1 or not location2:
            return 0.0
        
        similarity = 0.0
        factors = 0
        
        # City similarity
        city1 = location1.get("city", "").lower()
        city2 = location2.get("city", "").lower()
        if city1 and city2:
            similarity += 1.0 if city1 == city2 else 0.0
            factors += 1
        
        # Venue similarity
        venue1 = location1.get("venue_name", "").lower()
        venue2 = location2.get("venue_name", "").lower()
        if venue1 and venue2:
            venue_sim = self._text_similarity(venue1, venue2)
            similarity += venue_sim
            factors += 1
        
        # Address similarity
        address1 = location1.get("address", "").lower()
        address2 = location2.get("address", "").lower()
        if address1 and address2:
            address_sim = self._text_similarity(address1, address2)
            similarity += address_sim
            factors += 1
        
        return similarity / factors if factors > 0 else 0.0
    
    def _date_similarity(self, date1: Any, date2: Any) -> float:
        """Calculate date similarity."""
        if not date1 or not date2:
            return 0.0
        
        try:
            # Convert to datetime if needed
            if isinstance(date1, str):
                date1 = datetime.fromisoformat(date1.replace('Z', '+00:00'))
            if isinstance(date2, str):
                date2 = datetime.fromisoformat(date2.replace('Z', '+00:00'))
            
            # Calculate time difference
            time_diff = abs((date1 - date2).total_seconds())
            
            # Convert to similarity score (closer dates = higher similarity)
            max_diff = 7 * 24 * 60 * 60  # 7 days in seconds
            similarity = max(0, 1 - (time_diff / max_diff))
            
            return similarity
            
        except Exception as e:
            logger.error(f"Error calculating date similarity: {e}")
            return 0.0
    
    def _determine_match_type(self, event1: Dict[str, Any], event2: Dict[str, Any], similarity: float) -> str:
        """Determine the type of duplicate match."""
        if similarity >= 0.95:
            return "exact_duplicate"
        elif similarity >= 0.9:
            return "near_duplicate"
        elif similarity >= 0.8:
            return "possible_duplicate"
        else:
            return "similar_event"
    
    def _calculate_confidence(self, event1: Dict[str, Any], event2: Dict[str, Any], similarity: float) -> float:
        """Calculate confidence score for duplicate detection."""
        confidence = similarity
        
        # Boost confidence for exact matches
        if event1.get("title", "").lower() == event2.get("title", "").lower():
            confidence += 0.1
        
        if event1.get("location", {}).get("venue_name", "").lower() == event2.get("location", {}).get("venue_name", "").lower():
            confidence += 0.1
        
        # Reduce confidence for different sources
        sources1 = {source.get("platform", "") for source in event1.get("sources", [])}
        sources2 = {source.get("platform", "") for source in event2.get("sources", [])}
        
        if sources1.intersection(sources2):
            confidence += 0.05
        
        return min(1.0, confidence)
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    async def handle_duplicates(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle duplicate detection for an event."""
        try:
            # Detect duplicates
            duplicates = await self.detect_duplicates(event)
            
            if duplicates:
                # Find the best match
                best_match = max(duplicates, key=lambda d: d.confidence)
                
                if best_match.confidence >= 0.9:
                    # Mark as duplicate
                    event["duplicate_of"] = best_match.event2_id
                    event["duplicate_confidence"] = best_match.confidence
                    event["duplicate_type"] = best_match.match_type
                    
                    logger.info(f"Event {event['_id']} marked as duplicate of {best_match.event2_id}")
                
                elif best_match.confidence >= 0.8:
                    # Flag for manual review
                    event["duplicate_review"] = True
                    event["duplicate_candidates"] = [
                        {
                            "event_id": dup.event2_id,
                            "similarity": dup.similarity_score,
                            "confidence": dup.confidence,
                            "match_type": dup.match_type
                        }
                        for dup in duplicates[:3]  # Top 3 candidates
                    ]
                    
                    logger.info(f"Event {event['_id']} flagged for duplicate review")
            
            return event
            
        except Exception as e:
            logger.error(f"Error handling duplicates: {e}")
            return event
    
    async def process_existing_duplicates(self) -> Dict[str, Any]:
        """Process existing events for duplicate detection."""
        try:
            logger.info("Starting duplicate detection for existing events...")
            
            processed_count = 0
            duplicate_count = 0
            review_count = 0
            
            # Process events in batches
            batch_size = 100
            skip = 0
            
            while True:
                events = []
                async for event in db.db.events.find().skip(skip).limit(batch_size):
                    events.append(event)
                
                if not events:
                    break
                
                for event in events:
                    # Skip if already processed
                    if event.get("duplicate_processed"):
                        continue
                    
                    # Handle duplicates
                    updated_event = await self.handle_duplicates(event)
                    
                    # Update in database
                    await db.db.events.update_one(
                        {"_id": event["_id"]},
                        {
                            "$set": {
                                "duplicate_of": updated_event.get("duplicate_of"),
                                "duplicate_confidence": updated_event.get("duplicate_confidence"),
                                "duplicate_type": updated_event.get("duplicate_type"),
                                "duplicate_review": updated_event.get("duplicate_review"),
                                "duplicate_candidates": updated_event.get("duplicate_candidates"),
                                "duplicate_processed": True,
                                "duplicate_processed_at": datetime.now()
                            }
                        }
                    )
                    
                    processed_count += 1
                    
                    if updated_event.get("duplicate_of"):
                        duplicate_count += 1
                    elif updated_event.get("duplicate_review"):
                        review_count += 1
                
                skip += batch_size
                logger.info(f"Processed {processed_count} events...")
            
            result = {
                "processed_count": processed_count,
                "duplicate_count": duplicate_count,
                "review_count": review_count,
                "processed_at": datetime.now()
            }
            
            logger.info(f"Duplicate detection complete: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing existing duplicates: {e}")
            return {"error": str(e)}
