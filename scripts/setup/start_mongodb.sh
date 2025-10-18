#!/bin/bash
# MongoDB startup script for local development

echo "🚀 Starting MongoDB for AI Event Scraper..."

# Kill any existing MongoDB processes
pkill -f mongod

# Wait a moment
sleep 2

# Start MongoDB with minimal configuration
mongod \
  --dbpath /opt/homebrew/var/mongodb \
  --logpath /opt/homebrew/var/log/mongodb/mongo.log \
  --bind_ip 127.0.0.1 \
  --port 27017 &

# Wait for MongoDB to start
sleep 3

# Check if MongoDB is running
if pgrep -f mongod > /dev/null; then
    echo "✅ MongoDB started successfully!"
    echo "📍 Running on: mongodb://localhost:27017"
    echo "📊 Database path: /opt/homebrew/var/mongodb"
    echo "📝 Log file: /opt/homebrew/var/log/mongodb/mongo.log"
    echo ""
    echo "🧪 Test connection with: python test_mongodb.py"
    echo "🛑 Stop MongoDB with: pkill -f mongod"
else
    echo "❌ Failed to start MongoDB"
    echo "📝 Check logs: tail -f /opt/homebrew/var/log/mongodb/mongo.log"
    exit 1
fi
