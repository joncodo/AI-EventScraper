#!/usr/bin/env python3
"""
Test the /ping endpoint to debug Railway deployment issues
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime

# Create a minimal FastAPI app to test
app = FastAPI()

@app.get("/ping")
async def ping():
    """Simple ping endpoint for basic health checks"""
    return {"status": "ok", "timestamp": datetime.now()}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AI Event Scraper API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    
    print("🧪 Testing /ping endpoint...")
    
    # Test with TestClient
    client = TestClient(app)
    
    # Test ping endpoint
    response = client.get("/ping")
    print(f"Ping response: {response.status_code} - {response.json()}")
    
    # Test root endpoint
    response = client.get("/")
    print(f"Root response: {response.status_code} - {response.json()}")
    
    print("✅ All tests passed!")
    print("🚀 Starting server on port 8000...")
    
    # Start server
    uvicorn.run(app, host="0.0.0.0", port=8000)
