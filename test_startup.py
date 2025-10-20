#!/usr/bin/env python3
"""Test script to verify the application can start properly."""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test all critical imports."""
    print("🔍 Testing critical imports...")
    
    imports_to_test = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("motor", "Motor (MongoDB)"),
        ("pymongo", "PyMongo"),
        ("aiohttp", "aiohttp"),
        ("beautifulsoup4", "BeautifulSoup"),
        ("pydantic", "Pydantic"),
        ("openai", "OpenAI"),
    ]
    
    failed_imports = []
    
    for module_name, description in imports_to_test:
        try:
            __import__(module_name)
            print(f"✅ {description}: {module_name}")
        except ImportError as e:
            print(f"❌ {description}: {module_name} - {e}")
            failed_imports.append(module_name)
    
    # Test optional imports
    optional_imports = [
        ("feedparser", "RSS Parser"),
        ("icalendar", "iCal Parser"),
        ("selenium", "Selenium"),
    ]
    
    print("\n🔍 Testing optional imports...")
    for module_name, description in optional_imports:
        try:
            __import__(module_name)
            print(f"✅ {description}: {module_name}")
        except ImportError as e:
            print(f"⚠️ {description}: {module_name} - {e}")
    
    return len(failed_imports) == 0

def test_app_creation():
    """Test if we can create the FastAPI app."""
    print("\n🔍 Testing FastAPI app creation...")
    
    try:
        # Test importing the main app
        import railway_complete
        print("✅ railway_complete.py imported successfully")
        
        # Test if we can access the app
        app = railway_complete.app
        print("✅ FastAPI app object accessible")
        
        return True
        
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run all startup tests."""
    print("🚀 Running startup tests...")
    print(f"📊 Python version: {sys.version}")
    print(f"📊 Working directory: {os.getcwd()}")
    
    # Test imports
    imports_ok = test_imports()
    
    # Test app creation
    app_ok = test_app_creation()
    
    if imports_ok and app_ok:
        print("\n✅ All startup tests passed!")
        return 0
    else:
        print("\n❌ Some startup tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
