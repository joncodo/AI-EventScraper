# Complete Railway Environment Variables

Copy and paste this into your Railway environment variables:

```
AI_BATCH_SIZE=20
API_HOST=0.0.0.0
API_PORT=$PORT
ENVIRONMENT=production
MAX_CONCURRENT_REQUESTS=50
MONGODB_URI=mongodb://mongo:PPGnjbCCrwCxRvvFQnMcMpumOkJOMoOw@trolley.proxy.rlwy.net:21533
REQUEST_DELAY_SECONDS=0.5
MONGODB_MAX_POOL_SIZE=100
DEBUG=false
RELOAD=false
SCRAPING_TIMEOUT=30
RETRY_ATTEMPTS=3
LOG_LEVEL=INFO
LOG_FORMAT=json
ENABLE_METRICS=true
HEALTH_CHECK_INTERVAL=30
SCRAPING_ENABLED=true
SCRAPING_CITIES=New York,Los Angeles,Chicago,Houston,Phoenix
SCRAPING_LIMIT_PER_CITY=1000
DATA_VALIDATION_ENABLED=true
DUPLICATE_DETECTION_ENABLED=true
QUALITY_THRESHOLD=0.8
OPENAI_API_KEY=your_openai_api_key_here
WORKER_LOOP_SECONDS=60
WORKER_MAX_BACKOFF_SECONDS=300
CRON_TOP_CITIES_LIMIT=30
CRON_CITY_CONCURRENCY=5
CRON_FORCE_REFRESH_EVERY_HOURS=3
MONGODB_DATABASE=event_scraper
EVENT_SCRAPER_EVENTBRITE_API_KEY=your_eventbrite_api_key_here
```

## API Keys Setup

The following API keys are configured but may need to be obtained:

- **Eventbrite API Key**: ✅ Configured (see environment variables)
- **Meetup API Key**: ❌ Not configured (optional)
- **Facebook API Key**: ❌ Not configured (optional)
- **Google API Key**: ❌ Not configured (optional)

## Notes

1. The Eventbrite API key is already configured and working
2. Other API keys are optional and the scrapers will skip them if not configured
3. The RSS and iCal scrapers don't require API keys
4. The local events scrapers use public APIs that don't require keys