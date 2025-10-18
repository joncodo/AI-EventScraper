"""Database connection and operations for the AI Event Scraper."""
import asyncio
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from datetime import datetime
import logging
from bson import ObjectId

from .config import settings
from .models import Event, QueryRequest

logger = logging.getLogger(__name__)


class Database:
    """Database connection and operations manager."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self):
        """Connect to MongoDB."""
        try:
            # Use mongodb_uri if available (for cloud deployments), otherwise use mongodb_url
            connection_string = settings.mongodb_uri or settings.mongodb_url
            self.client = AsyncIOMotorClient(connection_string)
            self.db = self.client[settings.mongodb_database]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
            
            # Create indexes
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create database indexes for better performance."""
        if self.db is None:
            return
            
        collection = self.db.events
        
        # Create indexes
        indexes = [
            ("location.city", ASCENDING),
            ("location.country", ASCENDING),
            ("start_date", ASCENDING),
            ("category", ASCENDING),
            ("tags", ASCENDING),
            ("created_at", DESCENDING),
            ("updated_at", DESCENDING),
        ]
        
        for index_spec in indexes:
            try:
                await collection.create_index(index_spec)
            except Exception as e:
                logger.warning(f"Failed to create index {list(index_spec)}: {e}")
    
    async def insert_event(self, event: Event) -> str:
        """Insert a new event into the database."""
        if self.db is None:
            raise RuntimeError("Database not connected")
        
        event_dict = event.dict(by_alias=True)
        result = await self.db.events.insert_one(event_dict)
        return str(result.inserted_id)
    
    async def insert_events(self, events: List[Event]) -> List[str]:
        """Insert multiple events into the database."""
        if self.db is None:
            raise RuntimeError("Database not connected")
        
        event_dicts = [event.dict(by_alias=True) for event in events]
        result = await self.db.events.insert_many(event_dicts)
        return [str(id) for id in result.inserted_ids]
    
    async def find_events(self, query_request: QueryRequest) -> List[Event]:
        """Find events based on query criteria."""
        if self.db is None:
            raise RuntimeError("Database not connected")
        
        # Build MongoDB query
        mongo_query = {}
        
        if query_request.city:
            mongo_query["location.city"] = {"$regex": query_request.city, "$options": "i"}
        
        if query_request.country:
            mongo_query["location.country"] = {"$regex": query_request.country, "$options": "i"}
        
        if query_request.start_date:
            mongo_query["start_date"] = {"$gte": query_request.start_date}
        
        if query_request.end_date:
            if "start_date" in mongo_query:
                mongo_query["start_date"]["$lte"] = query_request.end_date
            else:
                mongo_query["start_date"] = {"$lte": query_request.end_date}
        
        if query_request.category:
            mongo_query["category"] = {"$regex": query_request.category, "$options": "i"}
        
        if query_request.tags:
            mongo_query["tags"] = {"$in": query_request.tags}
        
        # Execute query
        cursor = self.db.events.find(mongo_query).skip(query_request.offset).limit(query_request.limit)
        events = []
        
        async for doc in cursor:
            events.append(Event(**doc))
        
        return events
    
    async def find_duplicate_events(self, event: Event, similarity_threshold: float = 0.8) -> List[Event]:
        """Find potential duplicate events using various criteria."""
        if self.db is None:
            raise RuntimeError("Database not connected")
        
        # Build query for potential duplicates
        query = {
            "title": {"$regex": event.title, "$options": "i"},
            "start_date": {
                "$gte": event.start_date.replace(hour=0, minute=0, second=0),
                "$lte": event.start_date.replace(hour=23, minute=59, second=59)
            },
            "location.city": {"$regex": event.location.city, "$options": "i"}
        }
        
        cursor = self.db.events.find(query)
        potential_duplicates = []
        
        async for doc in cursor:
            potential_duplicates.append(Event(**doc))
        
        return potential_duplicates
    
    async def update_event(self, event_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an event in the database."""
        if self.db is None:
            raise RuntimeError("Database not connected")
        
        update_data["updated_at"] = datetime.utcnow()
        result = await self.db.events.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    async def delete_event(self, event_id: str) -> bool:
        """Delete an event from the database."""
        if self.db is None:
            raise RuntimeError("Database not connected")
        
        result = await self.db.events.delete_one({"_id": ObjectId(event_id)})
        return result.deleted_count > 0
    
    async def get_event_count(self, query_request: QueryRequest) -> int:
        """Get the count of events matching the query criteria."""
        if self.db is None:
            raise RuntimeError("Database not connected")
        
        # Build the same query as find_events
        mongo_query = {}
        
        if query_request.city:
            mongo_query["location.city"] = {"$regex": query_request.city, "$options": "i"}
        
        if query_request.country:
            mongo_query["location.country"] = {"$regex": query_request.country, "$options": "i"}
        
        if query_request.start_date:
            mongo_query["start_date"] = {"$gte": query_request.start_date}
        
        if query_request.end_date:
            if "start_date" in mongo_query:
                mongo_query["start_date"]["$lte"] = query_request.end_date
            else:
                mongo_query["start_date"] = {"$lte": query_request.end_date}
        
        if query_request.category:
            mongo_query["category"] = {"$regex": query_request.category, "$options": "i"}
        
        if query_request.tags:
            mongo_query["tags"] = {"$in": query_request.tags}
        
        return await self.db.events.count_documents(mongo_query)


# Global database instance
db = Database()
