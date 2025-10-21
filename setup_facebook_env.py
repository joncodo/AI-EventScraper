#!/usr/bin/env python3
"""Setup Facebook API credentials in .env file."""

import os
import shutil
from pathlib import Path

def setup_facebook_credentials():
    """Setup Facebook API credentials in .env file."""
    print("🔑 Setting up Facebook API credentials...")
    
    # Facebook credentials
    facebook_app_id = "1179636980759026"
    facebook_app_secret = "ad968745cf5ead627c0d31e41d90af87"
    
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
    
    # Update Facebook credentials
    facebook_updates = {
        "EVENT_SCRAPER_FACEBOOK_API_KEY": facebook_app_id,
        "EVENT_SCRAPER_FACEBOOK_APP_ID": facebook_app_id,
        "EVENT_SCRAPER_FACEBOOK_APP_SECRET": facebook_app_secret
    }
    
    print("💾 Updating .env file with Facebook credentials...")
    
    # Update each credential
    for key, value in facebook_updates.items():
        if f"{key}=" in content:
            # Replace existing
            import re
            pattern = f"{key}=.*"
            content = re.sub(pattern, f"{key}={value}", content)
            print(f"✅ Updated {key}")
        else:
            # Add new
            content += f"\n{key}={value}\n"
            print(f"✅ Added {key}")
    
    # Write back to .env
    with open(".env", "w") as f:
        f.write(content)
    
    print("✅ Facebook credentials saved to .env file")
    print()
    print("🧪 Testing configuration...")
    
    # Test the configuration
    try:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from src.core.config import settings
        
        print("✅ Configuration loaded successfully")
        
        # Check Facebook API key
        if settings.facebook_api_key == facebook_app_id:
            print("✅ Facebook API Key: Configured correctly")
        else:
            print("❌ Facebook API Key: Not configured correctly")
            
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
    
    print()
    print("🎯 Next Steps:")
    print("1. Run: python test_api_keys.py")
    print("2. Start the API server: python api_server.py")
    print("3. Check the /stats endpoint for Facebook events")
    print()
    print("📊 Expected Results:")
    print("- 100-300+ Facebook events per city")
    print("- High quality social events")
    print("- Real event data with dates and locations")

if __name__ == "__main__":
    setup_facebook_credentials()

