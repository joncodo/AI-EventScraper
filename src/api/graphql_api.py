"""
GraphQL API for AI Event Scraper

Provides flexible querying capabilities for event data.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from strawberry import Schema, Query, Mutation, Field
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from ..core.database import db
from ..core.models import Event

logger = logging.getLogger(__name__)


@strawberry.type
class Location:
    """Location type for GraphQL."""
    address: str
    city: str
    state: str
    country: str
    latitude: Optional[float]
    longitude: Optional[float]
    venue_name: str


@strawberry.type
class ContactInfo:
    """Contact info type for GraphQL."""
    email: str
    phone: str
    website: str


@strawberry.type
class EventSource:
    """Event source type for GraphQL."""
    platform: str
    url: str
    scraped_at: datetime


@strawberry.type
class EventType:
    """Event type for GraphQL."""
    id: str
    title: str
    description: str
    start_date: datetime
    end_date: Optional[datetime]
    location: Location
    contact_info: ContactInfo
    price: str
    category: str
    tags: List[str]
    sources: List[EventSource]
    ai_processed: bool
    confidence_score: float
    created_at: datetime
    updated_at: datetime


@strawberry.type
class EventStats:
    """Event statistics type for GraphQL."""
    total_events: int
    total_cities: int
    total_categories: int
    top_cities: List[Dict[str, Any]]
    top_categories: List[Dict[str, Any]]


@strawberry.input
class EventFilter:
    """Event filter input for GraphQL."""
    city: Optional[str] = None
    category: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    ai_processed: Optional[bool] = None


@strawberry.input
class EventSearch:
    """Event search input for GraphQL."""
    query: str
    limit: int = 10
    offset: int = 0


class EventQuery:
    """GraphQL queries for events."""
    
    @strawberry.field
    async def events(
        self,
        info: Info,
        filter: Optional[EventFilter] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[EventType]:
        """Get events with optional filtering."""
        try:
            # Build MongoDB query
            query = {}
            
            if filter:
                if filter.city:
                    query["location.city"] = filter.city
                if filter.category:
                    query["category"] = filter.category
                if filter.price_min is not None or filter.price_max is not None:
                    price_query = {}
                    if filter.price_min is not None:
                        price_query["$gte"] = filter.price_min
                    if filter.price_max is not None:
                        price_query["$lte"] = filter.price_max
                    query["price"] = price_query
                if filter.start_date:
                    query["start_date"] = {"$gte": filter.start_date}
                if filter.end_date:
                    query["end_date"] = {"$lte": filter.end_date}
                if filter.tags:
                    query["tags"] = {"$in": filter.tags}
                if filter.ai_processed is not None:
                    query["ai_processed"] = filter.ai_processed
            
            # Execute query
            cursor = db.db.events.find(query).skip(offset).limit(limit)
            events = []
            
            async for event_doc in cursor:
                event = self._convert_to_event_type(event_doc)
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Error in events query: {e}")
            return []
    
    @strawberry.field
    async def event(self, info: Info, id: str) -> Optional[EventType]:
        """Get a single event by ID."""
        try:
            from bson import ObjectId
            event_doc = await db.db.events.find_one({"_id": ObjectId(id)})
            
            if event_doc:
                return self._convert_to_event_type(event_doc)
            return None
            
        except Exception as e:
            logger.error(f"Error in event query: {e}")
            return None
    
    @strawberry.field
    async def search_events(
        self,
        info: Info,
        search: EventSearch
    ) -> List[EventType]:
        """Search events by text query."""
        try:
            # Build text search query
            query = {
                "$text": {"$search": search.query}
            }
            
            # Execute search
            cursor = db.db.events.find(query).skip(search.offset).limit(search.limit)
            events = []
            
            async for event_doc in cursor:
                event = self._convert_to_event_type(event_doc)
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Error in search_events query: {e}")
            return []
    
    @strawberry.field
    async def random_event(self, info: Info) -> Optional[EventType]:
        """Get a random event."""
        try:
            # Get random event using aggregation
            pipeline = [{"$sample": {"size": 1}}]
            cursor = db.db.events.aggregate(pipeline)
            
            async for event_doc in cursor:
                return self._convert_to_event_type(event_doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Error in random_event query: {e}")
            return None
    
    @strawberry.field
    async def event_stats(self, info: Info) -> EventStats:
        """Get event statistics."""
        try:
            # Get basic counts
            total_events = await db.db.events.count_documents({})
            
            # Get unique cities count
            cities_pipeline = [
                {"$group": {"_id": "$location.city"}},
                {"$count": "total"}
            ]
            cities_result = await db.db.events.aggregate(cities_pipeline).to_list(1)
            total_cities = cities_result[0]["total"] if cities_result else 0
            
            # Get unique categories count
            categories_pipeline = [
                {"$group": {"_id": "$category"}},
                {"$count": "total"}
            ]
            categories_result = await db.db.events.aggregate(categories_pipeline).to_list(1)
            total_categories = categories_result[0]["total"] if categories_result else 0
            
            # Get top cities
            top_cities_pipeline = [
                {"$group": {"_id": "$location.city", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            top_cities = []
            async for doc in db.db.events.aggregate(top_cities_pipeline):
                top_cities.append({"city": doc["_id"], "count": doc["count"]})
            
            # Get top categories
            top_categories_pipeline = [
                {"$group": {"_id": "$category", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            top_categories = []
            async for doc in db.db.events.aggregate(top_categories_pipeline):
                top_categories.append({"category": doc["_id"], "count": doc["count"]})
            
            return EventStats(
                total_events=total_events,
                total_cities=total_cities,
                total_categories=total_categories,
                top_cities=top_cities,
                top_categories=top_categories
            )
            
        except Exception as e:
            logger.error(f"Error in event_stats query: {e}")
            return EventStats(
                total_events=0,
                total_cities=0,
                total_categories=0,
                top_cities=[],
                top_categories=[]
            )
    
    def _convert_to_event_type(self, event_doc: Dict[str, Any]) -> EventType:
        """Convert MongoDB document to GraphQL EventType."""
        return EventType(
            id=str(event_doc["_id"]),
            title=event_doc.get("title", ""),
            description=event_doc.get("description", ""),
            start_date=event_doc.get("start_date", datetime.now()),
            end_date=event_doc.get("end_date"),
            location=Location(
                address=event_doc.get("location", {}).get("address", ""),
                city=event_doc.get("location", {}).get("city", ""),
                state=event_doc.get("location", {}).get("state", ""),
                country=event_doc.get("location", {}).get("country", ""),
                latitude=event_doc.get("location", {}).get("latitude"),
                longitude=event_doc.get("location", {}).get("longitude"),
                venue_name=event_doc.get("location", {}).get("venue_name", "")
            ),
            contact_info=ContactInfo(
                email=event_doc.get("contact_info", {}).get("email", ""),
                phone=event_doc.get("contact_info", {}).get("phone", ""),
                website=event_doc.get("contact_info", {}).get("website", "")
            ),
            price=event_doc.get("price", ""),
            category=event_doc.get("category", ""),
            tags=event_doc.get("tags", []),
            sources=[
                EventSource(
                    platform=source.get("platform", ""),
                    url=source.get("url", ""),
                    scraped_at=source.get("scraped_at", datetime.now())
                )
                for source in event_doc.get("sources", [])
            ],
            ai_processed=event_doc.get("ai_processed", False),
            confidence_score=event_doc.get("confidence_score", 0.0),
            created_at=event_doc.get("created_at", datetime.now()),
            updated_at=event_doc.get("updated_at", datetime.now())
        )


# Create GraphQL schema
schema = Schema(query=EventQuery)

# Create GraphQL router for FastAPI
graphql_router = GraphQLRouter(schema, path="/graphql")
