# Meetup OAuth 2.0 Setup Guide

## ⚠️ **Important: Meetup Changed Their API System**

As of June 2021, Meetup **no longer uses simple API keys**. They now require **OAuth 2.0 authentication**. This is more complex but still free.

---

## 🔑 **Step-by-Step Meetup OAuth Setup**

### **Step 1: Create Meetup OAuth App**

1. **Go to**: [Meetup API](https://www.meetup.com/api/)
2. **Sign in** to your Meetup account (or create one - it's free)
3. **Click**: "Create New Consumer" or "Register New App"
4. **Fill out the form**:
   - **Application Name**: `AI Event Scraper`
   - **Application Website**: `https://example.com` (or your website)
   - **Redirect URI**: `http://localhost:8080/callback`
   - **Description**: `Event discovery and aggregation service`
5. **Click**: "Register Consumer" or "Create App"

### **Step 2: Get Your OAuth Credentials**

After creating the app, you'll see:
- **Client ID** (this is like your "API key")
- **Client Secret** (keep this secure)
- **Redirect URI** (the one you entered)

### **Step 3: Configure in Your System**

Add to your `.env` file:
```bash
EVENT_SCRAPER_MEETUP_CLIENT_ID=your_client_id_here
EVENT_SCRAPER_MEETUP_CLIENT_SECRET=your_client_secret_here
EVENT_SCRAPER_MEETUP_REDIRECT_URI=http://localhost:8080/callback
```

---

## 🤔 **Is This Worth It?**

### **Pros:**
- ✅ **Free** - No costs
- ✅ **High Quality Events** - Professional meetups
- ✅ **50-200+ events per city**

### **Cons:**
- ❌ **More Complex** - Requires OAuth 2.0 setup
- ❌ **More Code** - Need to implement OAuth flow
- ❌ **User Authentication** - Requires user login

---

## 🎯 **Alternative: Skip Meetup for Now**

Since Meetup now requires OAuth 2.0 (which is more complex), you might want to focus on the **easier APIs first**:

### **Easier Free APIs:**
1. **Facebook Graph API** - Simple API key
2. **Google Calendar API** - Simple API key
3. **RSS/Feed APIs** - No API keys needed
4. **Local Government APIs** - No API keys needed

---

## 🚀 **Recommended Approach**

### **Start with Easy APIs:**
```bash
# These are simple API keys (not OAuth)
EVENT_SCRAPER_FACEBOOK_API_KEY=your_facebook_app_id
EVENT_SCRAPER_GOOGLE_API_KEY=your_google_api_key
```

### **Add Meetup Later:**
Once you have the basic system working, you can add Meetup OAuth 2.0 support.

---

## 📊 **Updated Priority List**

| **API** | **Difficulty** | **Setup Time** | **Events per City** | **Recommendation** |
|---------|----------------|----------------|-------------------|-------------------|
| **Facebook** | Easy | 10 minutes | 100-300+ | ✅ **Start Here** |
| **Google** | Easy | 5 minutes | 50-150+ | ✅ **Start Here** |
| **RSS/Feeds** | Easy | 0 minutes | 50-200+ | ✅ **Start Here** |
| **Meetup** | Hard | 30+ minutes | 50-200+ | ⏳ **Add Later** |

---

## 🎯 **My Recommendation**

**Start with Facebook and Google APIs first** - they're much easier to set up and will give you plenty of events. You can add Meetup OAuth 2.0 support later when you have more time.

Would you like me to help you set up the **Facebook API** and **Google API** first? These are much simpler and will give you 150-450+ events per city right away!

