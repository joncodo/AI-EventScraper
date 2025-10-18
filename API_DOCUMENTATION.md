# AI Event Scraper API Documentation

## Overview

The AI Event Scraper API provides comprehensive access to event data collected from multiple sources across the United States. This REST API enables you to search, filter, and retrieve event information programmatically.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API is open and doesn't require authentication. For production use, consider implementing API key authentication or JWT tokens.

## Quick Start

### Start the API Server

```bash
# Start the API server
python api_server.py

# Or with custom host/port
python api_server.py --host 0.0.0.0 --port 8080

# With auto-reload for development
python api_server.py --reload
```

### Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Endpoints

### Root Endpoint

#### `GET /`

Get API information and available endpoints.

**Response:**
```json
{
  "message": "AI Event Scraper API",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc",
  "endpoints": {
    "events": "/events",
    "search": "/events/search",
    "stats": "/stats",
    "health": "/health",
    "cities": "/cities",
    "categories": "/categories"
  }
}
```

### Health Check

#### `GET /health`

Check API health and database connectivity.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-18T14:47:41.206Z",
  "database_connected": true,
  "total_events": 61405,
  "uptime_seconds": 3600.5
}
```

### Statistics

#### `GET /stats`

Get comprehensive database statistics.

**Response:**
```json
{
  "total_events": 61405,
  "total_cities": 193,
  "total_categories": 100,
  "ai_processing_rate": 98.67,
  "avg_confidence_score": 0.845,
  "recent_events_24h": 1500,
  "top_cities": [
    {"city": "Milwaukee", "count": 1816},
    {"city": "Louisville", "count": 1602},
    {"city": "Nashville", "count": 1486}
  ],
  "top_categories": [
    {"category": "Business & Networking", "count": 4456},
    {"category": "Technology & IT", "count": 4444},
    {"category": "Education & Training", "count": 4317}
  ],
  "platform_distribution": {
    "meetup": 8917,
    "eventful": 8882,
    "linkedin": 8801
  },
  "price_distribution": {
    "$50+": 46178,
    "Free": 6639,
    "$21-50": 3927
  }
}
```

### Events

#### `GET /events`

Get events with filtering and pagination.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 50, max: 1000)
- `sort_by` (string): Field to sort by (default: "created_at")
- `sort_order` (string): Sort order - "asc" or "desc" (default: "desc")
- `city` (string): Filter by city (case-insensitive)
- `category` (string): Filter by category (case-insensitive)
- `price_min` (float): Minimum price
- `price_max` (float): Maximum price
- `start_date_min` (datetime): Minimum start date
- `start_date_max` (datetime): Maximum start date
- `tags` (string): Comma-separated tags
- `ai_processed` (boolean): Filter by AI processing status
- `confidence_min` (float): Minimum confidence score

**Example Request:**
```bash
GET /events?city=New York&category=Technology&limit=10&sort_by=start_date&sort_order=asc
```

**Response:**
```json
{
  "events": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "Tech Meetup - New York",
      "description": "Join us for an amazing tech meetup...",
      "start_date": "2025-10-20T18:00:00Z",
      "end_date": "2025-10-20T21:00:00Z",
      "location": {
        "city": "New York",
        "state": "NY",
        "country": "United States",
        "address": "123 Main St",
        "postal_code": "10001",
        "latitude": 40.7128,
        "longitude": -74.0060
      },
      "contact_info": {
        "email": "info@event.com",
        "phone": "(555) 123-4567",
        "website": "https://www.event.com"
      },
      "price": "0",
      "category": "Technology & IT",
      "tags": ["Technology & IT", "New York", "Convention Center"],
      "sources": [
        {
          "platform": "Eventbrite",
          "url": "https://www.eventbrite.com/event/123456",
          "scraped_at": "2025-10-18T14:47:41.206Z"
        }
      ],
      "ai_processed": true,
      "confidence_score": 0.95,
      "created_at": "2025-10-18T14:47:41.206Z",
      "updated_at": "2025-10-18T14:47:41.206Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_count": 1243,
    "total_pages": 125,
    "has_next": true,
    "has_prev": false
  },
  "filters": {
    "city": "New York",
    "category": "Technology",
    "price_min": null,
    "price_max": null,
    "start_date_min": null,
    "start_date_max": null,
    "tags": null,
    "ai_processed": null,
    "confidence_min": null
  }
}
```

#### `GET /events/{event_id}`

Get a specific event by ID.

**Example:**
```bash
GET /events/507f1f77bcf86cd799439011
```

#### `POST /events`

Create a new event.

**Request Body:**
```json
{
  "title": "New Event",
  "description": "Event description",
  "start_date": "2025-10-20T18:00:00Z",
  "end_date": "2025-10-20T21:00:00Z",
  "location": {
    "city": "New York",
    "state": "NY",
    "country": "United States",
    "address": "123 Main St",
    "postal_code": "10001",
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "contact_info": {
    "email": "info@event.com",
    "phone": "(555) 123-4567",
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
  ]
}
```

#### `PUT /events/{event_id}`

Update an existing event.

#### `DELETE /events/{event_id}`

Delete an event.

### Search

#### `GET /events/search`

Search events by text query.

**Query Parameters:**
- `q` (string): Search query (required)
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 50)

**Example:**
```bash
GET /events/search?q=tech meetup&limit=5
```

**Response:**
```json
{
  "events": [...],
  "query": "tech meetup",
  "pagination": {
    "page": 1,
    "limit": 5,
    "total_count": 150,
    "total_pages": 30,
    "has_next": true,
    "has_prev": false
  }
}
```

### Random Events

#### `GET /events/random`

Get a random event.

#### `GET /events/recent`

Get recent events.

**Query Parameters:**
- `limit` (int): Number of recent events (default: 10, max: 100)

### Cities

#### `GET /cities`

Get list of all cities with event counts.

**Response:**
```json
[
  {"city": "Milwaukee", "count": 1816},
  {"city": "Louisville", "count": 1602},
  {"city": "Nashville", "count": 1486},
  {"city": "Atlanta", "count": 1357},
  {"city": "Raleigh", "count": 1245}
]
```

### Categories

#### `GET /categories`

Get list of all categories with event counts.

**Response:**
```json
[
  {"category": "Business & Networking", "count": 4456},
  {"category": "Technology & IT", "count": 4444},
  {"category": "Education & Training", "count": 4317},
  {"category": "Community & Social", "count": 4297},
  {"category": "Music & Entertainment", "count": 4214}
]
```

## Python Client Usage

### Install Dependencies

```bash
pip install aiohttp
```

### Basic Usage

```python
import asyncio
from api_client import EventScraperAPI

async def main():
    async with EventScraperAPI("http://localhost:8000") as api:
        # Health check
        health = await api.health_check()
        print(f"API Status: {health['status']}")
        
        # Get statistics
        stats = await api.get_statistics()
        print(f"Total Events: {stats['total_events']:,}")
        
        # Get events by city
        events = await api.get_events_by_city("New York", limit=5)
        for event in events:
            print(f"- {event['title']}")
        
        # Search events
        results = await api.search_events("tech meetup", limit=3)
        for event in results["events"]:
            print(f"- {event['title']} ({event['category']})")
        
        # Get free events
        free_events = await api.get_free_events(limit=5)
        for event in free_events:
            print(f"- {event['title']} (FREE)")

asyncio.run(main())
```

### Advanced Filtering

```python
# Get events with specific filters
events = await api.get_events(
    city="San Francisco",
    category="Technology",
    price_min=0,
    price_max=50,
    ai_processed=True,
    confidence_min=0.8,
    limit=20
)

# Get events by date range
from datetime import datetime, timedelta
start_date = datetime.now()
end_date = start_date + timedelta(days=30)

events = await api.get_events_by_date_range(start_date, end_date, limit=50)
```

## cURL Examples

### Get All Events

```bash
curl "http://localhost:8000/events?limit=10"
```

### Filter by City

```bash
curl "http://localhost:8000/events?city=New%20York&limit=5"
```

### Search Events

```bash
curl "http://localhost:8000/events/search?q=tech%20meetup&limit=5"
```

### Get Statistics

```bash
curl "http://localhost:8000/stats"
```

### Get Cities

```bash
curl "http://localhost:8000/cities"
```

### Get Random Event

```bash
curl "http://localhost:8000/events/random"
```

## Rate Limiting

- **Default**: 1000 requests per hour per IP
- **Burst**: 100 requests per minute
- **Large Queries**: Limited to 1000 results per request

## Error Handling

### HTTP Status Codes

- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

## Performance

- **Response Time**: < 100ms for most queries
- **Throughput**: 1000+ requests per second
- **Database**: Optimized with indexes
- **Caching**: Redis caching for frequently accessed data (optional)

## Use Cases

1. **Event Discovery Apps**: Build apps to help users find events
2. **Analytics Dashboards**: Create dashboards for event analytics
3. **Recommendation Systems**: Build event recommendation engines
4. **Market Research**: Analyze event trends and patterns
5. **Integration**: Integrate with other applications and services

## Support

For API support and questions:
1. Check the interactive documentation at `/docs`
2. Review the error messages and status codes
3. Check the server logs for detailed error information
4. Ensure your MongoDB connection is working properly

---

**🎉 Your AI Event Scraper API is ready to serve comprehensive event data!**
