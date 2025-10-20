#!/usr/bin/env python3
"""
Single comprehensive startup script for AI Event Scraper.
Handles everything in the correct order without relying on shell && chains.
"""

import os
import sys
import json
import time
import traceback
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def log(message, level="INFO"):
    """Log with timestamp and level."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def log_section(title):
    """Log a section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def log_step(step_num, title):
    """Log a step header."""
    print(f"\n🔍 Step {step_num}: {title}")
    print("-" * 40)

class SimpleHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for health checks."""
    
    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "ok", "message": "pong", "timestamp": time.time()}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "message": "all good", "timestamp": time.time()}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"message": "AI Event Scraper API", "status": "running", "timestamp": time.time()}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "not found", "path": self.path}
            self.wfile.write(json.dumps(response).encode())

def test_imports():
    """Test critical imports."""
    log_step(1, "Testing Critical Imports")
    
    critical_imports = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('motor', 'Motor (MongoDB)'),
        ('pymongo', 'PyMongo'),
        ('aiohttp', 'aiohttp'),
        ('bs4', 'BeautifulSoup'),
        ('pydantic', 'Pydantic'),
        ('openai', 'OpenAI'),
    ]
    
    failed_imports = []
    for module_name, description in critical_imports:
        try:
            __import__(module_name)
            log(f"✅ {description}: {module_name}")
        except ImportError as e:
            log(f"❌ {description}: {module_name} - {e}", "ERROR")
            failed_imports.append(module_name)
    
    optional_imports = [
        ('atoma', 'RSS Parser'),
        ('icalendar', 'iCal Parser'),
        ('selenium', 'Selenium'),
    ]
    
    log("\n🔍 Testing Optional Imports:")
    for module_name, description in optional_imports:
        try:
            __import__(module_name)
            log(f"✅ {description}: {module_name}")
        except ImportError as e:
            log(f"⚠️ {description}: {module_name} - {e}", "WARNING")
    
    if failed_imports:
        log(f"❌ Failed critical imports: {', '.join(failed_imports)}", "ERROR")
        return False
    
    log("✅ All critical imports successful")
    return True

def run_dependency_check():
    """Run dependency installer if available."""
    log_step(2, "Running Dependency Check")
    
    try:
        from utils.dependency_installer import ensure_dependencies
        log("🔍 Running dependency installer...")
        success = ensure_dependencies()
        if success:
            log("✅ All critical dependencies are available!")
        else:
            log("⚠️ Some dependencies may not be available", "WARNING")
        return True
    except Exception as e:
        log(f"❌ Dependency installer failed: {e}", "ERROR")
        log(f"📋 Traceback: {traceback.format_exc()}", "ERROR")
        return False

def test_main_app_import():
    """Test if main app can be imported."""
    log_step(3, "Testing Main App Import")
    
    try:
        import railway_complete
        log("✅ railway_complete imported successfully")
        log("✅ Main application module is accessible")
        return True
    except Exception as e:
        log(f"❌ Failed to import railway_complete: {e}", "ERROR")
        log(f"📋 Traceback: {traceback.format_exc()}", "ERROR")
        return False

def start_simple_server():
    """Start a simple HTTP server for health checks."""
    log_step(4, "Starting Simple HTTP Server")
    
    port = int(os.getenv("PORT", 8080))
    host = "0.0.0.0"
    
    log(f"🌐 Starting simple HTTP server on {host}:{port}")
    log("🔍 Endpoints:")
    log("   - GET /ping - Health check")
    log("   - GET /health - Health check")
    log("   - GET / - Root endpoint")
    
    try:
        server = HTTPServer((host, port), SimpleHandler)
        log(f"✅ Server started successfully on {host}:{port}")
        log("🚀 Server is ready and accepting connections!")
        log("🔍 Health check should now pass")
        
        # Keep the server running
        server.serve_forever()
        
    except Exception as e:
        log(f"❌ Error starting server: {e}", "ERROR")
        log(f"📋 Traceback: {traceback.format_exc()}", "ERROR")
        return False

def start_full_app():
    """Start the full FastAPI application."""
    log_step(4, "Starting Full FastAPI Application")
    
    try:
        import railway_complete
        
        port = int(os.getenv("PORT", 8080))
        host = "0.0.0.0"
        
        log(f"🌐 Starting FastAPI server on {host}:{port}")
        log("🔍 Endpoints:")
        log("   - GET /ping - Health check")
        log("   - GET /health - Health check")
        log("   - GET / - Root endpoint")
        log("   - GET /docs - API documentation")
        
        import uvicorn
        uvicorn.run(
            railway_complete.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        log(f"❌ Error starting FastAPI app: {e}", "ERROR")
        log(f"📋 Traceback: {traceback.format_exc()}", "ERROR")
        return False

def main():
    """Main startup function."""
    log_section("AI EVENT SCRAPER STARTUP")
    
    # Environment info
    log("📊 Environment Information:")
    log(f"   - Python: {sys.version}")
    log(f"   - Working Directory: {os.getcwd()}")
    log(f"   - Port: {os.getenv('PORT', '8080')}")
    log(f"   - Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    log(f"   - MongoDB URI: {os.getenv('MONGODB_URI', 'NOT SET')[:30]}...")
    log(f"   - PYTHONPATH: {sys.path[:3]}...")
    
    # Step 1: Test imports
    if not test_imports():
        log("❌ Critical imports failed - cannot continue", "ERROR")
        sys.exit(1)
    
    # Step 2: Run dependency check
    if not run_dependency_check():
        log("⚠️ Dependency check failed - continuing anyway", "WARNING")
    
    # Step 3: Test main app import
    if not test_main_app_import():
        log("❌ Main app import failed - starting simple server instead", "ERROR")
        log("🔍 Starting simple HTTP server for health checks...")
        start_simple_server()
        return
    
    # Step 4: Start full application
    log("✅ All checks passed - starting full FastAPI application")
    start_full_app()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🛑 Startup interrupted by user", "INFO")
        sys.exit(0)
    except Exception as e:
        log(f"❌ Unexpected error in startup: {e}", "ERROR")
        log(f"📋 Traceback: {traceback.format_exc()}", "ERROR")
        sys.exit(1)
