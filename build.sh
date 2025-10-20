#!/bin/bash
# Build script for Railway deployment

echo "🚀 Starting Railway build process..."

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements with verbose output
echo "📦 Installing requirements..."
pip install --no-cache-dir -r requirements-railway.txt

# Install additional dependencies that might be missing
echo "📦 Installing additional dependencies..."
pip install --no-cache-dir feedparser==6.0.10 icalendar==5.0.11

# Verify critical dependencies
echo "🔍 Verifying critical dependencies..."
python test_dependencies.py

echo "✅ Build completed successfully!"
