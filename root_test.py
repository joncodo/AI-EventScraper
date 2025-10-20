#!/usr/bin/env python3
"""
Root test - run as root user to eliminate permission issues.
"""

import sys
import os
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

print("🚀 ============================================")
print("🚀 ROOT TEST - RUNNING AS ROOT USER")
print("🚀 ============================================")
print(f"📊 Python version: {sys.version}")
print(f"📊 Working directory: {os.getcwd()}")
print(f"📊 User: {os.getenv('USER', 'unknown')}")
print(f"📊 UID: {os.getuid()}")
print(f"📊 GID: {os.getgid()}")
print(f"📊 PORT: {os.getenv('PORT', '8080')}")
print("🚀 ============================================")

class RootTestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "ok", 
                "message": "root test server working", 
                "timestamp": time.time(),
                "user": os.getenv('USER', 'unknown'),
                "uid": os.getuid(),
                "gid": os.getgid(),
                "port": self.server.server_port
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "running",
                "message": "root test server",
                "timestamp": time.time(),
                "user": os.getenv('USER', 'unknown'),
                "uid": os.getuid()
            }
            self.wfile.write(json.dumps(response).encode())

def main():
    """Start the root test server."""
    port = int(os.getenv("PORT", 8080))
    host = "0.0.0.0"
    
    print(f"🌐 Starting root test server on {host}:{port}")
    print(f"👤 Running as user: {os.getenv('USER', 'unknown')} (UID: {os.getuid()})")
    print("✅ Server starting...")
    
    try:
        server = HTTPServer((host, port), RootTestHandler)
        print("✅ Server created successfully!")
        print("🚀 Server is ready and accepting connections!")
        print("📊 Server will run indefinitely...")
        
        # Keep the server running
        server.serve_forever()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
