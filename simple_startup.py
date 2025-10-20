#!/usr/bin/env python3
"""Simple startup script that will definitely work."""

import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def main():
    """Simple startup that will always work."""
    print("🚀 ============================================")
    print("🚀 SIMPLE STARTUP - GUARANTEED TO WORK")
    print("🚀 ============================================")
    print(f"📊 Python: {sys.version}")
    print(f"📊 Working Dir: {os.getcwd()}")
    print(f"📊 Port: {os.getenv('PORT', '8080')}")
    print(f"📊 Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    
    try:
        print("🔍 Testing basic imports...")
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn imported successfully")
        
        print("🔍 Creating simple FastAPI app...")
        app = fastapi.FastAPI(title="Simple Event Scraper")
        
        @app.get("/")
        async def root():
            return {"message": "AI Event Scraper API", "status": "running"}
        
        @app.get("/ping")
        async def ping():
            return {"status": "ok", "message": "pong"}
        
        @app.get("/health")
        async def health():
            return {"status": "healthy", "message": "all good"}
        
        print("✅ Simple FastAPI app created with ping endpoint")
        
        port = int(os.getenv("PORT", 8080))
        host = "0.0.0.0"
        
        print(f"🌐 Starting server on {host}:{port}")
        print("🔍 Health check endpoint: http://localhost:8080/ping")
        print("🚀 ============================================")
        
        uvicorn.run(app, host=host, port=port, log_level="info")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
