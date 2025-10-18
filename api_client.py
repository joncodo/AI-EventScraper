#!/usr/bin/env python3
"""
AI Event Scraper API Client
==========================

A Python client library for the AI Event Scraper API.
Provides easy-to-use methods for interacting with the API.

Usage:
    from api_client import EventScraperAPI
    
    api = EventScraperAPI("http://localhost:8000")
    events = await api.get_events(city="New York", limit=10)
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EventScraperAPI:
    """Client for AI Event Scraper API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    raise Exception(f"API Error {response.status}: {error_text}")
                
                return await response.json()
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    # Health and Stats
    async def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return await self._request("GET", "/health")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        return await self._request("GET", "/stats")
    
    # Events
    async def get_events(
        self,
        page: int = 1,
        limit: int = 50,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        city: Optional[str] = None,
        category: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        start_date_min: Optional[datetime] = None,
        start_date_max: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        ai_processed: Optional[bool] = None,
        confidence_min: Optional[float] = None
    ) -> Dict[str, Any]:
        """Get events with filtering and pagination"""
        params = {
            "page": page,
            "limit": limit,
            "sort_by": sort_by,
            "sort_order": sort_order
        }
        
        if city:
            params["city"] = city
        if category:
            params["category"] = category
        if price_min is not None:
            params["price_min"] = price_min
        if price_max is not None:
            params["price_max"] = price_max
        if start_date_min:
            params["start_date_min"] = start_date_min.isoformat()
        if start_date_max:
            params["start_date_max"] = start_date_max.isoformat()
        if tags:
            params["tags"] = ",".join(tags)
        if ai_processed is not None:
            params["ai_processed"] = ai_processed
        if confidence_min is not None:
            params["confidence_min"] = confidence_min
        
        return await self._request("GET", "/events", params=params)
    
    async def get_event(self, event_id: str) -> Dict[str, Any]:
        """Get a specific event by ID"""
        return await self._request("GET", f"/events/{event_id}")
    
    async def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new event"""
        return await self._request("POST", "/events", json=event_data)
    
    async def update_event(self, event_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing event"""
        return await self._request("PUT", f"/events/{event_id}", json=event_data)
    
    async def delete_event(self, event_id: str) -> Dict[str, Any]:
        """Delete an event"""
        return await self._request("DELETE", f"/events/{event_id}")
    
    async def search_events(self, query: str, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """Search events by text query"""
        params = {"q": query, "page": page, "limit": limit}
        return await self._request("GET", "/events/search", params=params)
    
    async def get_random_event(self) -> Dict[str, Any]:
        """Get a random event"""
        return await self._request("GET", "/events/random")
    
    async def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent events"""
        params = {"limit": limit}
        return await self._request("GET", "/events/recent", params=params)
    
    # Metadata
    async def get_cities(self) -> List[Dict[str, Any]]:
        """Get list of all cities with event counts"""
        return await self._request("GET", "/cities")
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get list of all categories with event counts"""
        return await self._request("GET", "/categories")
    
    # Convenience methods
    async def get_events_by_city(self, city: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get events for a specific city"""
        result = await self.get_events(city=city, limit=limit)
        return result["events"]
    
    async def get_events_by_category(self, category: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get events for a specific category"""
        result = await self.get_events(category=category, limit=limit)
        return result["events"]
    
    async def get_free_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get free events"""
        result = await self.get_events(price_min=0, price_max=0, limit=limit)
        return result["events"]
    
    async def get_events_by_date_range(self, start_date: datetime, end_date: datetime, limit: int = 50) -> List[Dict[str, Any]]:
        """Get events within a date range"""
        result = await self.get_events(
            start_date_min=start_date,
            start_date_max=end_date,
            limit=limit
        )
        return result["events"]
    
    async def get_high_confidence_events(self, confidence_min: float = 0.8, limit: int = 50) -> List[Dict[str, Any]]:
        """Get events with high AI confidence scores"""
        result = await self.get_events(confidence_min=confidence_min, limit=limit)
        return result["events"]

# Example usage
async def main():
    """Example usage of the API client"""
    async with EventScraperAPI("http://localhost:8000") as api:
        # Health check
        health = await api.health_check()
        print(f"API Status: {health['status']}")
        print(f"Total Events: {health['total_events']:,}")
        
        # Get statistics
        stats = await api.get_statistics()
        print(f"\n📊 Statistics:")
        print(f"Total Events: {stats['total_events']:,}")
        print(f"Total Cities: {stats['total_cities']}")
        print(f"AI Processing Rate: {stats['ai_processing_rate']}%")
        
        # Get recent events
        print(f"\n🆕 Recent Events:")
        recent = await api.get_recent_events(5)
        for event in recent:
            print(f"  - {event['title']} ({event['location']['city']})")
        
        # Search events
        print(f"\n🔍 Search Results for 'tech':")
        search_results = await api.search_events("tech", limit=3)
        for event in search_results["events"]:
            print(f"  - {event['title']} ({event['category']})")
        
        # Get events by city
        print(f"\n🏙️ Events in New York:")
        ny_events = await api.get_events_by_city("New York", limit=3)
        for event in ny_events:
            print(f"  - {event['title']} ({event['start_date']})")
        
        # Get free events
        print(f"\n💰 Free Events:")
        free_events = await api.get_free_events(3)
        for event in free_events:
            print(f"  - {event['title']} ({event['location']['city']})")

if __name__ == "__main__":
    asyncio.run(main())
