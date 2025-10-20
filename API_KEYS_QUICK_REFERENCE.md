# API Keys Quick Reference

## 🚀 **Quick Start - Get Your First 2 API Keys (10 minutes)**

### **1. Eventbrite API (5 minutes) - BIGGEST IMPACT**
1. Go to: https://www.eventbrite.com/platform/api-keys/
2. Sign up/Log in
3. Click "Create App"
4. Fill out form (any name/description)
5. Copy your **Private Token**
6. Test: `curl "https://www.eventbriteapi.com/v3/events/search/?token=YOUR_TOKEN&location.address=San Francisco"`

### **2. Meetup API (5 minutes) - HIGH IMPACT**
1. Go to: https://www.meetup.com/meetup_api/
2. Sign up/Log in
3. Click "Request API Key"
4. Fill out form (any name/description)
5. Copy your **API Key** from email
6. Test: `curl "https://api.meetup.com/find/upcoming_events?key=YOUR_KEY&location=San Francisco"`

---

## 🔧 **Configure in Railway (2 minutes)**

1. Go to Railway dashboard
2. Select your project
3. Go to "Variables" tab
4. Add these variables:
   ```
   EVENT_SCRAPER_EVENTBRITE_API_KEY=your_eventbrite_token_here
   EVENT_SCRAPER_MEETUP_API_KEY=your_meetup_key_here
   ```

---

## 🎯 **Expected Results**

- **Before**: 0 events (blocked scrapers)
- **After**: 150-700+ events per city
- **Improvement**: ∞% (from 0 to hundreds)

---

## 🆘 **Need Help?**

- **Eventbrite**: https://www.eventbrite.com/platform/api-keys/
- **Meetup**: https://www.meetup.com/meetup_api/
- **Full Guide**: See `GET_API_KEYS_STEP_BY_STEP.md`

---

## 🚀 **Ready to Start?**

**Start with Eventbrite API now - it's the biggest impact!**
