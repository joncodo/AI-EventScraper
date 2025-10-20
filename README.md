# AI Event Scraper

A comprehensive event discovery and data collection platform that intelligently scrapes, processes, and organizes events from multiple sources across the United States.

## Overview

The AI Event Scraper is a production-ready system designed to collect, process, and serve event data at scale. It combines web scraping capabilities with AI-powered data enhancement to provide clean, categorized, and searchable event information.

### Key Features Here

- **Multi-Platform Scraping**: Collects events from Eventbrite, Meetup, Facebook Events, and other major platforms
- **AI-Powered Processing**: Uses OpenAI to categorize, tag, and enhance event data quality
- **Scalable Architecture**: Built to handle millions of events across hundreds of cities
- **RESTful API**: Complete API for accessing and querying event data
- **Real-time Processing**: Continuous data collection and updates
- **Geographic Coverage**: Targets 300+ US cities with 100k+ population

## Quick Start

### Prerequisites

- Python 3.11+
- MongoDB (local or Atlas)
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI-EventScraper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp config/dev/env.example .env
   # Edit .env with your MongoDB URL and OpenAI API key
   ```

4. **Start MongoDB** (if running locally)
   ```bash
   ./scripts/setup/start_mongodb.sh
   ```

5. **Run the scraper**
   ```bash
   python main.py scrape "New York" "United States"
   ```

6. **Start the API server**
   ```bash
   python api_server.py
   ```

## Architecture

The system is built with a modular, scalable architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Scrapers  │───▶│   AI Processor   │───▶│   MongoDB       │
│                 │    │                  │    │                 │
│ • Eventbrite    │    │ • Categorization │    │ • Auto-scaling  │
│ • Meetup        │    │ • Deduplication  │    │ • Sharding      │
│ • Facebook      │    │ • Tag Extraction │    │ • Replication   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   REST API      │
                       │                 │
                       │ • FastAPI       │
                       │ • Swagger Docs  │
                       │ • Rate Limiting │
                       └─────────────────┘
```

## Project Structure

```
AI-EventScraper/
├── src/                    # Source code
│   ├── core/              # Core components (models, database, config)
│   ├── scrapers/          # Event scraping modules
│   ├── ai/                # AI processing modules
│   └── utils/             # Utility functions
├── tests/                 # Test suites
├── docs/                  # Documentation
├── scripts/               # Setup and automation scripts
├── data/                  # Data files and samples
├── config/                # Configuration files
├── main.py               # CLI entry point
├── api_server.py         # API server
└── requirements.txt      # Python dependencies
```

## Usage

### Command Line Interface

The CLI provides easy access to all system functionality:

```bash
# Scrape events for a city
python main.py scrape "Los Angeles" "United States"

# Query events from database
python main.py query --city "Chicago" --category "Technology" --limit 20

# Check system status
python main.py status

# View configuration
python main.py config
```

### API Usage

The REST API provides programmatic access to all event data:

```bash
# Get all events
curl "http://localhost:8000/events?limit=10"

# Search events
curl "http://localhost:8000/events/search?q=tech%20meetup"

# Get statistics
curl "http://localhost:8000/stats"
```

### Python Client

```python
import asyncio
from api_client import EventScraperAPI

async def main():
    async with EventScraperAPI("http://localhost:8000") as api:
        # Get events by city
        events = await api.get_events_by_city("New York", limit=10)
        for event in events:
            print(f"- {event['title']}")

asyncio.run(main())
```

## Configuration

### Environment Variables

```bash
# Database
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=event_scraper

# AI Processing
OPENAI_API_KEY=your_openai_api_key_here

# Performance
MAX_CONCURRENT_REQUESTS=50
REQUEST_DELAY_SECONDS=0.5
AI_BATCH_SIZE=20
```

### Scaling Configuration

For production deployment:

```bash
# Production settings
ENVIRONMENT=production
MAX_CONCURRENT_REQUESTS=100
MONGODB_MAX_POOL_SIZE=200
```

## Data Model

Events are stored with comprehensive information:

```json
{
  "title": "Tech Meetup - New York",
  "description": "Join us for an amazing tech meetup...",
  "start_date": "2025-10-20T18:00:00Z",
  "end_date": "2025-10-20T21:00:00Z",
  "location": {
    "city": "New York",
    "state": "NY",
    "country": "United States",
    "address": "123 Main St",
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "contact_info": {
    "email": "info@event.com",
    "website": "https://www.event.com"
  },
  "price": "25",
  "category": "Technology & IT",
  "tags": ["Technology", "Networking"],
  "sources": [
    {
      "platform": "Eventbrite",
      "url": "https://www.eventbrite.com/event/123456",
      "scraped_at": "2025-10-18T14:47:41.206Z"
    }
  ],
  "ai_processed": true,
  "confidence_score": 0.95
}
```

## Performance

### Current Benchmarks

- **Scraping Speed**: 1000+ events/hour per city
- **AI Processing**: 20 events/batch, 95% accuracy
- **Database Queries**: <100ms response time
- **API Throughput**: 1000+ requests/second

### Scaling Targets

- **Cities**: 300+ concurrent scraping
- **Events**: 1M+ events/day processing
- **API**: 10,000+ requests/minute
- **Uptime**: 99.9% availability

## Deployment

### Local Development

```bash
# Start MongoDB
./scripts/setup/start_mongodb.sh

# Run scraper
python main.py scrape "New York" "United States"

# Start API
python api_server.py --reload
```

### Production

```bash
# Using Docker
docker build -t ai-event-scraper .
docker run -p 8000:8000 ai-event-scraper

# Using uvicorn directly
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Cloud Deployment

The system is designed for easy deployment to any cloud platform:

- **AWS**: EC2, ECS, Lambda
- **Google Cloud**: Compute Engine, Cloud Run
- **Azure**: Virtual Machines, Container Instances
- **MongoDB Atlas**: Cloud database hosting

### Scheduled hourly refresh

The service includes an hourly background job that refreshes popular locations and scans for new events.

- Local run: `make cron-hourly`
- Cloud (Render): configured as a cron job named `hourly-refresh` with schedule `0 * * * *` in `render.yaml`.
- Cloud (Railway): add a cron service named `hourly-refresh` with schedule `0 * * * *` executing `python scripts/cron_hourly_refresh.py`. See `railway.json` example.

## API Documentation

Complete API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test suites
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/e2e/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Email**: support@ai-eventscraper.com

---

**Built for scale. Ready for production. 🚀**
