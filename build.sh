#!/bin/bash
# Build script for Railway deployment

echo "🚀 Starting Railway build process..."

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements with verbose output
echo "📦 Installing requirements..."
pip install --no-cache-dir -r requirements-railway.txt

# Verify critical dependencies
echo "🔍 Verifying critical dependencies..."
python test_dependencies.py

echo "✅ Build completed successfully!"
