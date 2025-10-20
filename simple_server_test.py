#!/usr/bin/env python3
"""
Simple server test - just get a basic HTTP server running with /ping endpoint.
This will help us isolate if the issue is with the comprehensive test or the server itself.
"""

import sys
import os
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

print("🚀 ============================================")
print("🚀 SIMPLE SERVER TEST")
print("🚀 ============================================")
print(f"📊 Python version: {sys.version}")
print(f"📊 Working directory: {os.getcwd()}")
print(f"📊 Port: {os.getenv('PORT', '8080')}")
print(f"📊 User: {os.getenv('USER', 'unknown')}")
print("🚀 ============================================")

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "ok", 
                "message": "pong", 
                "timestamp": time.time(),
                "python_version": sys.version,
                "working_directory": os.getcwd(),
                "port": os.getenv('PORT', '8080'),
                "user": os.getenv('USER', 'unknown')
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "message": "simple server is running",
                "timestamp": time.time()
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "running",
                "message": "simple server",
                "timestamp": time.time(),
                "endpoints": ["/ping", "/health", "/"]
            }
            self.wfile.write(json.dumps(response, indent=2).encode())

def main():
    """Start the simple server."""
    try:
        port = int(os.getenv("PORT", 8080))
        host = "0.0.0.0"
        
        print(f"🌐 Starting simple server on {host}:{port}")
        print("🔍 Endpoints:")
        print("   - GET /ping - Health check with system info")
        print("   - GET /health - Simple health check")
        print("   - GET / - Server info")
        
        server = HTTPServer((host, port), SimpleHandler)
        print("✅ Server started successfully!")
        print("🚀 Server is ready and accepting connections!")
        print("📊 Server will run indefinitely...")
        
        # Keep the server running
        server.serve_forever()
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
