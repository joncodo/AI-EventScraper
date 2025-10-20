#!/usr/bin/env python3
"""Startup script to ensure dependencies are installed before main application starts."""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def main():
    """Ensure dependencies are installed before starting the main application."""
    print("🔍 ============================================")
    print("🔍 STARTUP DEPENDENCY CHECK")
    print("🔍 ============================================")
    print(f"📊 Python version: {sys.version}")
    print(f"📊 Working directory: {os.getcwd()}")
    print(f"📊 Python path: {sys.path[:3]}...")
    print(f"📊 Environment variables:")
    for key in ['PORT', 'MONGODB_URI', 'ENVIRONMENT', 'PYTHONPATH']:
        value = os.getenv(key, 'NOT SET')
        if 'MONGODB_URI' in key and value != 'NOT SET':
            value = value[:20] + '...' if len(value) > 20 else value
        print(f"   - {key}: {value}")
    
    print("\n🔍 Step 1: Testing critical imports...")
    critical_imports = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('motor', 'Motor (MongoDB)'),
        ('pymongo', 'PyMongo'),
        ('aiohttp', 'aiohttp'),
        ('beautifulsoup4', 'BeautifulSoup'),
        ('pydantic', 'Pydantic'),
        ('openai', 'OpenAI'),
    ]
    
    failed_imports = []
    for module_name, description in critical_imports:
        try:
            __import__(module_name)
            print(f"   ✅ {description}: {module_name}")
        except ImportError as e:
            print(f"   ❌ {description}: {module_name} - {e}")
            failed_imports.append(module_name)
    
    print("\n🔍 Step 2: Testing optional imports...")
    optional_imports = [
        ('atoma', 'RSS Parser'),
        ('icalendar', 'iCal Parser'),
        ('selenium', 'Selenium'),
    ]
    
    for module_name, description in optional_imports:
        try:
            __import__(module_name)
            print(f"   ✅ {description}: {module_name}")
        except ImportError as e:
            print(f"   ⚠️ {description}: {module_name} - {e}")
    
    print("\n🔍 Step 3: Running dependency installer...")
    try:
        from utils.dependency_installer import ensure_dependencies
        success = ensure_dependencies()
        
        if success:
            print("✅ All critical dependencies are available!")
        else:
            print("⚠️ Some dependencies may not be available, but continuing...")
    except Exception as e:
        print(f"❌ Dependency installer failed: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        print("⚠️ Continuing with startup anyway...")
    
    print("\n🔍 Step 4: Testing main app import...")
    try:
        import railway_complete
        print("✅ railway_complete imported successfully")
        print("✅ Main application module is accessible")
    except Exception as e:
        print(f"❌ Failed to import railway_complete: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return 1  # Fail startup if main app can't be imported
    
    print("\n✅ ============================================")
    print("✅ STARTUP DEPENDENCY CHECK COMPLETED")
    print("✅ ============================================")
    return 0

if __name__ == "__main__":
    sys.exit(main())
