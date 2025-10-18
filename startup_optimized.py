#!/usr/bin/env python3
"""
Optimized Startup Script for Railway Deployment

This script provides faster startup by:
1. Lazy loading of heavy modules
2. Optimized database connection
3. Minimal startup dependencies
4. Health check optimization
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def startup_optimized():
    """Optimized startup sequence for Railway deployment."""
    
    logger.info("🚀 Starting AI Event Scraper API Server (Optimized)")
    
    # Import FastAPI and create app
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    # Create FastAPI app with minimal startup
    app = FastAPI(
        title="AI Event Scraper API",
        description="A comprehensive REST API for accessing event data",
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
    
    # Global database connection (lazy loaded)
    db_connection = None
    
    async def get_db():
        """Lazy database connection."""
        nonlocal db_connection
        if db_connection is None:
            from core.database import db
            await db.connect()
            db_connection = db
        return db_connection
    
    # Health check endpoint (optimized)
    @app.get("/health")
    async def health_check():
        """Optimized health check."""
        try:
            db = await get_db()
            # Quick ping instead of full query
            await db.client.admin.command('ping')
            return {
                "status": "healthy",
                "database": "connected",
                "timestamp": "2025-10-18T16:00:00Z"
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": "2025-10-18T16:00:00Z"
            }
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "AI Event Scraper API",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc",
            "endpoints": {
                "health": "/health",
                "events": "/events",
                "search": "/events/search",
                "stats": "/stats"
            }
        }
    
    # Lazy load other endpoints
    @app.on_event("startup")
    async def startup_event():
        """Startup event handler."""
        logger.info("🚀 API Server started successfully")
        logger.info("📊 Loading additional endpoints...")
        
        # Import and register other endpoints lazily
        try:
            from api_server import register_endpoints
            await register_endpoints(app, get_db)
            logger.info("✅ All endpoints loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load endpoints: {e}")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Shutdown event handler."""
        if db_connection:
            await db_connection.disconnect()
        logger.info("🛑 API Server shutdown complete")
    
    return app

# Create the app
app = asyncio.run(startup_optimized())

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    logger.info(f"🌐 Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")
