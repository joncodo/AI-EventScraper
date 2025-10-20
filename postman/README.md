# AI Event Scraper - Postman Collections

This directory contains Postman collections for testing the AI Event Scraper API deployed on Railway.

## 📁 Files

- `AI-EventScraper.postman_collection.json` - Complete API collection with all endpoints
- `AI-EventScraper.postman_environment.json` - Environment variables for Railway deployment
- `README.md` - This documentation file

## 🚀 Quick Start

### 1. Import Collections

1. Open Postman
2. Click **Import** button
3. Select both files:
   - `AI-EventScraper.postman_collection.json`
   - `AI-EventScraper.postman_environment.json`

### 2. Set Environment

1. In Postman, click the environment dropdown (top right)
2. Select **"AI Event Scraper - Railway Environment"**
3. The `baseUrl` is pre-configured to: `https://ai-event-scraper-production.up.railway.app`

### 3. Test the API

Start with these endpoints to verify everything is working:

1. **Ping** - Simple connectivity test
2. **Health Check** - Detailed system status
3. **Stats** - See current event counts and system metrics

## 📊 Available Endpoints

### System Health
- `GET /` - Root endpoint with API info
- `GET /ping` - Simple ping test
- `GET /health` - Detailed health check
- `GET /info` - API version and details

### Events
- `GET /events` - List events with filtering and pagination
- `GET /events/search` - Search events by text query
- `GET /events/random` - Get random events for discovery
- `GET /events/recent` - Get recently added events
- `GET /events/{event_id}` - Get specific event by ID

### Analytics
- `GET /stats` - Overall system statistics
- `GET /cities` - Cities with event counts
- `GET /categories` - Event categories with counts
- `GET /tags` - Popular tags with counts
- `GET /sources` - Event sources with counts
- `GET /trends` - Trending events and categories

### Data Export
- `GET /export` - Export events in JSON/CSV format

## 🔧 Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `baseUrl` | `https://ai-event-scraper-production.up.railway.app` | Railway deployment URL |
| `eventId` | (empty) | Used for event-specific requests |
| `apiKey` | (empty) | For future API authentication |

## 📝 Example Requests

### Get Recent Events
```
GET {{baseUrl}}/events/recent?hours=24&limit=10
```

### Search for Tech Events
```
GET {{baseUrl}}/events/search?q=tech&limit=20
```

### Get Events by City
```
GET {{baseUrl}}/events?city=Los Angeles&limit=10
```

### Get System Stats
```
GET {{baseUrl}}/stats
```

## 🎯 Testing Workflow

1. **Start with Health Checks**
   - Ping → Health → Info

2. **Check System Status**
   - Stats → Cities → Categories

3. **Test Event Retrieval**
   - List Events → Search Events → Random Events

4. **Explore Analytics**
   - Trends → Sources → Tags

5. **Test Data Export**
   - Export Events (JSON/CSV)

## 🔍 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if Railway deployment is running
   - Verify the `baseUrl` in environment

2. **404 Not Found**
   - Ensure you're using the correct endpoint paths
   - Check if the API is deployed correctly

3. **Empty Results**
   - The system may still be collecting data
   - Check `/stats` to see current event counts

### Railway Deployment Status

Check the Railway deployment status at:
- Railway Dashboard: https://railway.app/dashboard
- Direct API: https://ai-event-scraper-production.up.railway.app/health

## 📈 Expected Results

With the current deployment, you should see:
- **Total Events**: 200+ events
- **Recent Activity**: Events from last 24 hours
- **Top Cities**: Los Angeles, Indianapolis, Charlotte, Phoenix
- **Top Categories**: Technology & IT, Arts & Culture, etc.
- **Top Sources**: RSS feeds

## 🔄 Updates

The collections are updated to match the current Railway deployment. If you make changes to the API, remember to update these collections accordingly.

## 📞 Support

If you encounter issues:
1. Check the Railway logs
2. Verify the API endpoints in `railway_complete.py`
3. Test with curl commands first
4. Check the `/health` endpoint for detailed status
