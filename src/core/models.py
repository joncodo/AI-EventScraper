"""Data models for the AI Event Scraper."""
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema


class Location(BaseModel):
    """Location information for an event."""
    address: str
    city: str
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    venue_name: Optional[str] = None


class ContactInfo(BaseModel):
    """Contact information for an event."""
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    social_media: Dict[str, str] = Field(default_factory=dict)


class EventSource(BaseModel):
    """Information about where the event was scraped from."""
    platform: str  # e.g., "eventbrite", "meetup", "facebook"
    url: str
    scraped_at: datetime
    source_id: Optional[str] = None  # ID from the source platform


class Event(BaseModel):
    """Main event model."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    
    # Basic event information
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    
    # Location
    location: Location
    
    # Contact and pricing
    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    price: Optional[str] = None
    currency: Optional[str] = None
    
    # Categorization
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # Source information
    sources: List[EventSource] = Field(default_factory=list)
    
    # AI processing
    ai_processed: bool = False
    confidence_score: Optional[float] = None
    duplicate_of: Optional[PyObjectId] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Engagement and freshness
    view_count: int = 0
    popularity_score: Optional[float] = None
    staleness_tier: Optional[str] = None  # e.g., "high", "medium", "low"
    next_refresh_at: Optional[datetime] = None
    last_viewed_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ScrapeRequest(BaseModel):
    """Request model for scraping events."""
    city: str
    country: str
    radius_km: int = 100
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    categories: Optional[List[str]] = None


class QueryRequest(BaseModel):
    """Request model for querying events."""
    city: Optional[str] = None
    country: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 100
    offset: int = 0
