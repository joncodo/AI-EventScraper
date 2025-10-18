#!/usr/bin/env python3
"""
Ultra-Simple Railway Server

Minimal server designed specifically for Railway deployment.
No database dependencies, just basic endpoints.
"""

import os
import logging
from datetime import datetime
from fastapi import FastAPI
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="AI Event Scraper API")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Event Scraper API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown")
    }

@app.get("/ping")
async def ping():
    """Ping endpoint for Railway health checks."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "port": os.getenv("PORT", "8000")
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running"
    }

if __name__ == "__main__":
    # Railway sets PORT environment variable
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    logger.info(f"🚀 Starting Railway server on {host}:{port}")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info",
        access_log=True
    )
