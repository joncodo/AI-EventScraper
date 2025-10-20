#!/usr/bin/env python3
"""Test script to verify all dependencies are installed correctly."""

import sys

def test_dependency(module_name, description):
    """Test if a dependency can be imported."""
    try:
        __import__(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {description}: {module_name} - {e}")
        return False

def main():
    """Test all critical dependencies."""
    print("🔍 Testing critical dependencies...")
    
    dependencies = [
        ("feedparser", "RSS Parser"),
        ("icalendar", "iCal Parser"),
        ("selenium", "Browser Automation"),
        ("playwright", "Advanced Browser Automation"),
        ("undetected_chromedriver", "Stealth Browser"),
        ("requests_html", "HTML Parser"),
        ("aiohttp", "Async HTTP Client"),
        ("motor", "MongoDB Async Driver"),
        ("pymongo", "MongoDB Driver"),
        ("beautifulsoup4", "HTML Parser"),
        ("fake_useragent", "User Agent Generator"),
        ("openai", "OpenAI Client"),
        ("fastapi", "Web Framework"),
        ("uvicorn", "ASGI Server"),
        ("pydantic", "Data Validation"),
    ]
    
    failed = []
    for module, description in dependencies:
        if not test_dependency(module, description):
            failed.append(module)
    
    if failed:
        print(f"\n❌ Failed to import: {', '.join(failed)}")
        print("Please install missing dependencies:")
        for module in failed:
            print(f"  pip install {module}")
        sys.exit(1)
    else:
        print("\n✅ All dependencies imported successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
