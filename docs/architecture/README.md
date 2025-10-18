# Architecture Reference

This document provides detailed information about the AI Event Scraper system architecture, design decisions, and technical implementation.

## System Overview

The AI Event Scraper is a distributed, scalable system designed to collect, process, and serve event data from multiple sources across the United States. The architecture follows modern microservices principles with clear separation of concerns.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI Event Scraper                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Web UI    │  │   Mobile    │  │   External  │            │
│  │             │  │     App     │  │     API     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│         │                │                │                   │
│         └────────────────┼────────────────┘                   │
│                          │                                    │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                REST API Layer                          │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │  │
│  │  │   FastAPI   │  │   Rate      │  │   Auth      │    │  │
│  │  │   Server    │  │   Limiting  │  │   Service   │    │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                          │                                    │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Business Logic Layer                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │  │
│  │  │   Event     │  │   AI        │  │   Search    │    │  │
│  │  │   Manager   │  │   Processor │  │   Engine    │    │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                          │                                    │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Data Collection Layer                     │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │  │
│  │  │ Eventbrite  │  │   Meetup    │  │  Facebook   │    │  │
│  │  │  Scraper    │  │  Scraper    │  │  Scraper    │    │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                          │                                    │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                Data Storage Layer                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │  │
│  │  │   MongoDB   │  │   Redis     │  │   File      │    │  │
│  │  │  Database   │  │   Cache     │  │   Storage   │    │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Data Collection Layer

**Purpose**: Collect event data from various sources

**Components**:
- **Eventbrite Scraper**: Collects events from Eventbrite platform
- **Meetup Scraper**: Gathers events from Meetup.com
- **Facebook Scraper**: Extracts events from Facebook Events
- **Scraper Manager**: Orchestrates and manages all scrapers

**Key Features**:
- Concurrent scraping for performance
- Rate limiting to respect platform policies
- Error handling and retry logic
- Data validation and cleaning

**Implementation**:
```python
class BaseScraper(ABC):
    @abstractmethod
    async def scrape_events(self, city: str, country: str, limit: int = 100) -> List[Event]:
        """Scrape events for the given location."""
        pass

class EventbriteScraper(BaseScraper):
    async def scrape_events(self, city: str, country: str, limit: int = 100) -> List[Event]:
        # Implementation for Eventbrite scraping
        pass
```

### 2. AI Processing Layer

**Purpose**: Enhance and categorize collected event data

**Components**:
- **AI Processor**: Uses OpenAI to process event data
- **Categorization Engine**: Automatically categorizes events
- **Deduplication Service**: Identifies and handles duplicate events
- **Quality Assessment**: Evaluates data quality and confidence

**Key Features**:
- Batch processing for efficiency
- Confidence scoring for data quality
- Automatic tagging and categorization
- Duplicate detection and resolution

**Implementation**:
```python
class AIProcessor:
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
    
    async def process_events(self, events: List[Event]) -> List[Event]:
        """Process events with AI for categorization and enhancement."""
        # Implementation for AI processing
        pass
```

### 3. Data Storage Layer

**Purpose**: Store and manage event data efficiently

**Components**:
- **MongoDB**: Primary database for event storage
- **Redis**: Caching layer for performance
- **File Storage**: Static assets and backups

**Key Features**:
- Optimized indexes for fast queries
- Horizontal scaling capabilities
- Data replication and backup
- Efficient data compression

**Database Schema**:
```javascript
{
  "_id": ObjectId,
  "title": String,
  "description": String,
  "start_date": Date,
  "end_date": Date,
  "location": {
    "address": String,
    "city": String,
    "state": String,
    "country": String,
    "latitude": Number,
    "longitude": Number,
    "venue_name": String
  },
  "contact_info": {
    "email": String,
    "phone": String,
    "website": String,
    "social_media": Object
  },
  "price": String,
  "currency": String,
  "category": String,
  "tags": [String],
  "sources": [{
    "platform": String,
    "url": String,
    "scraped_at": Date,
    "source_id": String
  }],
  "ai_processed": Boolean,
  "confidence_score": Number,
  "duplicate_of": ObjectId,
  "created_at": Date,
  "updated_at": Date
}
```

### 4. API Layer

**Purpose**: Provide programmatic access to event data

**Components**:
- **FastAPI Server**: RESTful API implementation
- **Rate Limiting**: Request throttling and management
- **Authentication**: API key and JWT token support
- **Documentation**: Auto-generated API docs

**Key Features**:
- High-performance async operations
- Comprehensive filtering and search
- Pagination for large datasets
- Real-time statistics and monitoring

**Implementation**:
```python
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="AI Event Scraper API", version="1.0.0")

@app.get("/events")
async def get_events(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=1000),
    city: Optional[str] = Query(None)
):
    """Get events with filtering and pagination."""
    # Implementation for event retrieval
    pass
```

## Data Flow

### 1. Event Collection Process

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Scraper   │───▶│   Raw Data  │───▶│ Validation  │
│   Manager   │    │   Storage   │    │   & Clean   │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                           ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   AI        │◀───│   Event     │───▶│   MongoDB   │
│ Processing  │    │   Queue     │    │  Database   │
└─────────────┘    └─────────────┘    └─────────────┘
```

### 2. API Request Process

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│   FastAPI   │───▶│   Business  │
│   Request   │    │   Server    │    │   Logic     │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                           ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Response  │◀───│   Data      │◀───│   MongoDB   │
│   to Client │    │   Processing│    │   Query     │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Database Design

### Indexes

```javascript
// Performance indexes
db.events.createIndex({ "location.city": 1 })
db.events.createIndex({ "category": 1 })
db.events.createIndex({ "start_date": 1 })
db.events.createIndex({ "price": 1 })
db.events.createIndex({ "ai_processed": 1 })

// Compound indexes
db.events.createIndex({ "location.city": 1, "category": 1 })
db.events.createIndex({ "start_date": 1, "location.city": 1 })
db.events.createIndex({ "category": 1, "start_date": 1 })

// Text search index
db.events.createIndex({
  "title": "text",
  "description": "text",
  "category": "text",
  "tags": "text"
})
```

### Data Relationships

```
Events
├── Location (embedded)
├── ContactInfo (embedded)
├── Sources (array of embedded)
├── Tags (array of strings)
└── DuplicateOf (reference to another event)
```

## Scalability Considerations

### Horizontal Scaling

**Database Scaling**:
- MongoDB sharding for large datasets
- Read replicas for query distribution
- Connection pooling for efficiency

**API Scaling**:
- Load balancing across multiple API instances
- Stateless API design for easy scaling
- Caching layer for frequently accessed data

**Processing Scaling**:
- Distributed scraping across multiple workers
- Queue-based processing for AI tasks
- Batch processing for efficiency

### Performance Optimization

**Database Optimization**:
- Proper indexing strategy
- Query optimization
- Data compression
- Connection pooling

**API Optimization**:
- Async/await for non-blocking operations
- Response caching
- Pagination for large datasets
- Rate limiting

**Scraping Optimization**:
- Concurrent requests with rate limiting
- Intelligent retry logic
- Data deduplication
- Incremental updates

## Security Architecture

### API Security

**Authentication**:
- API key authentication
- JWT token support
- Rate limiting per user
- IP whitelisting

**Data Protection**:
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- HTTPS enforcement

### Data Security

**Database Security**:
- Encrypted connections (TLS)
- User authentication and authorization
- Regular security updates
- Backup encryption

**API Security**:
- Request validation
- Response sanitization
- Error message filtering
- Logging and monitoring

## Monitoring and Observability

### Metrics Collection

**System Metrics**:
- API response times
- Database query performance
- Scraping success rates
- Error rates and types

**Business Metrics**:
- Events collected per day
- Data quality scores
- User engagement
- API usage patterns

### Logging Strategy

**Structured Logging**:
- JSON format for easy parsing
- Correlation IDs for request tracking
- Different log levels (DEBUG, INFO, WARN, ERROR)
- Centralized log aggregation

**Monitoring Alerts**:
- High error rates
- Performance degradation
- Database connection issues
- API rate limit breaches

## Technology Stack

### Backend Technologies

- **Python 3.11+**: Core programming language
- **FastAPI**: High-performance web framework
- **MongoDB**: Document database
- **Motor**: Async MongoDB driver
- **Pydantic**: Data validation and serialization
- **OpenAI API**: AI processing and enhancement

### Scraping Technologies

- **BeautifulSoup4**: HTML parsing
- **Selenium**: Dynamic content scraping
- **Requests**: HTTP client
- **aiohttp**: Async HTTP client
- **Fake UserAgent**: User agent rotation

### Development Tools

- **Typer**: CLI framework
- **Rich**: Terminal formatting
- **Pytest**: Testing framework
- **Black**: Code formatting
- **Flake8**: Linting

### Infrastructure

- **Docker**: Containerization
- **MongoDB Atlas**: Cloud database
- **Redis**: Caching layer
- **Nginx**: Reverse proxy
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards

## Design Patterns

### Repository Pattern

```python
class EventRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def find_by_city(self, city: str) -> List[Event]:
        """Find events by city."""
        pass
    
    async def create(self, event: Event) -> Event:
        """Create a new event."""
        pass
```

### Factory Pattern

```python
class ScraperFactory:
    @staticmethod
    def create_scraper(platform: str) -> BaseScraper:
        """Create a scraper for the specified platform."""
        scrapers = {
            "eventbrite": EventbriteScraper,
            "meetup": MeetupScraper,
            "facebook": FacebookScraper
        }
        return scrapers[platform]()
```

### Observer Pattern

```python
class EventProcessor:
    def __init__(self):
        self.observers = []
    
    def add_observer(self, observer):
        self.observers.append(observer)
    
    def notify_observers(self, event):
        for observer in self.observers:
            observer.update(event)
```

## Future Enhancements

### Planned Features

1. **Real-time Event Streaming**: WebSocket support for live updates
2. **Machine Learning Models**: Custom ML models for better categorization
3. **Advanced Analytics**: Event trend analysis and predictions
4. **Mobile SDK**: Native mobile app support
5. **GraphQL API**: Alternative query interface
6. **Event Recommendations**: Personalized event suggestions

### Scalability Improvements

1. **Microservices Architecture**: Break down into smaller services
2. **Event Sourcing**: Event-driven architecture
3. **CQRS**: Command Query Responsibility Segregation
4. **Message Queues**: Asynchronous processing
5. **CDN Integration**: Global content delivery
6. **Auto-scaling**: Dynamic resource allocation

## Best Practices

### Code Organization

- **Modular Design**: Clear separation of concerns
- **Dependency Injection**: Loose coupling between components
- **Interface Segregation**: Small, focused interfaces
- **Single Responsibility**: Each class has one reason to change

### Error Handling

- **Graceful Degradation**: System continues to work with partial failures
- **Circuit Breaker**: Prevent cascade failures
- **Retry Logic**: Automatic retry for transient failures
- **Comprehensive Logging**: Detailed error information

### Testing Strategy

- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Test system under load

---

**This architecture provides a solid foundation for scaling the AI Event Scraper to handle millions of events across hundreds of cities while maintaining high performance and reliability.**
