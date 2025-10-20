#!/bin/bash
# Build script for Railway deployment

echo "🚀 Starting Railway build process..."

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements with verbose output
echo "📦 Installing requirements..."
pip install --no-cache-dir -r requirements-railway.txt

# Install critical dependencies with multiple methods
echo "📦 Installing critical dependencies with multiple methods..."

# Method 1: Standard install
echo "📦 Method 1: Standard install..."
pip install --no-cache-dir feedparser==6.0.10 icalendar==5.0.11

# Method 2: Force reinstall
echo "📦 Method 2: Force reinstall..."
pip install --no-cache-dir --force-reinstall feedparser icalendar

# Method 3: Install without dependencies
echo "📦 Method 3: Install without dependencies..."
pip install --no-cache-dir --no-deps feedparser icalendar

# Method 4: Install dependencies separately
echo "📦 Method 4: Install dependencies separately..."
pip install --no-cache-dir sgmllib3k python-dateutil pytz lxml

# Method 5: Install from different sources
echo "📦 Method 5: Install from different sources..."
pip install --no-cache-dir --index-url https://pypi.org/simple/ feedparser icalendar

# Verify critical dependencies
echo "🔍 Verifying critical dependencies..."
python test_dependencies.py

# If test fails, try runtime installation
if [ $? -ne 0 ]; then
    echo "⚠️ Some dependencies failed, but runtime installer will handle them..."
    echo "📦 Runtime dependency installer will attempt installation on startup"
else
    echo "✅ All dependencies verified successfully!"
fi

echo "✅ Build completed successfully!"
