#!/usr/bin/env python3
"""
Railway-Optimized API Server

Simplified version for Railway deployment with proper error handling.
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

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    global db_connected
    logger.info("🚀 Starting AI Event Scraper API Server")
    
    try:
        # Try to connect to database (optional for Railway)
        from core.database import db
        await db.connect()
        db_connected = True
        logger.info("✅ Database connected successfully")
    except Exception as e:
        logger.warning(f"⚠️ Database connection failed: {e}")
        logger.info("🔄 Continuing without database connection")
        db_connected = False

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    if db_connected:
        try:
            from core.database import db
            await db.disconnect()
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
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "ping": "/ping",
            "health": "/health",
            "events": "/events",
            "search": "/events/search",
            "stats": "/stats"
        }
    }

@app.get("/ping")
async def ping():
    """Simple ping endpoint for Railway health checks."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "uptime": (datetime.now() - app_start_time).total_seconds()
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
        
        if db_connected:
            try:
                from core.database import db
                total_events = await db.db.events.count_documents({})
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
    if not db_connected:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        from core.database import db
        
        # Get events
        events = []
        async for event_doc in db.db.events.find().skip(offset).limit(limit):
            event_doc['_id'] = str(event_doc['_id'])
            events.append(event_doc)
        
        # Get total count
        total_count = await db.db.events.count_documents({})
        
        return {
            "events": events,
            "total": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get database statistics."""
    if not db_connected:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        from core.database import db
        
        # Get basic counts
        total_events = await db.db.events.count_documents({})
        
        # Get city counts
        pipeline = [
            {"$group": {"_id": "$location.city", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        top_cities = []
        async for doc in db.db.events.aggregate(pipeline):
            top_cities.append({"city": doc["_id"], "count": doc["count"]})
        
        # Get category counts
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        top_categories = []
        async for doc in db.db.events.aggregate(pipeline):
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
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    logger.info(f"🌐 Starting server on {host}:{port}")
    logger.info(f"📚 Docs will be available at http://{host}:{port}/docs")
    
    uvicorn.run(app, host=host, port=port, log_level="info")
