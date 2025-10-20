# Get API Keys - Step by Step Guide

## 🎯 **Let's Get Your API Keys!**

I'll walk you through getting each API key step-by-step. We'll start with the most important ones that will give you the biggest impact.

---

## 🔑 **API Key #1: Eventbrite (Most Important)**

### **Why Eventbrite?**
- **Largest event platform** in the world
- **100-500+ events per city**
- **Free API** with generous limits
- **5 minutes setup**

### **Step-by-Step Instructions:**

#### **Step 1: Go to Eventbrite**
1. Open your browser
2. Go to: https://www.eventbrite.com/platform/api-keys/
3. Click **"Get Started"** or **"Sign Up"**

#### **Step 2: Create Account**
1. If you don't have an Eventbrite account:
   - Click **"Sign Up"**
   - Enter your email and password
   - Verify your email
2. If you already have an account:
   - Click **"Log In"**
   - Enter your credentials

#### **Step 3: Create App**
1. Once logged in, click **"Create App"**
2. Fill out the form:
   - **App Name**: "AI Event Scraper" (or any name you like)
   - **Description**: "Event data collection for AI Event Scraper"
   - **Website**: You can use your GitHub repo URL or any website
3. Click **"Create App"**

#### **Step 4: Get Your API Key**
1. After creating the app, you'll see your **"Private Token"**
2. **Copy this token** - it looks like: `ABC123DEF456GHI789`
3. **Save it somewhere safe** - you'll need it in a minute

#### **Step 5: Test Your Key**
Let's test if your Eventbrite API key works:

```bash
# Test your Eventbrite API key
curl "https://www.eventbriteapi.com/v3/events/search/?token=YOUR_TOKEN_HERE&location.address=San Francisco"
```

Replace `YOUR_TOKEN_HERE` with your actual token.

**✅ Success**: You should see JSON data with events
**❌ Error**: Check your token and try again

---

## 🔑 **API Key #2: Meetup (High Impact)**

### **Why Meetup?**
- **Large community events** database
- **50-200+ events per city**
- **Free API** with good limits
- **5 minutes setup**

### **Step-by-Step Instructions:**

#### **Step 1: Go to Meetup**
1. Open your browser
2. Go to: https://www.meetup.com/meetup_api/
3. Click **"Get Started"** or **"Sign Up"**

#### **Step 2: Create Account**
1. If you don't have a Meetup account:
   - Click **"Sign Up"**
   - Enter your email and password
   - Verify your email
2. If you already have an account:
   - Click **"Log In"**

#### **Step 3: Request API Key**
1. Once logged in, look for **"API Key"** section
2. Click **"Request API Key"**
3. Fill out the form:
   - **Application Name**: "AI Event Scraper"
   - **Description**: "Event data collection for AI Event Scraper"
   - **Website**: Your GitHub repo URL or any website
4. Click **"Submit Request"**

#### **Step 4: Get Your API Key**
1. You'll receive an email with your API key
2. **Copy the API key** - it looks like: `1234567890abcdef1234567890abcdef`
3. **Save it somewhere safe**

#### **Step 5: Test Your Key**
Let's test if your Meetup API key works:

```bash
# Test your Meetup API key
curl "https://api.meetup.com/find/upcoming_events?key=YOUR_KEY_HERE&location=San Francisco"
```

Replace `YOUR_KEY_HERE` with your actual key.

**✅ Success**: You should see JSON data with events
**❌ Error**: Check your key and try again

---

## 🔑 **API Key #3: Facebook Events (Social Events)**

### **Why Facebook Events?**
- **Massive social events** database
- **100-300+ events per city**
- **Free API** with good limits
- **10 minutes setup**

### **Step-by-Step Instructions:**

#### **Step 1: Go to Facebook Developers**
1. Open your browser
2. Go to: https://developers.facebook.com/
3. Click **"Get Started"** or **"Log In"**

#### **Step 2: Create Account**
1. If you don't have a Facebook account:
   - Click **"Sign Up"**
   - Create a Facebook account
2. If you already have an account:
   - Click **"Log In"**

#### **Step 3: Create App**
1. Once logged in, click **"Create App"**
2. Select **"Consumer"** as app type
3. Fill out the form:
   - **App Name**: "AI Event Scraper"
   - **App Contact Email**: Your email
   - **App Purpose**: "Event data collection"
4. Click **"Create App"**

#### **Step 4: Add Facebook Login**
1. In your app dashboard, click **"Add Product"**
2. Find **"Facebook Login"** and click **"Set Up"**
3. Select **"Web"** platform
4. Enter your website URL (can be your GitHub repo)

#### **Step 5: Get Your Access Token**
1. Go to **"App Settings"** → **"Basic"**
2. Copy your **"App ID"** and **"App Secret"**
3. To get an access token, go to: https://developers.facebook.com/tools/explorer/
4. Select your app
5. Click **"Generate Access Token"**
6. **Copy the access token** - it looks like: `EAABwzLixnjYBO...`

#### **Step 6: Test Your Key**
Let's test if your Facebook API key works:

```bash
# Test your Facebook API key
curl "https://graph.facebook.com/v18.0/search?type=event&q=events in San Francisco&access_token=YOUR_TOKEN_HERE"
```

Replace `YOUR_TOKEN_HERE` with your actual token.

**✅ Success**: You should see JSON data with events
**❌ Error**: Check your token and try again

---

## 🔑 **API Key #4: Google Calendar (Public Events)**

### **Why Google Calendar?**
- **Public calendar events**
- **50-150+ events per city**
- **Free API** with good limits
- **15 minutes setup**

### **Step-by-Step Instructions:**

#### **Step 1: Go to Google Cloud Console**
1. Open your browser
2. Go to: https://console.cloud.google.com/
3. Click **"Get Started"** or **"Sign In"**

#### **Step 2: Create Project**
1. If you don't have a Google account:
   - Create a Google account first
2. Once logged in, click **"Create Project"**
3. Enter project name: "AI Event Scraper"
4. Click **"Create"**

#### **Step 3: Enable Calendar API**
1. In your project dashboard, click **"APIs & Services"** → **"Library"**
2. Search for **"Calendar API"**
3. Click on **"Google Calendar API"**
4. Click **"Enable"**

#### **Step 4: Create Credentials**
1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"API Key"**
3. **Copy the API key** - it looks like: `AIzaSyABC123DEF456GHI789`
4. **Save it somewhere safe**

#### **Step 5: Test Your Key**
Let's test if your Google API key works:

```bash
# Test your Google API key
curl "https://www.googleapis.com/calendar/v3/calendars/en.usa%23holiday%40group.v.calendar.google.com/events?key=YOUR_KEY_HERE"
```

Replace `YOUR_KEY_HERE` with your actual key.

**✅ Success**: You should see JSON data with events
**❌ Error**: Check your key and try again

---

## 🔧 **Configure Your API Keys**

Now that you have your API keys, let's configure them:

### **For Local Development:**

1. **Create .env file:**
```bash
cd /Users/jon/Code/OUTGOING/AI-EventScraper
cp config/dev/env.example .env
```

2. **Edit .env file:**
```bash
nano .env
```

3. **Add your API keys:**
```bash
# Event Platform API Keys
EVENT_SCRAPER_EVENTBRITE_API_KEY=your_eventbrite_token_here
EVENT_SCRAPER_MEETUP_API_KEY=your_meetup_key_here
EVENT_SCRAPER_FACEBOOK_API_KEY=your_facebook_token_here
EVENT_SCRAPER_GOOGLE_API_KEY=your_google_key_here
```

### **For Railway Deployment:**

1. **Go to Railway dashboard:**
   - Go to: https://railway.app
   - Sign in to your account
   - Select your project

2. **Add Environment Variables:**
   - Click on your service
   - Go to "Variables" tab
   - Click "New Variable"
   - Add each API key:
     ```
     EVENT_SCRAPER_EVENTBRITE_API_KEY=your_eventbrite_token_here
     EVENT_SCRAPER_MEETUP_API_KEY=your_meetup_key_here
     EVENT_SCRAPER_FACEBOOK_API_KEY=your_facebook_token_here
     EVENT_SCRAPER_GOOGLE_API_KEY=your_google_key_here
     ```

---

## 🧪 **Test Your Setup**

Let's test if everything is working:

```bash
# Test your API keys
python -c "
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path('src')))

from core.config import settings

print('🔑 API Keys Status:')
print(f'Eventbrite: {\"✅ Configured\" if settings.eventbrite_api_key else \"❌ Not configured\"}')
print(f'Meetup: {\"✅ Configured\" if settings.meetup_api_key else \"❌ Not configured\"}')
print(f'Facebook: {\"✅ Configured\" if settings.facebook_api_key else \"❌ Not configured\"}')
print(f'Google: {\"✅ Configured\" if settings.google_api_key else \"❌ Not configured\"}')
"
```

---

## 🎯 **Priority Order**

### **Start Here (10 minutes total):**
1. **Eventbrite API** (5 minutes) - Biggest impact
2. **Meetup API** (5 minutes) - High impact

### **Add Later (25 minutes total):**
3. **Facebook Events API** (10 minutes) - Social events
4. **Google Calendar API** (15 minutes) - Public events

---

## 🆘 **Need Help?**

### **Common Issues:**
1. **"Invalid API key"**: Check if you copied the key correctly
2. **"Rate limit exceeded"**: Wait a few minutes and try again
3. **"Permission denied"**: Make sure you enabled the right APIs

### **Getting Help:**
1. **Check the official documentation** links above
2. **Most APIs have free tiers** with generous limits
3. **Start with Eventbrite** for the biggest impact
4. **Test each key** before moving to the next

---

## 🎉 **Expected Results**

With all 4 API keys configured, you should get:

- **San Francisco**: 500-900 events
- **New York**: 725-1,125 events
- **Chicago**: 375-725 events

**That's a massive improvement from 0 events!**

---

## 🚀 **Ready to Start?**

1. **Start with Eventbrite API** (5 minutes)
2. **Get Meetup API** (5 minutes)
3. **Deploy to Railway** with these keys
4. **See immediate results**: 150-700+ events per city

**Let's get your first API key now!**
