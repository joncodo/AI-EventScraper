#!/usr/bin/env python3
"""
Railway-Fixed Server with Proper Database Connection

This version fixes the Railway deployment issues:
1. Proper environment variable handling
2. Fixed database connection
3. Graceful error handling
4. Railway-optimized startup
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Event Scraper API",
    description="A comprehensive REST API for accessing event data",
    version="1.0.0"
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
db_instance = None

def get_mongodb_uri():
    """Get MongoDB URI from Railway environment variables."""
    # Railway provides MONGODB_URI directly
    mongodb_uri = os.getenv("MONGODB_URI")
    
    if mongodb_uri:
        logger.info("✅ Found MONGODB_URI from Railway")
        return mongodb_uri
    
    # Fallback to prefixed environment variable
    mongodb_uri = os.getenv("EVENT_SCRAPER_MONGODB_URI")
    if mongodb_uri:
        logger.info("✅ Found EVENT_SCRAPER_MONGODB_URI")
        return mongodb_uri
    
    # Fallback to local development
    mongodb_uri = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    logger.info(f"⚠️ Using fallback MongoDB URI: {mongodb_uri}")
    return mongodb_uri

async def connect_to_database():
    """Connect to MongoDB with proper error handling."""
    global db_connected, db_instance
    
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        
        mongodb_uri = get_mongodb_uri()
        database_name = os.getenv("MONGODB_DATABASE", "event_scraper")
        
        logger.info(f"🔗 Connecting to MongoDB: {database_name}")
        
        # Create client
        client = AsyncIOMotorClient(mongodb_uri)
        db_instance = client[database_name]
        
        # Test connection
        await client.admin.command('ping')
        logger.info("✅ Database connected successfully")
        
        db_connected = True
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        db_connected = False
        return False

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    global db_connected
    logger.info("🚀 Starting AI Event Scraper API Server")
    
    # Try to connect to database (non-blocking)
    await connect_to_database()
    
    if db_connected:
        logger.info("✅ Server started with database connection")
    else:
        logger.info("⚠️ Server started without database connection")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    if db_connected and db_instance:
        try:
            db_instance.client.close()
            logger.info("✅ Database disconnected")
        except Exception as e:
            logger.error(f"❌ Error disconnecting from database: {e}")
    
    logger.info("🛑 API Server shutdown complete")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Event Scraper API",
        "version": "1.0.0",
        "status": "running",
        "database_connected": db_connected,
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown"),
        "docs": "/docs",
        "endpoints": {
            "ping": "/ping",
            "health": "/health",
            "events": "/events",
            "stats": "/stats"
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
    """Health check endpoint."""
    try:
        uptime = (datetime.now() - app_start_time).total_seconds()
        
        health_data = {
            "status": "healthy" if db_connected else "degraded",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime,
            "database_connected": db_connected
        }
        
        if db_connected and db_instance:
            try:
                total_events = await db_instance.events.count_documents({})
                health_data["total_events"] = total_events
            except Exception as e:
                logger.error(f"Error getting event count: {e}")
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

@app.get("/events")
async def get_events(limit: int = 10, offset: int = 0):
    """Get events with optional filtering."""
    if not db_connected or not db_instance:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get events
        events = []
        async for event_doc in db_instance.events.find().skip(offset).limit(limit):
            event_doc['_id'] = str(event_doc['_id'])
            events.append(event_doc)
        
        # Get total count
        total_count = await db_instance.events.count_documents({})
        
        return {
            "events": events,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "database_connected": True
        }
        
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get database statistics."""
    if not db_connected or not db_instance:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get basic counts
        total_events = await db_instance.events.count_documents({})
        
        # Get city counts
        pipeline = [
            {"$group": {"_id": "$location.city", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        top_cities = []
        async for doc in db_instance.events.aggregate(pipeline):
            top_cities.append({"city": doc["_id"], "count": doc["count"]})
        
        # Get category counts
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        top_categories = []
        async for doc in db_instance.events.aggregate(pipeline):
            top_categories.append({"category": doc["_id"], "count": doc["count"]})
        
        return {
            "total_events": total_events,
            "top_cities": top_cities,
            "top_categories": top_categories,
            "database_connected": True
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Railway sets PORT environment variable
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    logger.info(f"🌐 Starting Railway server on {host}:{port}")
    logger.info(f"📚 Docs will be available at http://{host}:{port}/docs")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info",
        access_log=True
    )
