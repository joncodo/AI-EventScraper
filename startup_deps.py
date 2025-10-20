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
    print("🔍 Running startup dependency check...")
    print(f"📊 Python version: {sys.version}")
    print(f"📊 Working directory: {os.getcwd()}")
    print(f"📊 Python path: {sys.path[:3]}...")
    
    try:
        from utils.dependency_installer import ensure_dependencies
        success = ensure_dependencies()
        
        if success:
            print("✅ All critical dependencies are available!")
        else:
            print("⚠️ Some dependencies may not be available, but continuing...")
        
        # Test imports directly
        print("🔍 Testing direct imports...")
        try:
            import atoma
            print("✅ atoma import successful")
        except ImportError as e:
            print(f"❌ atoma import failed: {e}")
        
        try:
            import icalendar
            print("✅ icalendar import successful")
        except ImportError as e:
            print(f"❌ icalendar import failed: {e}")
        
        return 0  # Don't fail startup, let the app handle it
            
    except Exception as e:
        print(f"❌ Dependency installer failed: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        print("⚠️ Continuing with startup anyway...")
        return 0  # Don't fail startup

if __name__ == "__main__":
    sys.exit(main())
