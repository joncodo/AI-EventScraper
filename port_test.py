#!/usr/bin/env python3
"""
Port test - try multiple standard ports to find one that works on Railway.
"""

import sys
import os
import time
import json
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler

print("🚀 ============================================")
print("🚀 PORT TEST - TRYING MULTIPLE PORTS")
print("🚀 ============================================")
print(f"📊 Python version: {sys.version}")
print(f"📊 Working directory: {os.getcwd()}")
print(f"📊 PORT env var: {os.getenv('PORT', 'NOT_SET')}")
print("🚀 ============================================")

class PortTestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "ok", 
                "message": "port test server working", 
                "timestamp": time.time(),
                "port": self.server.server_port,
                "host": self.server.server_address[0]
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "running",
                "message": "port test server",
                "timestamp": time.time(),
                "port": self.server.server_port
            }
            self.wfile.write(json.dumps(response).encode())

def test_port(port):
    """Test if a port is available."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', port))
        sock.close()
        return True
    except:
        return False

def main():
    """Try multiple ports to find one that works."""
    
    # List of ports to try in order of preference
    ports_to_try = []
    
    # 1. Railway's PORT environment variable (highest priority)
    railway_port = os.getenv('PORT')
    if railway_port and railway_port.isdigit():
        ports_to_try.append(int(railway_port))
        print(f"🎯 Railway PORT env var: {railway_port}")
    
    # 2. Standard web app ports
    standard_ports = [3000, 5000, 8000, 8080, 9000, 4000, 6000]
    ports_to_try.extend(standard_ports)
    
    # 3. Remove duplicates while preserving order
    ports_to_try = list(dict.fromkeys(ports_to_try))
    
    print(f"🔍 Ports to try: {ports_to_try}")
    
    # Try each port
    for port in ports_to_try:
        print(f"\n🔍 Testing port {port}...")
        
        if test_port(port):
            print(f"✅ Port {port} is available!")
            
            try:
                print(f"🌐 Starting server on 0.0.0.0:{port}")
                server = HTTPServer(('0.0.0.0', port), PortTestHandler)
                print(f"✅ Server created successfully on port {port}!")
                print(f"🚀 Server is ready and accepting connections!")
                print(f"📊 Server will run indefinitely on port {port}...")
                
                # Keep the server running
                server.serve_forever()
                
            except Exception as e:
                print(f"❌ Error starting server on port {port}: {e}")
                continue
        else:
            print(f"❌ Port {port} is not available")
    
    print("❌ No available ports found!")
    sys.exit(1)

if __name__ == "__main__":
    main()
