# Source Tracking Implementation

## Overview

This document describes the implementation of comprehensive data source tracking for the AI Event Scraper. Every event collected now requires and maintains specific information about where the data came from.

## Key Features Implemented

### 1. Enhanced EventSource Model

- **Fixed EventSource model** to include the `url` field that scrapers were using
- **Added validation** to ensure every event has at least one source
- **Source information includes**:
  - `platform`: The source platform (e.g., "eventbrite", "meetup", "facebook")
  - `url`: The URL of the source page/API endpoint
  - `scraped_at`: When the data was collected
  - `source_id`: Optional ID from the source platform

### 2. Database Enhancements

- **Added indexes** for source-related queries:
  - `sources.platform` for filtering by platform
  - `sources.url` for URL-based queries
- **New database methods**:
  - `find_events_by_source_platform()`: Query events by source platform
  - `get_source_statistics()`: Get aggregated statistics about data sources
- **Improved source merging**: When updating existing events, sources are merged intelligently to avoid duplicates

### 3. API Enhancements

- **New endpoints**:
  - `GET /sources`: Get statistics about data sources
  - `GET /events/source/{platform}`: Get events from a specific source platform
- **Enhanced existing endpoints**:
  - Added `source_platform` filter to the main `/events` endpoint
- **Updated API documentation** to include new source-related endpoints

### 4. Scraper Improvements

- **Fixed RSS scraper** to use correct `source_id` field instead of `event_id`
- **Verified all scrapers** are properly setting source information
- **Enhanced source merging** in scraper managers to avoid duplicate sources

## Data Model

### EventSource Structure
```python
class EventSource(BaseModel):
    platform: str  # e.g., "eventbrite", "meetup", "facebook"
    url: str  # URL of the source page/API endpoint
    scraped_at: datetime
    source_id: Optional[str] = None  # ID from the source platform
```

### Event Model Updates
```python
class Event(BaseModel):
    # ... other fields ...
    sources: List[EventSource] = Field(default_factory=list, min_items=1)
    
    @root_validator
    def validate_sources(cls, values):
        """Ensure every event has at least one source."""
        sources = values.get('sources', [])
        if not sources:
            raise ValueError("Every event must have at least one source")
        return values
```

## API Usage Examples

### Get Source Statistics
```bash
curl "http://localhost:8000/sources"
```

Response:
```json
{
  "source_platforms": [
    {
      "platform": "eventbrite",
      "source_count": 150,
      "unique_event_count": 120
    },
    {
      "platform": "meetup", 
      "source_count": 89,
      "unique_event_count": 75
    }
  ]
}
```

### Get Events by Source Platform
```bash
curl "http://localhost:8000/events/source/eventbrite?page=1&limit=10"
```

### Filter Events by Source Platform
```bash
curl "http://localhost:8000/events?source_platform=meetup"
```

## Database Queries

### Find Events by Source Platform
```python
events = await db.find_events_by_source_platform("eventbrite")
```

### Get Source Statistics
```python
stats = await db.get_source_statistics()
```

### Filter Events by Source in Main Query
```python
# Events from specific platform
filter_query = {"sources.platform": "meetup"}
```

## Validation

- **Every event must have at least one source** - enforced at the model level
- **Source URLs are unique** within an event to prevent duplicates
- **Source merging** when updating existing events preserves all unique sources

## Testing

A test script `test_source_tracking.py` has been created to verify:
- Source tracking functionality
- Source validation (events without sources are rejected)
- Database operations with sources
- API endpoint functionality

## Benefits

1. **Data Provenance**: Complete tracking of where each event came from
2. **Quality Control**: Ability to filter and analyze events by source
3. **Duplicate Prevention**: Intelligent merging of sources when updating events
4. **Analytics**: Source statistics for understanding data collection patterns
5. **Debugging**: Easy identification of problematic sources
6. **Compliance**: Full audit trail of data sources

## Migration Notes

- **Existing events** will continue to work, but new events must have sources
- **Database indexes** will be created automatically on next startup
- **API endpoints** are backward compatible with existing functionality
- **Scrapers** have been updated to ensure proper source tracking

## Future Enhancements

- Source reliability scoring
- Automatic source health monitoring
- Source-specific scraping schedules
- Enhanced source analytics and reporting

