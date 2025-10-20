#!/usr/bin/env python3
"""
Comprehensive test to verify all components needed for the AI Event Scraper application.
This will test every single dependency and component before attempting to run the main app.
"""

import sys
import os
import time
import json
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

print("🚀 ============================================")
print("🚀 COMPREHENSIVE AI EVENT SCRAPER TEST")
print("🚀 ============================================")

# Test results tracking
test_results = {
    "environment": {},
    "python_modules": {},
    "file_system": {},
    "network": {},
    "database": {},
    "application": {}
}

def log_test(category, test_name, success, message="", details=None):
    """Log test results with consistent formatting."""
    status = "✅" if success else "❌"
    print(f"{status} {category.upper()}: {test_name}")
    if message:
        print(f"   📝 {message}")
    if details:
        print(f"   📋 {details}")
    
    test_results[category][test_name] = {
        "success": success,
        "message": message,
        "details": details
    }

def test_environment():
    """Test basic environment setup."""
    print("\n🔍 Testing Environment Setup")
    print("=" * 50)
    
    # Python version
    python_version = sys.version
    log_test("environment", "Python Version", True, f"Python {python_version.split()[0]}")
    
    # Working directory
    cwd = os.getcwd()
    expected_cwd = "/app"
    cwd_ok = cwd == expected_cwd
    log_test("environment", "Working Directory", cwd_ok, 
             f"Current: {cwd}, Expected: {expected_cwd}")
    
    # Port environment variable
    port = os.getenv("PORT", "NOT_SET")
    port_ok = port != "NOT_SET" and port.isdigit()
    log_test("environment", "PORT Environment", port_ok, 
             f"PORT: {port}")
    
    # PYTHONPATH
    pythonpath = os.getenv("PYTHONPATH", "NOT_SET")
    pythonpath_ok = pythonpath != "NOT_SET"
    log_test("environment", "PYTHONPATH", pythonpath_ok, 
             f"PYTHONPATH: {pythonpath}")
    
    # User
    user = os.getenv("USER", "unknown")
    log_test("environment", "User", True, f"Running as: {user}")
    
    # Environment type
    env_type = os.getenv("ENVIRONMENT", "development")
    log_test("environment", "Environment Type", True, f"Environment: {env_type}")

def test_python_modules():
    """Test all required Python modules."""
    print("\n🔍 Testing Python Modules")
    print("=" * 50)
    
    # Core modules (should always be available)
    core_modules = [
        ("sys", "System"),
        ("os", "Operating System"),
        ("json", "JSON"),
        ("time", "Time"),
        ("pathlib", "Path"),
        ("http.server", "HTTP Server"),
        ("traceback", "Traceback"),
    ]
    
    for module_name, description in core_modules:
        try:
            __import__(module_name)
            log_test("python_modules", f"Core: {description}", True, module_name)
        except ImportError as e:
            log_test("python_modules", f"Core: {description}", False, 
                     f"Failed to import {module_name}", str(e))
    
    # Critical application modules
    critical_modules = [
        ("fastapi", "FastAPI Framework"),
        ("uvicorn", "ASGI Server"),
        ("motor", "MongoDB Async Driver"),
        ("pymongo", "MongoDB Driver"),
        ("aiohttp", "Async HTTP Client"),
        ("bs4", "HTML Parser (BeautifulSoup)"),
        ("fake_useragent", "User-Agent Generator"),
        ("pydantic", "Data Validation"),
        ("pydantic_settings", "Settings Management"),
        ("openai", "OpenAI API Client"),
    ]
    
    for module_name, description in critical_modules:
        try:
            __import__(module_name)
            log_test("python_modules", f"Critical: {description}", True, module_name)
        except ImportError as e:
            log_test("python_modules", f"Critical: {description}", False, 
                     f"Failed to import {module_name}", str(e))
    
    # Optional modules
    optional_modules = [
        ("atoma", "RSS Parser"),
        ("icalendar", "iCal Parser"),
        ("selenium", "Selenium WebDriver"),
        ("playwright", "Playwright"),
        ("undetected_chromedriver", "Undetected ChromeDriver"),
        ("requests_html", "Requests HTML"),
        ("geopy", "Geocoding"),
        ("dateutil", "Date Utilities"),
        ("pytz", "Timezone Utilities"),
        ("lxml", "XML/HTML Parser"),
    ]
    
    for module_name, description in optional_modules:
        try:
            __import__(module_name)
            log_test("python_modules", f"Optional: {description}", True, module_name)
        except ImportError as e:
            log_test("python_modules", f"Optional: {description}", False, 
                     f"Failed to import {module_name}", str(e))

def test_file_system():
    """Test file system access and required files."""
    print("\n🔍 Testing File System")
    print("=" * 50)
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    log_test("file_system", "Current Directory", True, str(current_dir))
    
    # Check for key files
    key_files = [
        "requirements-railway.txt",
        "railway_complete.py",
        "startup.py",
        "src/__init__.py",
        "src/core/__init__.py",
        "src/core/models.py",
        "src/core/database.py",
        "src/scrapers/__init__.py",
        "src/scrapers/enhanced_scraper_manager.py",
        "src/utils/dependency_installer.py",
    ]
    
    for file_path in key_files:
        path = Path(file_path)
        exists = path.exists()
        log_test("file_system", f"File: {file_path}", exists, 
                 "EXISTS" if exists else "MISSING")
    
    # Check for directories
    key_dirs = [
        "src",
        "src/core",
        "src/scrapers",
        "src/utils",
        "src/ai",
        "src/api",
        "src/worker",
    ]
    
    for dir_path in key_dirs:
        path = Path(dir_path)
        exists = path.exists() and path.is_dir()
        log_test("file_system", f"Directory: {dir_path}", exists, 
                 "EXISTS" if exists else "MISSING")
    
    # Check Python path
    python_paths = sys.path
    log_test("file_system", "Python Path", True, f"Found {len(python_paths)} paths")
    for i, path in enumerate(python_paths[:5]):  # Show first 5
        log_test("file_system", f"Python Path {i+1}", True, path)

def test_network():
    """Test network connectivity."""
    print("\n🔍 Testing Network Connectivity")
    print("=" * 50)
    
    # Test basic HTTP server creation
    try:
        from http.server import HTTPServer, BaseHTTPRequestHandler
        server = HTTPServer(('0.0.0.0', 8080), BaseHTTPRequestHandler)
        server.server_close()
        log_test("network", "HTTP Server Creation", True, "Can create HTTP server")
    except Exception as e:
        log_test("network", "HTTP Server Creation", False, 
                 "Failed to create HTTP server", str(e))
    
    # Test if we can bind to the port
    port = int(os.getenv("PORT", 8080))
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', port))
        sock.close()
        log_test("network", "Port Binding", True, f"Can bind to port {port}")
    except Exception as e:
        log_test("network", "Port Binding", False, 
                 f"Cannot bind to port {port}", str(e))

def test_database():
    """Test database connectivity."""
    print("\n🔍 Testing Database Connectivity")
    print("=" * 50)
    
    # Check MongoDB URI
    mongodb_uri = os.getenv("MONGODB_URI", "NOT_SET")
    uri_ok = mongodb_uri != "NOT_SET" and "mongodb://" in mongodb_uri
    log_test("database", "MongoDB URI", uri_ok, 
             f"URI: {mongodb_uri[:30]}..." if mongodb_uri != "NOT_SET" else "NOT_SET")
    
    # Test motor import and basic connection
    try:
        import motor.motor_asyncio
        log_test("database", "Motor Import", True, "Motor imported successfully")
        
        # Try to create a client (don't actually connect)
        client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
        log_test("database", "Motor Client Creation", True, "Can create Motor client")
    except Exception as e:
        log_test("database", "Motor Import/Client", False, 
                 "Failed to import or create Motor client", str(e))
    
    # Test pymongo
    try:
        import pymongo
        log_test("database", "PyMongo Import", True, "PyMongo imported successfully")
    except Exception as e:
        log_test("database", "PyMongo Import", False, 
                 "Failed to import PyMongo", str(e))

def test_application():
    """Test application-specific components."""
    print("\n🔍 Testing Application Components")
    print("=" * 50)
    
    # Add src to Python path
    src_path = Path("src")
    if src_path.exists():
        sys.path.insert(0, str(src_path))
        log_test("application", "Python Path Setup", True, "Added src to Python path")
    else:
        log_test("application", "Python Path Setup", False, "src directory not found")
    
    # Test core models import
    try:
        from core.models import Event, Location, ContactInfo, EventSource
        log_test("application", "Core Models Import", True, "All core models imported")
    except Exception as e:
        log_test("application", "Core Models Import", False, 
                 "Failed to import core models", str(e))
    
    # Test database module import
    try:
        from core.database import get_database, connect_to_database
        log_test("application", "Database Module Import", True, "Database module imported")
    except Exception as e:
        log_test("application", "Database Module Import", False, 
                 "Failed to import database module", str(e))
    
    # Test scraper manager import
    try:
        from scrapers.enhanced_scraper_manager import EnhancedScraperManager
        log_test("application", "Scraper Manager Import", True, "Scraper manager imported")
    except Exception as e:
        log_test("application", "Scraper Manager Import", False, 
                 "Failed to import scraper manager", str(e))
    
    # Test dependency installer import
    try:
        from utils.dependency_installer import ensure_dependencies
        log_test("application", "Dependency Installer Import", True, "Dependency installer imported")
    except Exception as e:
        log_test("application", "Dependency Installer Import", False, 
                 "Failed to import dependency installer", str(e))
    
    # Test main application import
    try:
        import railway_complete
        log_test("application", "Main App Import", True, "railway_complete imported")
    except Exception as e:
        log_test("application", "Main App Import", False, 
                 "Failed to import railway_complete", str(e))

def print_summary():
    """Print test summary."""
    print("\n📊 ============================================")
    print("📊 TEST SUMMARY")
    print("📊 ============================================")
    
    total_tests = 0
    passed_tests = 0
    
    for category, tests in test_results.items():
        if not tests:
            continue
            
        category_passed = sum(1 for test in tests.values() if test["success"])
        category_total = len(tests)
        total_tests += category_total
        passed_tests += category_passed
        
        status = "✅" if category_passed == category_total else "⚠️" if category_passed > 0 else "❌"
        print(f"{status} {category.upper()}: {category_passed}/{category_total} tests passed")
    
    print(f"\n🎯 OVERALL: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Application should be ready to run.")
    elif passed_tests > total_tests * 0.8:
        print("⚠️ Most tests passed. Application might work with some limitations.")
    else:
        print("❌ Many tests failed. Application will likely not work properly.")

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "ok", 
                "message": "comprehensive test server", 
                "timestamp": time.time(),
                "test_results": test_results
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "message": "comprehensive test server is running",
                "timestamp": time.time()
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "running",
                "message": "comprehensive test server",
                "timestamp": time.time(),
                "endpoints": ["/ping", "/health", "/"]
            }
            self.wfile.write(json.dumps(response, indent=2).encode())

def main():
    """Run all tests and start server."""
    try:
        # Run all tests
        test_environment()
        test_python_modules()
        test_file_system()
        test_network()
        test_database()
        test_application()
        
        # Print summary
        print_summary()
        
        # Start server
        port = int(os.getenv("PORT", 8080))
        host = "0.0.0.0"
        
        print(f"\n🌐 Starting comprehensive test server on {host}:{port}")
        print("🔍 Endpoints:")
        print("   - GET /ping - Health check with test results")
        print("   - GET /health - Simple health check")
        print("   - GET / - Server info")
        
        server = HTTPServer((host, port), TestHandler)
        print("✅ Server started successfully!")
        print("🚀 Server is ready and accepting connections!")
        print("📊 All test results are available at /ping endpoint")
        
        server.serve_forever()
        
    except Exception as e:
        print(f"❌ Critical Error: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
