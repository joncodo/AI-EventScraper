#!/usr/bin/env python3
"""
Minimal test - absolutely minimal HTTP server with no imports beyond built-ins.
This will help us determine if the issue is with any imports or just the server itself.
"""

import sys
import os
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

print("🚀 ============================================")
print("🚀 MINIMAL TEST - NO IMPORTS")
print("🚀 ============================================")
print(f"📊 Python version: {sys.version}")
print(f"📊 Working directory: {os.getcwd()}")
print(f"📊 Port: {os.getenv('PORT', '8080')}")
print("🚀 ============================================")

class MinimalHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "ok", 
                "message": "minimal server working", 
                "timestamp": time.time()
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "running",
                "message": "minimal server",
                "timestamp": time.time()
            }
            self.wfile.write(json.dumps(response).encode())

def main():
    """Start the minimal server."""
    port = int(os.getenv("PORT", 8080))
    host = "0.0.0.0"
    
    print(f"🌐 Starting minimal server on {host}:{port}")
    print("✅ Server starting...")
    
    try:
        server = HTTPServer((host, port), MinimalHandler)
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
