# API Reference

This document provides detailed information about the AI Event Scraper API endpoints, request/response formats, and usage examples.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API is open and doesn't require authentication. For production use, consider implementing API key authentication or JWT tokens.

## Response Format

All API responses follow a consistent format:

### Success Response

```json
{
  "data": { ... },
  "message": "Success",
  "status": 200
}
```

### Error Response

```json
{
  "error": "Error message",
  "status": 400,
  "details": { ... }
}
```

## Endpoints

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
    {"city": "Louisville", "count": 1602}
  ],
  "top_categories": [
    {"category": "Business & Networking", "count": 4456},
    {"category": "Technology & IT", "count": 4444}
  ],
  "platform_distribution": {
    "meetup": 8917,
    "eventful": 8882
  },
  "price_distribution": {
    "$50+": 46178,
    "Free": 6639
  }
}
```

### Events

#### `GET /events`

Get events with filtering and pagination.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `page` | integer | Page number | 1 |
| `limit` | integer | Items per page (max 1000) | 50 |
| `sort_by` | string | Field to sort by | "created_at" |
| `sort_order` | string | Sort order ("asc" or "desc") | "desc" |
| `city` | string | Filter by city (case-insensitive) | - |
| `category` | string | Filter by category (case-insensitive) | - |
| `price_min` | float | Minimum price | - |
| `price_max` | float | Maximum price | - |
| `start_date_min` | datetime | Minimum start date | - |
| `start_date_max` | datetime | Maximum start date | - |
| `tags` | string | Comma-separated tags | - |
| `ai_processed` | boolean | Filter by AI processing status | - |
| `confidence_min` | float | Minimum confidence score | - |

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

**Parameters:**
- `event_id` (string): The event ID

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Tech Meetup - New York",
  "description": "Join us for an amazing tech meetup...",
  "start_date": "2025-10-20T18:00:00Z",
  "end_date": "2025-10-20T21:00:00Z",
  "location": { ... },
  "contact_info": { ... },
  "price": "0",
  "category": "Technology & IT",
  "tags": ["Technology & IT", "New York"],
  "sources": [ ... ],
  "ai_processed": true,
  "confidence_score": 0.95,
  "created_at": "2025-10-18T14:47:41.206Z",
  "updated_at": "2025-10-18T14:47:41.206Z"
}
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

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "New Event",
  "description": "Event description",
  "start_date": "2025-10-20T18:00:00Z",
  "end_date": "2025-10-20T21:00:00Z",
  "location": { ... },
  "contact_info": { ... },
  "price": "25",
  "category": "Technology & IT",
  "tags": ["Technology", "Networking"],
  "sources": [ ... ],
  "ai_processed": false,
  "confidence_score": 0.0,
  "created_at": "2025-10-18T14:47:41.206Z",
  "updated_at": "2025-10-18T14:47:41.206Z"
}
```

#### `PUT /events/{event_id}`

Update an existing event.

**Parameters:**
- `event_id` (string): The event ID

**Request Body:**
```json
{
  "title": "Updated Event Title",
  "description": "Updated description",
  "price": "30"
}
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Updated Event Title",
  "description": "Updated description",
  "start_date": "2025-10-20T18:00:00Z",
  "end_date": "2025-10-20T21:00:00Z",
  "location": { ... },
  "contact_info": { ... },
  "price": "30",
  "category": "Technology & IT",
  "tags": ["Technology", "Networking"],
  "sources": [ ... ],
  "ai_processed": false,
  "confidence_score": 0.0,
  "created_at": "2025-10-18T14:47:41.206Z",
  "updated_at": "2025-10-18T15:30:00.000Z"
}
```

#### `DELETE /events/{event_id}`

Delete an event.

**Parameters:**
- `event_id` (string): The event ID

**Response:**
```json
{
  "message": "Event deleted successfully"
}
```

### Search

#### `GET /events/search`

Search events by text query.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `q` | string | Search query (required) | - |
| `page` | integer | Page number | 1 |
| `limit` | integer | Items per page | 50 |

**Example:**
```bash
GET /events/search?q=tech meetup&limit=5
```

**Response:**
```json
{
  "events": [ ... ],
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

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Random Event",
  "description": "A randomly selected event...",
  "start_date": "2025-10-20T18:00:00Z",
  "end_date": "2025-10-20T21:00:00Z",
  "location": { ... },
  "contact_info": { ... },
  "price": "0",
  "category": "Community & Social",
  "tags": ["Community", "Social"],
  "sources": [ ... ],
  "ai_processed": true,
  "confidence_score": 0.92,
  "created_at": "2025-10-18T14:47:41.206Z",
  "updated_at": "2025-10-18T14:47:41.206Z"
}
```

#### `GET /events/recent`

Get recent events.

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of recent events (max 100) | 10 |

**Response:**
```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "title": "Recent Event 1",
    "description": "A recently added event...",
    "start_date": "2025-10-20T18:00:00Z",
    "end_date": "2025-10-20T21:00:00Z",
    "location": { ... },
    "contact_info": { ... },
    "price": "0",
    "category": "Technology & IT",
    "tags": ["Technology", "Recent"],
    "sources": [ ... ],
    "ai_processed": true,
    "confidence_score": 0.95,
    "created_at": "2025-10-18T14:47:41.206Z",
    "updated_at": "2025-10-18T14:47:41.206Z"
  }
]
```

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

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

### Error Response Format

```json
{
  "detail": "Error message description",
  "status_code": 400,
  "timestamp": "2025-10-18T14:47:41.206Z"
}
```

### Common Error Messages

- `"Invalid event ID format"` - Event ID is not a valid ObjectId
- `"Event not found"` - Event with specified ID doesn't exist
- `"Validation error"` - Request data doesn't match expected format
- `"Database connection failed"` - Unable to connect to database
- `"Rate limit exceeded"` - Too many requests in a short time

## Rate Limiting

- **Default**: 1000 requests per hour per IP
- **Burst**: 100 requests per minute
- **Large Queries**: Limited to 1000 results per request

## Examples

### Python Client

```python
import asyncio
import aiohttp

async def get_events():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:8000/events?city=New York&limit=5') as response:
            data = await response.json()
            return data['events']

# Run the async function
events = asyncio.run(get_events())
```

### JavaScript Client

```javascript
async function getEvents() {
  const response = await fetch('http://localhost:8000/events?city=New York&limit=5');
  const data = await response.json();
  return data.events;
}

// Usage
getEvents().then(events => console.log(events));
```

### cURL Examples

```bash
# Get all events
curl "http://localhost:8000/events?limit=10"

# Filter by city
curl "http://localhost:8000/events?city=New%20York&limit=5"

# Search events
curl "http://localhost:8000/events/search?q=tech%20meetup&limit=5"

# Get statistics
curl "http://localhost:8000/stats"

# Get cities
curl "http://localhost:8000/cities"

# Get random event
curl "http://localhost:8000/events/random"
```

## Interactive Documentation

The API includes interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Support

For API support and questions:

1. Check the interactive documentation at `/docs`
2. Review the error messages and status codes
3. Check the server logs for detailed error information
4. Ensure your MongoDB connection is working properly

---

**🎉 Your AI Event Scraper API is ready to serve comprehensive event data!**
