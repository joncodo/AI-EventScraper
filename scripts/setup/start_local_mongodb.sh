#!/bin/bash
# MongoDB startup script for AI Event Scraper

echo "🚀 Starting Local MongoDB for AI Event Scraper..."

# Kill any existing MongoDB processes
pkill -f mongod 2>/dev/null

# Wait a moment
sleep 2

# Create a clean database directory
mkdir -p /tmp/mongodb_eventscraping

# Start MongoDB with clean configuration
mongod \
  --dbpath /tmp/mongodb_eventscraping \
  --port 27017 \
  --bind_ip 127.0.0.1 \
  --logpath /tmp/mongodb_eventscraping.log &

# Wait for MongoDB to start
sleep 3

# Check if MongoDB is running
if pgrep -f mongod > /dev/null; then
    echo "✅ MongoDB started successfully!"
    echo "📍 Running on: mongodb://localhost:27017"
    echo "📊 Database path: /tmp/mongodb_eventscraping"
    echo "📝 Log file: /tmp/mongodb_eventscraping.log"
    echo ""
    echo "🧪 Test connection with: python test_mongodb.py"
    echo "🎯 Run scraper with: python cli.py scrape \"Your City\" \"Your Country\" --save"
    echo "🔍 Query events with: python cli.py query --city \"Your City\""
    echo "📊 Check status with: python cli.py status"
    echo "🛑 Stop MongoDB with: pkill -f mongod"
    echo ""
    echo "🎉 Your AI Event Scraper is ready for massive scale!"
else
    echo "❌ Failed to start MongoDB"
    echo "📝 Check logs: tail -f /tmp/mongodb_eventscraping.log"
    exit 1
fi

