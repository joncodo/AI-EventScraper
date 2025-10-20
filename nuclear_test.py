#!/usr/bin/env python3
"""
NUCLEAR TEST - Maximum logging and different approach to force Railway to use latest changes.
This uses Flask instead of http.server and has aggressive logging at every step.
"""

import sys
import os
import time
import json
import traceback
from datetime import datetime

print("🚀 ============================================")
print("🚀 NUCLEAR TEST - MAXIMUM LOGGING")
print("🚀 ============================================")
print(f"📊 Timestamp: {datetime.now().isoformat()}")
print(f"📊 Python version: {sys.version}")
print(f"📊 Working directory: {os.getcwd()}")
print(f"📊 User: {os.getenv('USER', 'unknown')}")
print(f"📊 UID: {os.getuid()}")
print(f"📊 GID: {os.getgid()}")
print(f"📊 PORT: {os.getenv('PORT', '8080')}")
print(f"📊 PYTHONPATH: {os.getenv('PYTHONPATH', 'NOT_SET')}")
print("🚀 ============================================")

# Check if Flask is available
try:
    from flask import Flask, jsonify
    print("✅ Flask imported successfully")
    FLASK_AVAILABLE = True
except ImportError as e:
    print(f"❌ Flask not available: {e}")
    FLASK_AVAILABLE = False

# Check if we can create a Flask app
if FLASK_AVAILABLE:
    try:
        print("🔍 Creating Flask app...")
        app = Flask(__name__)
        print("✅ Flask app created successfully")
        
        @app.route('/ping')
        def ping():
            print(f"📡 PING request received at {datetime.now().isoformat()}")
            return jsonify({
                "status": "ok",
                "message": "nuclear test server working",
                "timestamp": time.time(),
                "datetime": datetime.now().isoformat(),
                "python_version": sys.version,
                "working_directory": os.getcwd(),
                "user": os.getenv('USER', 'unknown'),
                "uid": os.getuid(),
                "gid": os.getgid(),
                "port": os.getenv('PORT', '8080'),
                "flask_available": True
            })
        
        @app.route('/health')
        def health():
            print(f"📡 HEALTH request received at {datetime.now().isoformat()}")
            return jsonify({
                "status": "healthy",
                "message": "nuclear test server is running",
                "timestamp": time.time(),
                "datetime": datetime.now().isoformat()
            })
        
        @app.route('/')
        def root():
            print(f"📡 ROOT request received at {datetime.now().isoformat()}")
            return jsonify({
                "status": "running",
                "message": "nuclear test server",
                "timestamp": time.time(),
                "datetime": datetime.now().isoformat(),
                "endpoints": ["/ping", "/health", "/"]
            })
        
        print("✅ Flask routes defined successfully")
        
    except Exception as e:
        print(f"❌ Error creating Flask app: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        FLASK_AVAILABLE = False

# Fallback to http.server if Flask fails
if not FLASK_AVAILABLE:
    print("🔄 Falling back to http.server...")
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class NuclearHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            print(f"📡 HTTP request received: {self.path} at {datetime.now().isoformat()}")
            if self.path == '/ping':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "status": "ok",
                    "message": "nuclear test server working (http.server fallback)",
                    "timestamp": time.time(),
                    "datetime": datetime.now().isoformat(),
                    "python_version": sys.version,
                    "working_directory": os.getcwd(),
                    "user": os.getenv('USER', 'unknown'),
                    "uid": os.getuid(),
                    "gid": os.getgid(),
                    "port": os.getenv('PORT', '8080'),
                    "flask_available": False
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "status": "running",
                    "message": "nuclear test server (http.server fallback)",
                    "timestamp": time.time(),
                    "datetime": datetime.now().isoformat()
                }
                self.wfile.write(json.dumps(response).encode())

def main():
    """Start the nuclear test server."""
    print("🔍 Starting nuclear test server...")
    
    port = int(os.getenv("PORT", 8080))
    host = "0.0.0.0"
    
    print(f"🌐 Target: {host}:{port}")
    print(f"📊 Flask available: {FLASK_AVAILABLE}")
    
    try:
        if FLASK_AVAILABLE:
            print("🚀 Starting Flask server...")
            print("✅ Flask server starting...")
            print("🚀 Flask server is ready and accepting connections!")
            print("📊 Flask server will run indefinitely...")
            print(f"📡 Endpoints: http://{host}:{port}/ping, /health, /")
            
            # Run Flask app
            app.run(host=host, port=port, debug=False)
            
        else:
            print("🚀 Starting http.server fallback...")
            server = HTTPServer((host, port), NuclearHandler)
            print("✅ http.server created successfully!")
            print("🚀 http.server is ready and accepting connections!")
            print("📊 http.server will run indefinitely...")
            print(f"📡 Endpoints: http://{host}:{port}/ping, /")
            
            # Keep the server running
            server.serve_forever()
            
    except Exception as e:
        print(f"❌ Critical Error: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        print("🔄 Attempting to keep process alive for debugging...")
        
        # Keep process alive for debugging
        try:
            while True:
                print(f"🔄 Process alive at {datetime.now().isoformat()}")
                time.sleep(10)
        except KeyboardInterrupt:
            print("🛑 Process interrupted")
        except Exception as e2:
            print(f"❌ Error in keep-alive loop: {e2}")
        
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 NUCLEAR TEST STARTING...")
    main()
