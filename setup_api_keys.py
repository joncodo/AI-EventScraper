#!/usr/bin/env python3
"""Interactive API keys setup script."""

import os
import sys
from pathlib import Path

def setup_api_keys():
    """Interactive setup for API keys."""
    print("🔑 API Keys Setup Wizard")
    print("=" * 40)
    print()
    
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file from template...")
        try:
            # Copy from example
            import shutil
            shutil.copy("config/dev/env.example", ".env")
            print("✅ Created .env file")
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return
    else:
        print("✅ .env file already exists")
    
    print()
    print("🔧 Let's configure your API keys:")
    print()
    
    # Get API keys from user
    api_keys = {}
    
    print("1. Meetup API Key")
    print("   Get it from: https://www.meetup.com/meetup_api/")
    meetup_key = input("   Enter your Meetup API key (or press Enter to skip): ").strip()
    if meetup_key:
        api_keys['EVENT_SCRAPER_MEETUP_API_KEY'] = meetup_key
    
    print()
    print("2. Facebook API Key")
    print("   Get it from: https://developers.facebook.com/")
    facebook_key = input("   Enter your Facebook App ID (or press Enter to skip): ").strip()
    if facebook_key:
        api_keys['EVENT_SCRAPER_FACEBOOK_API_KEY'] = facebook_key
    
    print()
    print("3. Google API Key")
    print("   Get it from: https://console.cloud.google.com/")
    google_key = input("   Enter your Google API key (or press Enter to skip): ").strip()
    if google_key:
        api_keys['EVENT_SCRAPER_GOOGLE_API_KEY'] = google_key
    
    print()
    print("4. Eventbrite API Key")
    print("   Get it from: https://www.eventbrite.com/platform/api-keys/")
    eventbrite_key = input("   Enter your Eventbrite API key (or press Enter to skip): ").strip()
    if eventbrite_key:
        api_keys['EVENT_SCRAPER_EVENTBRITE_API_KEY'] = eventbrite_key
    
    # Update .env file
    if api_keys:
        print()
        print("💾 Updating .env file...")
        
        # Read current .env
        with open(".env", "r") as f:
            content = f.read()
        
        # Update with new keys
        for key, value in api_keys.items():
            # Replace existing or add new
            if f"{key}=" in content:
                # Replace existing
                import re
                pattern = f"{key}=.*"
                content = re.sub(pattern, f"{key}={value}", content)
            else:
                # Add new
                content += f"\n{key}={value}\n"
        
        # Write back
        with open(".env", "w") as f:
            f.write(content)
        
        print("✅ Updated .env file with your API keys")
    else:
        print("ℹ️  No API keys provided. You can add them later to .env file")
    
    print()
    print("🧪 Testing configuration...")
    
    # Test the configuration
    try:
        # Add src to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from src.core.config import settings
        
        print("✅ Configuration loaded successfully")
        print(f"Environment: {settings.environment}")
        
        # Check which APIs are configured
        configured_apis = []
        if settings.meetup_api_key and settings.meetup_api_key != "your_meetup_key_here":
            configured_apis.append("Meetup")
        if settings.facebook_api_key and settings.facebook_api_key != "your_facebook_token_here":
            configured_apis.append("Facebook")
        if settings.google_api_key and settings.google_api_key != "your_google_key_here":
            configured_apis.append("Google")
        if settings.eventbrite_api_key and settings.eventbrite_api_key != "your_eventbrite_token_here":
            configured_apis.append("Eventbrite")
        
        if configured_apis:
            print(f"✅ Configured APIs: {', '.join(configured_apis)}")
        else:
            print("⚠️  No APIs configured yet")
            
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
    
    print()
    print("🎯 Next Steps:")
    print("1. Run: python test_api_keys.py")
    print("2. Start the API server: python api_server.py")
    print("3. Check the /stats endpoint for event counts")
    print()
    print("📚 For detailed setup instructions, see: API_KEYS_SETUP_STEP_BY_STEP.md")

if __name__ == "__main__":
    setup_api_keys()

