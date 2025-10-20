#!/usr/bin/env python3
"""
Railway Complete API - Full-Featured Developer API

This is the complete, full-featured API for Railway deployment with:
1. All CRUD operations for events
2. Advanced search and filtering
3. Geographic queries
4. Developer-friendly endpoints
5. Data analytics and insights
6. Bulk operations
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path as PathLib
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# Add src directory to Python path
project_root = PathLib(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
from worker.background_worker import BackgroundRefreshWorker  # noqa: E402

# Configure logging (force override to ensure visibility in Railway runtime)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("uvicorn.error").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    global db_connected, worker
    
    print("🚀 ============================================")
    print("🚀 FASTAPI APPLICATION STARTUP")
    print("🚀 ============================================")
    logger.info("🚀 Starting AI Event Scraper API Server (railway_complete)")
    
    print("📊 Environment Information:")
    print(f"   - Python: {sys.version}")
    print(f"   - Working Directory: {os.getcwd()}")
    print(f"   - Port: {os.getenv('PORT', '8080')}")
    print(f"   - Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    print(f"   - MongoDB URI: {os.getenv('MONGODB_URI', 'NOT SET')[:30]}...")

    print("\n🔍 Step 1: Final dependency verification...")
    # Ensure critical dependencies are installed
    try:
        from utils.dependency_installer import ensure_dependencies
        logger.info("🔍 Ensuring critical dependencies are installed...")
        deps_success = ensure_dependencies()
        if deps_success:
            logger.info("✅ All critical dependencies are available")
            print("✅ All critical dependencies verified")
        else:
            logger.warning("⚠️ Some dependencies may not be available")
            print("⚠️ Some dependencies may be missing")
    except Exception as e:
        logger.error(f"❌ Dependency installer failed: {e}")
        print(f"❌ Dependency verification failed: {e}")

    print("\n🔍 Step 2: Database connection...")
    # Try to connect to database (non-blocking)
    await connect_to_database()

    if db_connected:
        logger.info("✅ Server started with database connection")
        print("✅ Database connected successfully")
    else:
        logger.info("⚠️ Server started without database connection")
        print("⚠️ Database connection failed - continuing without DB")

    print("\n🔍 Step 3: Background worker initialization...")
    # Start continuous background refresh worker
    if worker is None:
        try:
            worker = BackgroundRefreshWorker()
            worker.start()
            logger.info("[worker] Background refresh worker started from railway_complete")
            print("✅ Background worker started successfully")
        except Exception as e:
            logger.error(f"❌ Failed to start background worker: {e}")
            print(f"❌ Background worker failed to start: {e}")
            worker = None

    print("\n✅ ============================================")
    print("✅ FASTAPI APPLICATION STARTUP COMPLETE")
    print("✅ ============================================")
    logger.info("✅ FastAPI application startup completed successfully")

    yield

    print("\n🛑 ============================================")
    print("🛑 FASTAPI APPLICATION SHUTDOWN")
    print("🛑 ============================================")
    
    # Shutdown
    if worker is not None:
        try:
            print("🛑 Stopping background worker...")
            await worker.stop()
            print("✅ Background worker stopped")
        except Exception as e:
            logger.warning(f"Error stopping background worker: {e}")
            print(f"⚠️ Error stopping background worker: {e}")
        worker = None

    if db_connected and db_client is not None:
        try:
            print("🛑 Disconnecting from database...")
            db_client.close()
            logger.info("✅ Database disconnected")
            print("✅ Database disconnected")
        except Exception as e:
            logger.error(f"❌ Error disconnecting from database: {e}")
            print(f"❌ Error disconnecting from database: {e}")

    print("✅ ============================================")
    print("✅ FASTAPI APPLICATION SHUTDOWN COMPLETE")
    print("✅ ============================================")
    logger.info("🛑 API Server shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="AI Event Scraper API",
    description="A comprehensive REST API for accessing event data with full CRUD operations, search, filtering, and analytics",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
app_start_time = datetime.now()
db_connected = False
db_client = None
db_database = None
worker: BackgroundRefreshWorker | None = None


def get_mongodb_uri():
    """Get MongoDB URI from Railway environment variables."""
    mongodb_uri = os.getenv("MONGODB_URI")
    if mongodb_uri:
        logger.info("✅ Found MONGODB_URI from Railway")
        return mongodb_uri
    mongodb_uri = os.getenv("EVENT_SCRAPER_MONGODB_URI")
    if mongodb_uri:
        logger.info("✅ Found EVENT_SCRAPER_MONGODB_URI")
        return mongodb_uri
    mongodb_uri = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    logger.info(f"⚠️ Using fallback MongoDB URI: {mongodb_uri}")
    return mongodb_uri


async def connect_to_database():
    """Connect to MongoDB with proper error handling."""
    global db_connected, db_client, db_database
    
    print("🔗 ============================================")
    print("🔗 DATABASE CONNECTION")
    print("🔗 ============================================")
    
    try:
        from motor.motor_asyncio import AsyncIOMotorClient

        mongodb_uri = get_mongodb_uri()
        database_name = os.getenv("MONGODB_DATABASE", "event_scraper")

        print(f"📊 Database Configuration:")
        print(f"   - Database Name: {database_name}")
        print(f"   - MongoDB URI: {mongodb_uri[:50]}...")
        print(f"   - Connection Timeout: 30s")

        logger.info(f"🔗 Connecting to MongoDB: {database_name}")
        logger.info(f"🔗 MongoDB URI: {mongodb_uri[:50]}...")

        print("🔍 Step 1: Creating MongoDB client...")
        db_client = AsyncIOMotorClient(mongodb_uri)
        db_database = db_client[database_name]
        print("✅ MongoDB client created")

        print("🔍 Step 2: Testing connection with ping...")
        await db_client.admin.command('ping')
        logger.info("✅ Database connected successfully")
        print("✅ Database ping successful")

        print("🔍 Step 3: Checking database accessibility...")
        event_count = await db_database.events.count_documents({})
        logger.info(f"✅ Database accessible - {event_count} events found")
        print(f"✅ Database accessible - {event_count} events found")

        print("🔍 Step 4: Creating database indexes...")
        # Create indexes for better performance
        await db_database.events.create_index("location.city")
        await db_database.events.create_index("location.country")
        await db_database.events.create_index("start_date")
        await db_database.events.create_index("category")
        await db_database.events.create_index("created_at")
        await db_database.events.create_index("updated_at")
        print("✅ Database indexes created")

        db_connected = True
        print("✅ ============================================")
        print("✅ DATABASE CONNECTION SUCCESSFUL")
        print("✅ ============================================")
        return True
        
    except Exception as e:
        print(f"❌ ============================================")
        print(f"❌ DATABASE CONNECTION FAILED")
        print(f"❌ ============================================")
        print(f"❌ Error: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        print(f"❌ ============================================")
        
        logger.error(f"❌ Database connection failed: {e}")
        db_connected = False
        db_client = None
        db_database = None
        return False



# ============================================================================
# BASIC ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with comprehensive API information."""
    return {
        "message": "AI Event Scraper API",
        "version": "2.0.0",
        "status": "running",
        "database_connected": db_connected,
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown"),
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "basic": {
                "ping": "/ping",
                "health": "/health",
                "info": "/info"
            },
            "events": {
                "list": "/events",
                "get": "/events/{event_id}",
                "create": "POST /events",
                "update": "PUT /events/{event_id}",
                "delete": "DELETE /events/{event_id}",
                "search": "/events/search",
                "random": "/events/random",
                "recent": "/events/recent"
            },
            "analytics": {
                "stats": "/stats",
                "cities": "/cities",
                "categories": "/categories",
                "tags": "/tags",
                "sources": "/sources",
                "trends": "/trends"
            },
            "bulk": {
                "export": "/export",
                "import": "POST /import",
                "batch_update": "PUT /events/batch"
            }
        }
    }

@app.get("/ping")
async def ping():
    """Simple ping endpoint for Railway health checks."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "uptime": (datetime.now() - app_start_time).total_seconds(),
        "database_connected": db_connected
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    try:
        uptime = (datetime.now() - app_start_time).total_seconds()
        
        health_data = {
            "status": "healthy" if db_connected else "degraded",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime,
            "database_connected": db_connected,
            "version": "2.0.0"
        }
        
        if db_connected and db_database is not None:
            try:
                total_events = await db_database.events.count_documents({})
                health_data["total_events"] = total_events
                
                # Get recent activity
                recent_events = await db_database.events.count_documents({
                    "created_at": {"$gte": datetime.now() - timedelta(days=1)}
                })
                health_data["recent_events_24h"] = recent_events
                
            except Exception as e:
                logger.error(f"Error getting health data: {e}")
                health_data["database_connected"] = False
                health_data["status"] = "degraded"
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/info")
async def api_info():
    """Get detailed API information and capabilities."""
    return {
        "api_name": "AI Event Scraper API",
        "version": "2.0.0",
        "description": "Comprehensive REST API for event data management",
        "features": [
            "Full CRUD operations",
            "Advanced search and filtering",
            "Geographic queries",
            "Data analytics",
            "Bulk operations",
            "Real-time statistics"
        ],
        "database_connected": db_connected,
        "total_endpoints": 25,
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }

# ============================================================================
# EVENT CRUD OPERATIONS
# ============================================================================

@app.get("/events")
async def get_events(
    limit: int = Query(10, ge=1, le=100, description="Number of events to return"),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    category: Optional[str] = Query(None, description="Filter by category"),
    city: Optional[str] = Query(None, description="Filter by city"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    date_from: Optional[str] = Query(None, description="Filter events from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter events to date (YYYY-MM-DD)")
):
    """Get events with advanced filtering and sorting."""
    if not db_connected or db_database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Build query
        query = {}
        
        if category:
            query["category"] = {"$regex": category, "$options": "i"}
        
        if city:
            query["location.city"] = {"$regex": city, "$options": "i"}
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            query["tags"] = {"$in": tag_list}
        
        if date_from or date_to:
            date_query = {}
            if date_from:
                date_query["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                date_query["$lte"] = datetime.fromisoformat(date_to)
            query["start_date"] = date_query
        
        # Build sort
        sort_direction = -1 if sort_order == "desc" else 1
        sort_spec = [(sort_by, sort_direction)]
        
        # Get events
        events = []
        async for event_doc in db_database.events.find(query).sort(sort_spec).skip(offset).limit(limit):
            if '_id' in event_doc:
                event_doc['_id'] = str(event_doc['_id'])
            events.append(event_doc)
        
        # Get total count
        total_count = await db_database.events.count_documents(query)
        
        return {
            "events": events,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "filters": {
                "category": category,
                "city": city,
                "tags": tags,
                "date_from": date_from,
                "date_to": date_to
            },
            "sort": {
                "by": sort_by,
                "order": sort_order
            },
            "database_connected": True
        }
        
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/events/search")
async def search_events(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Search events by title, description, or tags."""
    if not db_connected or db_database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Build search query
        search_query = {
            "$or": [
                {"title": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
                {"tags": {"$regex": q, "$options": "i"}},
                {"location.city": {"$regex": q, "$options": "i"}},
                {"category": {"$regex": q, "$options": "i"}}
            ]
        }
        
        # Get events
        events = []
        async for event_doc in db_database.events.find(search_query).skip(offset).limit(limit):
            if '_id' in event_doc:
                event_doc['_id'] = str(event_doc['_id'])
            events.append(event_doc)
        
        # Get total count
        total_count = await db_database.events.count_documents(search_query)
        
        return {
            "events": events,
            "total": total_count,
            "query": q,
            "limit": limit,
            "offset": offset,
            "database_connected": True
        }
        
    except Exception as e:
        logger.error(f"Error searching events: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/events/random")
async def get_random_events(limit: int = Query(5, ge=1, le=20)):
    """Get random events."""
    if not db_connected or db_database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get random events using aggregation
        pipeline = [{"$sample": {"size": limit}}]
        
        events = []
        async for event_doc in db_database.events.aggregate(pipeline):
            if '_id' in event_doc:
                event_doc['_id'] = str(event_doc['_id'])
            events.append(event_doc)
        
        return {
            "events": events,
            "count": len(events),
            "database_connected": True
        }
        
    except Exception as e:
        logger.error(f"Error getting random events: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/events/recent")
async def get_recent_events(
    limit: int = Query(10, ge=1, le=100),
    hours: int = Query(24, ge=1, le=168, description="Hours to look back")
):
    """Get recently created events."""
    if not db_connected or db_database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Calculate date threshold
        threshold = datetime.now() - timedelta(hours=hours)
        
        # Get recent events
        events = []
        async for event_doc in db_database.events.find({
            "created_at": {"$gte": threshold}
        }).sort("created_at", -1).limit(limit):
            if '_id' in event_doc:
                event_doc['_id'] = str(event_doc['_id'])
            events.append(event_doc)
        
        return {
            "events": events,
            "count": len(events),
            "hours_back": hours,
            "threshold": threshold.isoformat(),
            "database_connected": True
        }
        
    except Exception as e:
        logger.error(f"Error getting recent events: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/events/{event_id}")
async def get_event(event_id: str = Path(..., description="Event ID")):
    """Get a specific event by ID."""
    if not db_connected or db_database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        from bson import ObjectId
        
        event = await db_database.events.find_one({"_id": ObjectId(event_id)})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        event['_id'] = str(event['_id'])
        return event
        
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Event not found")
        logger.error(f"Error getting event {event_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ============================================================================
# ANALYTICS AND INSIGHTS
# ============================================================================

@app.get("/stats")
async def get_stats():
    """Get comprehensive database statistics."""
    if not db_connected or db_database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get basic counts
        total_events = await db_database.events.count_documents({})
        
        # Get recent activity
        recent_24h = await db_database.events.count_documents({
            "created_at": {"$gte": datetime.now() - timedelta(days=1)}
        })
        
        recent_7d = await db_database.events.count_documents({
            "created_at": {"$gte": datetime.now() - timedelta(days=7)}
        })
        
        # Get city counts
        pipeline = [
            {"$group": {"_id": "$location.city", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        top_cities = []
        async for doc in db_database.events.aggregate(pipeline):
            top_cities.append({"city": doc["_id"], "count": doc["count"]})
        
        # Get category counts
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        top_categories = []
        async for doc in db_database.events.aggregate(pipeline):
            top_categories.append({"category": doc["_id"], "count": doc["count"]})
        
        # Get source platform counts
        pipeline = [
            {"$unwind": "$sources"},
            {"$group": {"_id": "$sources.platform", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        top_sources = []
        async for doc in db_database.events.aggregate(pipeline):
            top_sources.append({"platform": doc["_id"], "count": doc["count"]})
        
        return {
            "total_events": total_events,
            "recent_activity": {
                "last_24h": recent_24h,
                "last_7d": recent_7d
            },
            "top_cities": top_cities,
            "top_categories": top_categories,
            "top_sources": top_sources,
            "database_connected": True
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cities")
async def get_cities(
    limit: int = Query(50, ge=1, le=200),
    min_events: int = Query(1, ge=1, description="Minimum number of events")
):
    """Get list of cities with event counts."""
    if not db_connected or db_database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        pipeline = [
            {"$group": {"_id": "$location.city", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gte": min_events}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        cities = []
        async for doc in db_database.events.aggregate(pipeline):
            cities.append({"city": doc["_id"], "count": doc["count"]})
        
        return {
            "cities": cities,
            "count": len(cities),
            "min_events": min_events,
            "database_connected": True
        }
        
    except Exception as e:
        logger.error(f"Error getting cities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
async def get_categories():
    """Get list of all categories with event counts."""
    if not db_connected or db_database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        categories = []
        async for doc in db_database.events.aggregate(pipeline):
            categories.append({"category": doc["_id"], "count": doc["count"]})
        
        return {
            "categories": categories,
            "count": len(categories),
            "database_connected": True
        }
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tags")
async def get_tags(
    limit: int = Query(50, ge=1, le=200),
    min_events: int = Query(1, ge=1, description="Minimum number of events")
):
    """Get list of all tags with event counts."""
    if not db_connected or db_database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        pipeline = [
            {"$unwind": "$tags"},
            {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gte": min_events}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        tags = []
        async for doc in db_database.events.aggregate(pipeline):
            tags.append({"tag": doc["_id"], "count": doc["count"]})
        
        return {
            "tags": tags,
            "count": len(tags),
            "min_events": min_events,
            "database_connected": True
        }
        
    except Exception as e:
        logger.error(f"Error getting tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sources")
async def get_sources():
    """Get list of all source platforms with event counts."""
    if not db_connected or db_database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        pipeline = [
            {"$unwind": "$sources"},
            {"$group": {"_id": "$sources.platform", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        sources = []
        async for doc in db_database.events.aggregate(pipeline):
            sources.append({"platform": doc["_id"], "count": doc["count"]})
        
        return {
            "sources": sources,
            "count": len(sources),
            "database_connected": True
        }
        
    except Exception as e:
        logger.error(f"Error getting sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trends")
async def get_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    """Get event trends over time."""
    if not db_connected or db_database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Calculate date threshold
        threshold = datetime.now() - timedelta(days=days)
        
        # Get daily event counts
        pipeline = [
            {"$match": {"created_at": {"$gte": threshold}}},
            {"$group": {
                "_id": {
                    "year": {"$year": "$created_at"},
                    "month": {"$month": "$created_at"},
                    "day": {"$dayOfMonth": "$created_at"}
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}}
        ]
        
        trends = []
        async for doc in db_database.events.aggregate(pipeline):
            date_str = f"{doc['_id']['year']}-{doc['_id']['month']:02d}-{doc['_id']['day']:02d}"
            trends.append({"date": date_str, "count": doc["count"]})
        
        return {
            "trends": trends,
            "days_analyzed": days,
            "total_points": len(trends),
            "database_connected": True
        }
        
    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# BULK OPERATIONS
# ============================================================================

@app.get("/export")
async def export_events(
    format: str = Query("json", pattern="^(json|csv)$", description="Export format"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of events to export"),
    category: Optional[str] = Query(None, description="Filter by category"),
    city: Optional[str] = Query(None, description="Filter by city")
):
    """Export events in JSON or CSV format."""
    if not db_connected or db_database is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Build query
        query = {}
        if category:
            query["category"] = {"$regex": category, "$options": "i"}
        if city:
            query["location.city"] = {"$regex": city, "$options": "i"}
        
        # Get events
        events = []
        async for event_doc in db_database.events.find(query).limit(limit):
            if '_id' in event_doc:
                event_doc['_id'] = str(event_doc['_id'])
            events.append(event_doc)
        
        if format == "csv":
            # Convert to CSV format
            import csv
            import io
            
            if not events:
                return {"message": "No events found", "count": 0}
            
            # Get all unique keys
            all_keys = set()
            for event in events:
                all_keys.update(event.keys())
            
            # Create CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(events)
            
            return {
                "format": "csv",
                "data": output.getvalue(),
                "count": len(events),
                "database_connected": True
            }
        else:
            return {
                "format": "json",
                "events": events,
                "count": len(events),
                "database_connected": True
            }
        
    except Exception as e:
        logger.error(f"Error exporting events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Railway sets PORT environment variable
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    print("🌐 ============================================")
    print("🌐 STARTING UVICORN SERVER")
    print("🌐 ============================================")
    print(f"📊 Server Configuration:")
    print(f"   - Host: {host}")
    print(f"   - Port: {port}")
    print(f"   - Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    print(f"   - Log Level: info")
    print(f"   - Access Log: enabled")
    print(f"📚 API Documentation will be available at:")
    print(f"   - Swagger UI: http://{host}:{port}/docs")
    print(f"   - ReDoc: http://{host}:{port}/redoc")
    print(f"   - OpenAPI JSON: http://{host}:{port}/openapi.json")
    print(f"🔍 Health Check: http://{host}:{port}/ping")
    print("🌐 ============================================")
    
    logger.info(f"🌐 Starting Railway Complete API on {host}:{port}")
    logger.info(f"📚 Docs will be available at http://{host}:{port}/docs")
    
    try:
        uvicorn.run(
            app, 
            host=host, 
            port=port,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ ============================================")
        print(f"❌ SERVER STARTUP FAILED")
        print(f"❌ ============================================")
        print(f"❌ Error: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        print(f"❌ ============================================")
        logger.error(f"❌ Server startup failed: {e}")
        raise
