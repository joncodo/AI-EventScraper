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

# Force install critical dependencies
echo "📦 Force installing critical dependencies..."
pip install --no-cache-dir --force-reinstall feedparser icalendar

# Verify critical dependencies
echo "🔍 Verifying critical dependencies..."
python test_dependencies.py

# If test fails, try alternative installation methods
if [ $? -ne 0 ]; then
    echo "⚠️ Some dependencies failed, trying alternative methods..."
    
    # Try installing with different methods
    pip install --no-cache-dir --no-deps feedparser
    pip install --no-cache-dir --no-deps icalendar
    
    # Install dependencies separately
    pip install --no-cache-dir sgmllib3k python-dateutil pytz lxml
    
    echo "🔍 Re-testing dependencies..."
    python test_dependencies.py
fi

echo "✅ Build completed successfully!"
