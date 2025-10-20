#!/usr/bin/env python3
"""Basic test to verify Python can run in the container."""

import sys
import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

print("🚀 ============================================")
print("🚀 BASIC PYTHON TEST")
print("🚀 ============================================")
print(f"📊 Python version: {sys.version}")
print(f"📊 Working directory: {os.getcwd()}")
print(f"📊 Port: {os.getenv('PORT', '8080')}")
print(f"📊 User: {os.getenv('USER', 'unknown')}")
print("🚀 ============================================")

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "ok", "message": "pong", "timestamp": time.time()}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "running", "message": "basic test server", "timestamp": time.time()}
            self.wfile.write(json.dumps(response).encode())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    host = "0.0.0.0"
    
    print(f"🌐 Starting basic test server on {host}:{port}")
    print("🔍 Endpoints: /ping, /")
    
    try:
        server = HTTPServer((host, port), TestHandler)
        print("✅ Server started successfully!")
        print("🚀 Server is ready and accepting connections!")
        server.serve_forever()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        sys.exit(1)
