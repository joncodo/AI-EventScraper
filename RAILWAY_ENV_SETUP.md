# Railway Environment Variables Setup

## 🚀 **Railway Deployment with API Keys**

This guide shows you how to configure API keys in Railway for maximum event data collection.

## 📋 **Required Environment Variables for Railway**

Add these environment variables in your Railway dashboard:

### **1. Core Configuration**
```bash
EVENT_SCRAPER_ENVIRONMENT=production
EVENT_SCRAPER_DEBUG=false
EVENT_SCRAPER_LOG_LEVEL=INFO
```

### **2. MongoDB Configuration**
```bash
EVENT_SCRAPER_MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/event_scraper
EVENT_SCRAPER_MONGODB_DATABASE=event_scraper_prod
```

### **3. OpenAI Configuration**
```bash
EVENT_SCRAPER_OPENAI_API_KEY=your_openai_api_key_here
```

### **4. Event Platform API Keys** ⭐⭐⭐⭐⭐
```bash
# Eventbrite API (Most Important)
EVENT_SCRAPER_EVENTBRITE_API_KEY=your_eventbrite_token_here

# Meetup API (High Impact)
EVENT_SCRAPER_MEETUP_API_KEY=your_meetup_key_here

# Facebook Events API (Social Events)
EVENT_SCRAPER_FACEBOOK_API_KEY=your_facebook_token_here

# Google Calendar API (Public Events)
EVENT_SCRAPER_GOOGLE_API_KEY=your_google_key_here
```

### **5. Optional API Keys**
```bash
# News and Press Releases
EVENT_SCRAPER_NEWSAPI_KEY=your_newsapi_key_here
EVENT_SCRAPER_PRNEWSWIRE_API_KEY=your_prnewswire_key_here

# Event Aggregators
EVENT_SCRAPER_CITYSPARK_API_KEY=your_cityspark_key_here
EVENT_SCRAPER_EVENTFUL_API_KEY=your_eventful_key_here
```

### **6. Performance Configuration**
```bash
EVENT_SCRAPER_MAX_CONCURRENT_REQUESTS=50
EVENT_SCRAPER_REQUEST_DELAY_SECONDS=0.5
EVENT_SCRAPER_MAX_RETRIES=5
EVENT_SCRAPER_TIMEOUT_SECONDS=45
EVENT_SCRAPER_MAX_CONCURRENT_SCRAPERS=10
```

## 🔧 **How to Add Environment Variables in Railway**

### **Step 1: Access Railway Dashboard**
1. Go to [Railway.app](https://railway.app)
2. Sign in to your account
3. Select your project

### **Step 2: Add Environment Variables**
1. Click on your service
2. Go to the "Variables" tab
3. Click "New Variable"
4. Add each environment variable from the list above

### **Step 3: Deploy**
1. Railway will automatically redeploy when you add variables
2. Check the logs to ensure everything is working
3. Test the API endpoints

## 🎯 **Priority Order for API Keys**

### **Phase 1: Essential APIs (Deploy First)**
1. **Eventbrite API** - 5 minutes setup, 100-500+ events per city
2. **Meetup API** - 5 minutes setup, 50-200+ events per city

### **Phase 2: Additional APIs (Add Later)**
3. **Facebook Events API** - 10 minutes setup, 100-300+ events per city
4. **Google Calendar API** - 15 minutes setup, 50-150+ events per city

### **Phase 3: Optional APIs (Nice to Have)**
5. **NewsAPI** - For event announcements
6. **CitySpark API** - For local event aggregators

## 📊 **Expected Results by Phase**

### **Phase 1 (Eventbrite + Meetup):**
- **Before**: 0 events (blocked scrapers)
- **After**: 150-700+ events per city
- **Improvement**: ∞% (from 0 to hundreds)

### **Phase 2 (+ Facebook + Google):**
- **Before**: 150-700+ events per city
- **After**: 300-1,150+ events per city
- **Improvement**: 100-200% more events

### **Phase 3 (+ Optional APIs):**
- **Before**: 300-1,150+ events per city
- **After**: 400-1,500+ events per city
- **Improvement**: 30-50% more events

## 🚀 **Quick Start Commands**

### **1. Get Eventbrite API Key (5 minutes)**
```bash
# Go to: https://www.eventbrite.com/platform/api-keys/
# Sign up, create app, copy Private Token
# Add to Railway: EVENT_SCRAPER_EVENTBRITE_API_KEY=your_token
```

### **2. Get Meetup API Key (5 minutes)**
```bash
# Go to: https://www.meetup.com/meetup_api/
# Sign up, request API key, copy key
# Add to Railway: EVENT_SCRAPER_MEETUP_API_KEY=your_key
```

### **3. Deploy to Railway**
```bash
# Railway will automatically redeploy with new environment variables
# Check logs to see the improvement in event discovery
```

## 🔍 **Testing Your Setup**

After adding API keys, test your Railway deployment:

```bash
# Test the API endpoint
curl https://your-railway-app.railway.app/ping

# Test event scraping
curl "https://your-railway-app.railway.app/api/events?city=San%20Francisco&country=United%20States"
```

## 📈 **Monitoring Results**

### **Check Railway Logs:**
1. Go to Railway dashboard
2. Click on your service
3. Go to "Deployments" tab
4. Click on latest deployment
5. Check logs for event counts

### **Expected Log Messages:**
```
✅ Eventbrite API found 250 events
✅ Meetup API found 120 events
✅ Facebook API found 180 events
✅ Google Calendar API found 80 events
✅ Total events scraped: 630
```

## 🛡️ **Security Notes**

1. **Never commit API keys** to your repository
2. **Use Railway environment variables** for all sensitive data
3. **Rotate API keys** every 90 days
4. **Monitor usage** to avoid rate limits
5. **Use different keys** for different environments

## 🎯 **Success Metrics**

With API keys configured, you should see:

- **Event Discovery**: 300-1,500+ events per city (vs 0 before)
- **Data Quality**: Structured, reliable data from official APIs
- **Reliability**: 99%+ uptime (no bot detection issues)
- **Speed**: Faster data collection (no scraping delays)
- **Coverage**: Comprehensive event coverage across platforms

## 📞 **Troubleshooting**

### **Common Issues:**
1. **API key not working**: Check the key format and permissions
2. **Rate limits**: Reduce concurrent requests or upgrade API plan
3. **No events found**: Check city name format and API parameters
4. **Deployment issues**: Check Railway logs for error messages

### **Getting Help:**
1. Check the [API Keys Setup Guide](./API_KEYS_SETUP.md)
2. Review Railway deployment logs
3. Test API keys individually
4. Start with Eventbrite API for quick wins

With API keys configured in Railway, your event scraper will transform from **0 events** to **hundreds of events per city** with reliable, structured data!
