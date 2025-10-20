#!/usr/bin/env python3
"""Minimal startup test to verify the application can start."""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_minimal_startup():
    """Test minimal startup without full initialization."""
    print("🔍 Testing minimal startup...")
    
    try:
        # Test basic imports
        print("📦 Testing basic imports...")
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn imported successfully")
        
        # Test if we can create a basic FastAPI app
        print("📦 Testing FastAPI app creation...")
        app = fastapi.FastAPI(title="Test App")
        print("✅ FastAPI app created successfully")
        
        # Test if we can import the main app
        print("📦 Testing main app import...")
        import railway_complete
        print("✅ railway_complete imported successfully")
        
        print("✅ Minimal startup test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Minimal startup test failed: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_minimal_startup()
    sys.exit(0 if success else 1)
