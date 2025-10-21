#!/usr/bin/env python3
"""Setup Google API credentials in .env file."""

import os
import shutil
from pathlib import Path

def setup_google_credentials():
    """Setup Google API credentials in .env file."""
    print("🔍 Setting up Google API credentials...")
    
    # Google API key
    google_api_key = "AIzaSyCWEkCguR1umdjJNVInly2LCZgUAm76MPo"
    
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file from template...")
        try:
            # Copy from example
            shutil.copy("config/dev/env.example", ".env")
            print("✅ Created .env file from template")
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return
    else:
        print("✅ .env file already exists")
    
    # Read current .env content
    with open(".env", "r") as f:
        content = f.read()
    
    # Update Google credentials
    print("💾 Updating .env file with Google credentials...")
    
    # Update Google API key
    if "EVENT_SCRAPER_GOOGLE_API_KEY=" in content:
        # Replace existing
        import re
        pattern = "EVENT_SCRAPER_GOOGLE_API_KEY=.*"
        content = re.sub(pattern, f"EVENT_SCRAPER_GOOGLE_API_KEY={google_api_key}", content)
        print("✅ Updated EVENT_SCRAPER_GOOGLE_API_KEY")
    else:
        # Add new
        content += f"\nEVENT_SCRAPER_GOOGLE_API_KEY={google_api_key}\n"
        print("✅ Added EVENT_SCRAPER_GOOGLE_API_KEY")
    
    # Write back to .env
    with open(".env", "w") as f:
        f.write(content)
    
    print("✅ Google API credentials saved to .env file")
    print()
    print("🧪 Testing configuration...")
    
    # Test the configuration
    try:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from src.core.config import settings
        
        print("✅ Configuration loaded successfully")
        
        # Check Google API key
        if settings.google_api_key == google_api_key:
            print("✅ Google API Key: Configured correctly")
        else:
            print("❌ Google API Key: Not configured correctly")
            
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
    
    print()
    print("🎯 Next Steps:")
    print("1. Run: python test_api_keys.py")
    print("2. Start the API server: python api_server.py")
    print("3. Check the /stats endpoint for Google events")
    print()
    print("📊 Expected Results:")
    print("- 50-150+ Google Calendar events per city")
    print("- Public calendar events from organizations")
    print("- University and government events")
    print("- Community and business events")

if __name__ == "__main__":
    setup_google_credentials()

