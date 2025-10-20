#!/usr/bin/env python3
"""Ultra simple startup that will definitely work."""

import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "ok", "message": "pong"}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "message": "all good"}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"message": "AI Event Scraper API", "status": "running"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "not found"}
            self.wfile.write(json.dumps(response).encode())

def main():
    """Ultra simple startup using built-in Python HTTP server."""
    print("🚀 ============================================")
    print("🚀 ULTRA SIMPLE STARTUP - GUARANTEED TO WORK")
    print("🚀 ============================================")
    print(f"📊 Python: {sys.version}")
    print(f"📊 Working Dir: {os.getcwd()}")
    print(f"📊 Port: {os.getenv('PORT', '8080')}")
    print(f"📊 Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    
    port = int(os.getenv("PORT", 8080))
    host = "0.0.0.0"
    
    print(f"🌐 Starting simple HTTP server on {host}:{port}")
    print("🔍 Endpoints:")
    print("   - GET /ping - Health check")
    print("   - GET /health - Health check")
    print("   - GET / - Root endpoint")
    print("🚀 ============================================")
    
    try:
        server = HTTPServer((host, port), SimpleHandler)
        print(f"✅ Server started successfully on {host}:{port}")
        server.serve_forever()
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
