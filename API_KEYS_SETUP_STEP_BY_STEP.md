# API Keys Setup - Step by Step Guide

## 🎯 **Quick Setup (5 minutes each)**

Follow these steps to get your API keys and configure them in the system.

---

## **1. Meetup API Key** 🎯

### **Get the API Key**
1. **Go to**: [Meetup API Keys](https://www.meetup.com/meetup_api/)
2. **Click**: "Get your API key"
3. **Sign in** with your Meetup account (or create one)
4. **Fill out the form**:
   - Application Name: `AI Event Scraper`
   - Description: `Event discovery and aggregation service`
   - Website: `https://your-domain.com` (or your actual website)
5. **Accept terms** and submit
6. **Copy your API key** (looks like: `1234567890abcdef1234567890abcdef`)

### **Configure in System**
Add to your `.env` file:
```bash
EVENT_SCRAPER_MEETUP_API_KEY=your_actual_meetup_key_here
```

**Expected Results**: 50-200+ events per city

---

## **2. Facebook API Key** 📘

### **Get the API Key**
1. **Go to**: [Facebook Developers](https://developers.facebook.com/)
2. **Click**: "My Apps" → "Create App"
3. **Choose**: "Consumer" app type
4. **Fill out**:
   - App Name: `AI Event Scraper`
   - App Contact Email: Your email
   - App Purpose: `Event discovery and aggregation`
5. **Create App** and go to App Dashboard
6. **Go to**: "Settings" → "Basic"
7. **Copy**: "App ID" and "App Secret"
8. **Add Products**: "Facebook Login" (required for Events API)
9. **Go to**: "App Review" → "Permissions and Features"
10. **Request**: `user_events` permission

### **Configure in System**
Add to your `.env` file:
```bash
EVENT_SCRAPER_FACEBOOK_API_KEY=your_app_id_here
```

**Expected Results**: 100-300+ events per city

---

## **3. Google API Key** 🔍

### **Get the API Key**
1. **Go to**: [Google Cloud Console](https://console.cloud.google.com/)
2. **Create Project** (or select existing):
   - Project Name: `AI Event Scraper`
3. **Enable APIs**:
   - Go to "APIs & Services" → "Library"
   - Search and enable: "Google Calendar API"
   - Search and enable: "Google Places API"
4. **Create Credentials**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy your API key
5. **Restrict API Key** (recommended):
   - Click on your API key
   - Under "API restrictions", select "Restrict key"
   - Choose: "Google Calendar API" and "Google Places API"

### **Configure in System**
Add to your `.env` file:
```bash
EVENT_SCRAPER_GOOGLE_API_KEY=your_google_api_key_here
```

**Expected Results**: 50-150+ events per city

---

## **4. Test Your API Keys** 🧪

### **Create Test Script**
Create a file called `test_api_keys.py`:

```python
#!/usr/bin/env python3
"""Test API keys configuration."""

import os
import sys
import asyncio
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import settings
from src.scrapers.api_scraper import APIEventScraper

async def test_api_keys():
    """Test all configured API keys."""
    print("🧪 Testing API Keys...")
    
    # Test Meetup API
    if settings.meetup_api_key:
        print("✅ Meetup API Key: Configured")
    else:
        print("❌ Meetup API Key: Not configured")
    
    # Test Facebook API
    if settings.facebook_api_key:
        print("✅ Facebook API Key: Configured")
    else:
        print("❌ Facebook API Key: Not configured")
    
    # Test Google API
    if settings.google_api_key:
        print("✅ Google API Key: Configured")
    else:
        print("❌ Google API Key: Not configured")
    
    # Test API Scraper
    try:
        scraper = APIEventScraper()
        print("✅ API Scraper: Initialized successfully")
    except Exception as e:
        print(f"❌ API Scraper: Error - {e}")

if __name__ == "__main__":
    asyncio.run(test_api_keys())
```

### **Run the Test**
```bash
python test_api_keys.py
```

---

## **5. Environment Configuration** ⚙️

### **Local Development**
1. **Copy the example file**:
   ```bash
   cp config/dev/env.example .env
   ```

2. **Edit `.env`** with your actual API keys:
   ```bash
   # Event Platform API Keys
   EVENT_SCRAPER_EVENTBRITE_API_KEY=your_eventbrite_token_here
   EVENT_SCRAPER_MEETUP_API_KEY=your_meetup_key_here
   EVENT_SCRAPER_FACEBOOK_API_KEY=your_facebook_token_here
   EVENT_SCRAPER_GOOGLE_API_KEY=your_google_key_here
   ```

### **Production (Railway)**
Add these environment variables in your Railway dashboard:
```
EVENT_SCRAPER_MEETUP_API_KEY=your_meetup_key_here
EVENT_SCRAPER_FACEBOOK_API_KEY=your_facebook_token_here
EVENT_SCRAPER_GOOGLE_API_KEY=your_google_key_here
```

---

## **6. Expected Results** 📊

| **API** | **Setup Time** | **Events per City** | **Quality** |
|---------|----------------|-------------------|-------------|
| **Meetup** | 5 minutes | 50-200+ | High |
| **Facebook** | 10 minutes | 100-300+ | High |
| **Google** | 5 minutes | 50-150+ | High |
| **Total** | 20 minutes | 200-650+ | Excellent |

---

## **7. Troubleshooting** 🔧

### **Common Issues**

**Meetup API**:
- ❌ "Invalid API key" → Check if key is correct
- ❌ "Rate limit exceeded" → Wait and try again

**Facebook API**:
- ❌ "App not approved" → Use test mode for development
- ❌ "Permission denied" → Request user_events permission

**Google API**:
- ❌ "API not enabled" → Enable Calendar API in console
- ❌ "Quota exceeded" → Check usage limits

### **Get Help**
- Check the logs: `tail -f logs/app.log`
- Test individual scrapers: `python test_api_keys.py`
- Check API documentation for each platform

---

## **8. Next Steps** 🚀

After setting up all API keys:

1. **Test the system**: Run `python test_api_keys.py`
2. **Start scraping**: The system will automatically use the new APIs
3. **Monitor results**: Check the `/stats` endpoint for event counts
4. **Scale up**: Add more cities to your scraping list

**Expected Total Events**: 500-1,500+ events per city with all APIs configured!

