#!/bin/bash

# AI Event Scraper - Railway Startup Script
# This script ensures the application starts properly in Railway

echo "🚀 Starting AI Event Scraper API Server..."

# Set default port if not provided
export PORT=${PORT:-8000}

# Start the API server
python api_server.py --host 0.0.0.0 --port $PORT
