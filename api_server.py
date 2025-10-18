#!/usr/bin/env python3
"""
AI Event Scraper API Server

A comprehensive REST API for accessing event data collected from multiple sources.
Provides endpoints for searching, filtering, and retrieving event information.

Features:
- Full CRUD operations for events
- Advanced search and filtering
- Geographic queries
- Real-time statistics
- Pagination and sorting
- Interactive API documentation

Usage:
    python api_server.py [--host HOST] [--port PORT] [--reload]
"""

import asyncio
import sys
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from enum import Enum

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from fastapi import FastAPI, HTTPException, Query, Path, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from bson import ObjectId
import uvicorn

from core.database import db
from core.models import Event, Location, ContactInfo, EventSource

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Event Scraper API",
    description="A comprehensive REST API for accessing event data from the AI Event Scraper database",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class EventResponse(BaseModel):
    id: str
    title: str
    description: str
    start_date: datetime
    end_date: datetime
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

class EventCreate(BaseModel):
    title: str
    description: str
    start_date: datetime
    end_date: datetime
    location: Location
    contact_info: ContactInfo
    price: str
    category: str
    tags: List[str]
    sources: List[EventSource]

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[Location] = None
    contact_info: Optional[ContactInfo] = None
    price: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    sources: Optional[List[EventSource]] = None

class SearchFilters(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    start_date_min: Optional[datetime] = None
    start_date_max: Optional[datetime] = None
    tags: Optional[List[str]] = None
    ai_processed: Optional[bool] = None
    confidence_min: Optional[float] = None

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(50, ge=1, le=1000, description="Items per page")
    sort_by: str = Field("created_at", description="Field to sort by")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")

class StatsResponse(BaseModel):
    total_events: int
    total_cities: int
    total_categories: int
    ai_processing_rate: float
    avg_confidence_score: float
    recent_events_24h: int
    top_cities: List[Dict[str, Any]]
    top_categories: List[Dict[str, Any]]
    platform_distribution: Dict[str, int]
    price_distribution: Dict[str, int]

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database_connected: bool
    total_events: int
    uptime_seconds: float

# Global variables
app_start_time = datetime.now()

# Dependency to get database connection
async def get_database():
    if not db.db:
        await db.connect()
    return db.db

# Helper functions
def convert_objectid_to_str(obj):
    """Convert ObjectId to string for JSON serialization"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    return obj

def event_doc_to_response(doc: dict) -> EventResponse:
    """Convert MongoDB document to EventResponse"""
    doc = convert_objectid_to_str(doc)
    return EventResponse(**doc)

# API Endpoints

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Event Scraper API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "events": "/events",
            "search": "/events/search",
            "stats": "/stats",
            "health": "/health",
            "cities": "/cities",
            "categories": "/categories"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        database = await get_database()
        total_events = await database.events.count_documents({})
        uptime = (datetime.now() - app_start_time).total_seconds()
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            database_connected=True,
            total_events=total_events,
            uptime_seconds=uptime
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            database_connected=False,
            total_events=0,
            uptime_seconds=(datetime.now() - app_start_time).total_seconds()
        )

@app.get("/stats", response_model=StatsResponse)
async def get_statistics():
    """Get comprehensive database statistics"""
    try:
        database = await get_database()
        
        # Basic counts
        total_events = await database.events.count_documents({})
        
        # Recent events (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_events = await database.events.count_documents({
            "created_at": {"$gte": yesterday}
        })
        
        # AI processing stats
        ai_processed = await database.events.count_documents({"ai_processed": True})
        ai_processing_rate = (ai_processed / total_events * 100) if total_events > 0 else 0
        
        # Confidence score stats
        confidence_scores = []
        async for doc in database.events.find({}, {"confidence_score": 1}):
            if "confidence_score" in doc:
                confidence_scores.append(doc["confidence_score"])
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # City counts
        city_counts = {}
        async for doc in database.events.find({}, {"location.city": 1}):
            if "location" in doc and "city" in doc["location"]:
                city = doc["location"]["city"]
                city_counts[city] = city_counts.get(city, 0) + 1
        
        top_cities = [{"city": city, "count": count} for city, count in sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
        total_cities = len(city_counts)
        
        # Category counts
        category_counts = {}
        async for doc in database.events.find({}, {"category": 1}):
            if "category" in doc:
                category = doc["category"]
                category_counts[category] = category_counts.get(category, 0) + 1
        
        top_categories = [{"category": category, "count": count} for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
        total_categories = len(category_counts)
        
        # Platform distribution
        platform_counts = {}
        async for doc in database.events.find({}, {"sources.platform": 1}):
            if "sources" in doc and doc["sources"]:
                for source in doc["sources"]:
                    if "platform" in source:
                        platform = source["platform"]
                        platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        # Price distribution
        price_distribution = {}
        async for doc in database.events.find({}, {"price": 1}):
            if "price" in doc:
                price = doc["price"]
                if price == "0" or price == 0:
                    price_distribution["Free"] = price_distribution.get("Free", 0) + 1
                elif price in ["1", "2", "3", "4", "5"]:
                    price_distribution["$1-5"] = price_distribution.get("$1-5", 0) + 1
                elif price in ["6", "7", "8", "9", "10"]:
                    price_distribution["$6-10"] = price_distribution.get("$6-10", 0) + 1
                elif price in ["11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]:
                    price_distribution["$11-20"] = price_distribution.get("$11-20", 0) + 1
                elif price in ["21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50"]:
                    price_distribution["$21-50"] = price_distribution.get("$21-50", 0) + 1
                else:
                    price_distribution["$50+"] = price_distribution.get("$50+", 0) + 1
        
        return StatsResponse(
            total_events=total_events,
            total_cities=total_cities,
            total_categories=total_categories,
            ai_processing_rate=round(ai_processing_rate, 2),
            avg_confidence_score=round(avg_confidence, 3),
            recent_events_24h=recent_events,
            top_cities=top_cities,
            top_categories=top_categories,
            platform_distribution=platform_counts,
            price_distribution=price_distribution
        )
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events", response_model=Dict[str, Any])
async def get_events(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=1000, description="Items per page"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    city: Optional[str] = Query(None, description="Filter by city"),
    category: Optional[str] = Query(None, description="Filter by category"),
    price_min: Optional[float] = Query(None, description="Minimum price"),
    price_max: Optional[float] = Query(None, description="Maximum price"),
    start_date_min: Optional[datetime] = Query(None, description="Minimum start date"),
    start_date_max: Optional[datetime] = Query(None, description="Maximum start date"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    ai_processed: Optional[bool] = Query(None, description="Filter by AI processing status"),
    confidence_min: Optional[float] = Query(None, description="Minimum confidence score")
):
    """Get events with filtering and pagination"""
    try:
        database = await get_database()
        
        # Build filter query
        filter_query = {}
        
        if city:
            filter_query["location.city"] = {"$regex": city, "$options": "i"}
        
        if category:
            filter_query["category"] = {"$regex": category, "$options": "i"}
        
        if price_min is not None or price_max is not None:
            price_filter = {}
            if price_min is not None:
                price_filter["$gte"] = str(price_min)
            if price_max is not None:
                price_filter["$lte"] = str(price_max)
            filter_query["price"] = price_filter
        
        if start_date_min or start_date_max:
            date_filter = {}
            if start_date_min:
                date_filter["$gte"] = start_date_min
            if start_date_max:
                date_filter["$lte"] = start_date_max
            filter_query["start_date"] = date_filter
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            filter_query["tags"] = {"$in": tag_list}
        
        if ai_processed is not None:
            filter_query["ai_processed"] = ai_processed
        
        if confidence_min is not None:
            filter_query["confidence_score"] = {"$gte": confidence_min}
        
        # Get total count
        total_count = await database.events.count_documents(filter_query)
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Build sort
        sort_direction = 1 if sort_order == "asc" else -1
        sort_criteria = [(sort_by, sort_direction)]
        
        # Get events
        events = []
        async for doc in database.events.find(filter_query).sort(sort_criteria).skip(skip).limit(limit):
            events.append(event_doc_to_response(doc))
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            "events": events,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            },
            "filters": {
                "city": city,
                "category": category,
                "price_min": price_min,
                "price_max": price_max,
                "start_date_min": start_date_min,
                "start_date_max": start_date_max,
                "tags": tags,
                "ai_processed": ai_processed,
                "confidence_min": confidence_min
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: str = Path(..., description="Event ID")):
    """Get a specific event by ID"""
    try:
        database = await get_database()
        
        # Validate ObjectId
        try:
            object_id = ObjectId(event_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid event ID format")
        
        # Find event
        doc = await database.events.find_one({"_id": object_id})
        if not doc:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return event_doc_to_response(doc)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event {event_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events", response_model=EventResponse)
async def create_event(event: EventCreate):
    """Create a new event"""
    try:
        database = await get_database()
        
        # Convert to dict and add timestamps
        event_dict = event.dict()
        event_dict["ai_processed"] = False
        event_dict["confidence_score"] = 0.0
        event_dict["created_at"] = datetime.now()
        event_dict["updated_at"] = datetime.now()
        
        # Insert event
        result = await database.events.insert_one(event_dict)
        
        # Get the created event
        doc = await database.events.find_one({"_id": result.inserted_id})
        return event_doc_to_response(doc)
        
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/events/{event_id}", response_model=EventResponse)
async def update_event(event_id: str, event_update: EventUpdate):
    """Update an existing event"""
    try:
        database = await get_database()
        
        # Validate ObjectId
        try:
            object_id = ObjectId(event_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid event ID format")
        
        # Check if event exists
        existing = await database.events.find_one({"_id": object_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Prepare update data
        update_data = {k: v for k, v in event_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.now()
        
        # Update event
        await database.events.update_one({"_id": object_id}, {"$set": update_data})
        
        # Get updated event
        doc = await database.events.find_one({"_id": object_id})
        return event_doc_to_response(doc)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating event {event_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/events/{event_id}")
async def delete_event(event_id: str):
    """Delete an event"""
    try:
        database = await get_database()
        
        # Validate ObjectId
        try:
            object_id = ObjectId(event_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid event ID format")
        
        # Delete event
        result = await database.events.delete_one({"_id": object_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return {"message": "Event deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/search", response_model=Dict[str, Any])
async def search_events(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=1000, description="Items per page")
):
    """Search events by text query"""
    try:
        database = await get_database()
        
        # Build search query
        search_query = {
            "$or": [
                {"title": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
                {"category": {"$regex": q, "$options": "i"}},
                {"tags": {"$regex": q, "$options": "i"}},
                {"location.city": {"$regex": q, "$options": "i"}},
                {"location.state": {"$regex": q, "$options": "i"}}
            ]
        }
        
        # Get total count
        total_count = await database.events.count_documents(search_query)
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Get events
        events = []
        async for doc in database.events.find(search_query).sort("created_at", -1).skip(skip).limit(limit):
            events.append(event_doc_to_response(doc))
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            "events": events,
            "query": q,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cities", response_model=List[Dict[str, Any]])
async def get_cities():
    """Get list of all cities with event counts"""
    try:
        database = await get_database()
        
        # Aggregate city counts
        pipeline = [
            {"$group": {"_id": "$location.city", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$project": {"city": "$_id", "count": 1, "_id": 0}}
        ]
        
        cities = []
        async for doc in database.events.aggregate(pipeline):
            if doc["city"]:  # Filter out null cities
                cities.append(doc)
        
        return cities
        
    except Exception as e:
        logger.error(f"Error getting cities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories", response_model=List[Dict[str, Any]])
async def get_categories():
    """Get list of all categories with event counts"""
    try:
        database = await get_database()
        
        # Aggregate category counts
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$project": {"category": "$_id", "count": 1, "_id": 0}}
        ]
        
        categories = []
        async for doc in database.events.aggregate(pipeline):
            if doc["category"]:  # Filter out null categories
                categories.append(doc)
        
        return categories
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/random", response_model=EventResponse)
async def get_random_event():
    """Get a random event"""
    try:
        database = await get_database()
        
        # Get random event
        pipeline = [{"$sample": {"size": 1}}]
        
        async for doc in database.events.aggregate(pipeline):
            return event_doc_to_response(doc)
        
        raise HTTPException(status_code=404, detail="No events found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting random event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/recent", response_model=List[EventResponse])
async def get_recent_events(
    limit: int = Query(10, ge=1, le=100, description="Number of recent events")
):
    """Get recent events"""
    try:
        database = await get_database()
        
        events = []
        async for doc in database.events.find().sort("created_at", -1).limit(limit):
            events.append(event_doc_to_response(doc))
        
        return events
        
    except Exception as e:
        logger.error(f"Error getting recent events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    try:
        await db.connect()
        logger.info("🚀 API Server started successfully")
        logger.info("📊 Connected to MongoDB")
    except Exception as e:
        logger.error(f"❌ Failed to start API server: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connection on shutdown"""
    try:
        await db.disconnect()
        logger.info("🛑 API Server shutdown complete")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Event Scraper API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    logger.info(f"🚀 Starting AI Event Scraper API Server")
    logger.info(f"🌐 Host: {args.host}")
    logger.info(f"🔌 Port: {args.port}")
    logger.info(f"📚 Docs: http://{args.host}:{args.port}/docs")
    
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
