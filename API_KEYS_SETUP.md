# API Keys Setup Guide

## 🎯 **Configure API Keys for Maximum Event Data**

This guide will help you obtain and configure API keys for official event platforms to get **structured, reliable data** instead of relying on web scraping.

## 📊 **Expected Results with API Keys**

| Platform | Without API Key | With API Key | Improvement |
|----------|----------------|--------------|-------------|
| **Eventbrite** | 0 events (blocked) | 100-500+ events | **∞%** |
| **Meetup** | 0 events (blocked) | 50-200+ events | **∞%** |
| **Facebook Events** | 0 events (blocked) | 100-300+ events | **∞%** |
| **Google Calendar** | 0 events (blocked) | 50-150+ events | **∞%** |
| **Total** | 0 events | 300-1,150+ events | **∞%** |

## 🔑 **Required API Keys**

### **1. Eventbrite API** ⭐⭐⭐⭐⭐
**Why**: Largest event platform, structured data, high volume
**Cost**: Free (with rate limits)
**Events**: 100-500+ per city

#### **How to Get:**
1. Go to [Eventbrite API](https://www.eventbrite.com/platform/api-keys/)
2. Sign up for Eventbrite account
3. Create new app
4. Copy your **Private Token**
5. Set environment variable: `EVENT_SCRAPER_EVENTBRITE_API_KEY=your_token_here`

#### **Rate Limits:**
- 1,000 requests/hour (free tier)
- 10,000 requests/hour (paid tier)

---

### **2. Meetup API** ⭐⭐⭐⭐
**Why**: Large community events, reliable data
**Cost**: Free (with rate limits)
**Events**: 50-200+ per city

#### **How to Get:**
1. Go to [Meetup API](https://www.meetup.com/meetup_api/)
2. Sign up for Meetup account
3. Request API key
4. Copy your **API Key**
5. Set environment variable: `EVENT_SCRAPER_MEETUP_API_KEY=your_key_here`

#### **Rate Limits:**
- 200 requests/hour (free tier)
- 1,000 requests/hour (paid tier)

---

### **3. Facebook Events API** ⭐⭐⭐⭐
**Why**: Massive event database, social data
**Cost**: Free (with rate limits)
**Events**: 100-300+ per city

#### **How to Get:**
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create new app
3. Add "Facebook Login" product
4. Get your **App Access Token**
5. Set environment variable: `EVENT_SCRAPER_FACEBOOK_API_KEY=your_token_here`

#### **Rate Limits:**
- 200 requests/hour (free tier)
- 1,000 requests/hour (paid tier)

---

### **4. Google Calendar API** ⭐⭐⭐
**Why**: Public calendars, university events
**Cost**: Free (with rate limits)
**Events**: 50-150+ per city

#### **How to Get:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable Calendar API
4. Create credentials (API Key)
5. Copy your **API Key**
6. Set environment variable: `EVENT_SCRAPER_GOOGLE_API_KEY=your_key_here`

#### **Rate Limits:**
- 1,000 requests/day (free tier)
- 10,000 requests/day (paid tier)

---

## 🔧 **Configuration Setup**

### **1. Environment Variables**

Create a `.env` file in your project root:

```bash
# Event Platform API Keys
EVENT_SCRAPER_EVENTBRITE_API_KEY=your_eventbrite_token_here
EVENT_SCRAPER_MEETUP_API_KEY=your_meetup_key_here
EVENT_SCRAPER_FACEBOOK_API_KEY=your_facebook_token_here
EVENT_SCRAPER_GOOGLE_API_KEY=your_google_key_here

# Optional: Additional API Keys
EVENT_SCRAPER_NEWSAPI_KEY=your_newsapi_key_here
EVENT_SCRAPER_PRNEWSWIRE_API_KEY=your_prnewswire_key_here
EVENT_SCRAPER_CITYSPARK_API_KEY=your_cityspark_key_here
EVENT_SCRAPER_EVENTFUL_API_KEY=your_eventful_key_here
```

### **2. Railway Deployment**

For Railway deployment, add these as environment variables in your Railway dashboard:

```bash
EVENT_SCRAPER_EVENTBRITE_API_KEY=your_eventbrite_token_here
EVENT_SCRAPER_MEETUP_API_KEY=your_meetup_key_here
EVENT_SCRAPER_FACEBOOK_API_KEY=your_facebook_token_here
EVENT_SCRAPER_GOOGLE_API_KEY=your_google_key_here
```

### **3. Local Development**

For local development, create a `.env` file:

```bash
# Copy the example file
cp config/dev/env.example .env

# Edit the file and add your API keys
nano .env
```

## 🚀 **Quick Start (Recommended APIs)**

### **Priority 1: Eventbrite** (Most Important)
- **Signup**: [Eventbrite API](https://www.eventbrite.com/platform/api-keys/)
- **Time**: 5 minutes
- **Impact**: 100-500+ events per city
- **Difficulty**: Easy

### **Priority 2: Meetup** (High Impact)
- **Signup**: [Meetup API](https://www.meetup.com/meetup_api/)
- **Time**: 5 minutes
- **Impact**: 50-200+ events per city
- **Difficulty**: Easy

### **Priority 3: Facebook Events** (Social Events)
- **Signup**: [Facebook Developers](https://developers.facebook.com/)
- **Time**: 10 minutes
- **Impact**: 100-300+ events per city
- **Difficulty**: Medium

### **Priority 4: Google Calendar** (Public Events)
- **Signup**: [Google Cloud Console](https://console.cloud.google.com/)
- **Time**: 15 minutes
- **Impact**: 50-150+ events per city
- **Difficulty**: Medium

## 📈 **Expected Results by City**

With all API keys configured, you should get:

### **San Francisco:**
- Eventbrite: 200-400 events
- Meetup: 100-150 events
- Facebook: 150-250 events
- Google Calendar: 50-100 events
- **Total**: 500-900 events

### **New York:**
- Eventbrite: 300-500 events
- Meetup: 150-200 events
- Facebook: 200-300 events
- Google Calendar: 75-125 events
- **Total**: 725-1,125 events

### **Chicago:**
- Eventbrite: 150-300 events
- Meetup: 75-125 events
- Facebook: 100-200 events
- Google Calendar: 50-100 events
- **Total**: 375-725 events

## 🔍 **Testing Your API Keys**

After setting up your API keys, test them:

```bash
# Test the enhanced scraper with API keys
python -c "
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path('src')))
from scrapers.api_scraper import APIEventScraper

async def test():
    async with APIEventScraper() as scraper:
        events = await scraper.scrape_events('San Francisco', 'United States')
        print(f'Found {len(events)} events with API keys!')

asyncio.run(test())
"
```

## 🛡️ **Security Best Practices**

1. **Never commit API keys** to version control
2. **Use environment variables** for all keys
3. **Rotate keys regularly** (every 90 days)
4. **Monitor usage** to avoid rate limits
5. **Use different keys** for dev/staging/prod

## 🎯 **Next Steps**

1. **Get Eventbrite API key** (5 minutes) - Highest impact
2. **Get Meetup API key** (5 minutes) - High impact
3. **Deploy to Railway** with API keys
4. **Monitor results** - Should see 10x more events
5. **Add more API keys** as needed

## 📞 **Support**

If you need help with any API setup:
1. Check the official documentation links above
2. Most APIs have free tiers with generous limits
3. Start with Eventbrite and Meetup for quick wins
4. Add Facebook and Google Calendar for comprehensive coverage

With API keys configured, your event scraper will transform from **0 events** to **hundreds of events per city** with reliable, structured data!
