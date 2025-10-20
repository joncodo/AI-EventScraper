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
    
    try:
        from utils.dependency_installer import ensure_dependencies
        success = ensure_dependencies()
        
        if success:
            print("✅ All critical dependencies are available!")
            return 0
        else:
            print("⚠️ Some dependencies may not be available, but continuing...")
            return 0  # Don't fail startup, let the app handle it
            
    except Exception as e:
        print(f"❌ Dependency installer failed: {e}")
        print("⚠️ Continuing with startup anyway...")
        return 0  # Don't fail startup

if __name__ == "__main__":
    sys.exit(main())
