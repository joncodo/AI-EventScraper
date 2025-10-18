"""
Core module for AI Event Scraper

Contains the fundamental components:
- Database: MongoDB connection and operations
- Models: Pydantic data models for events and requests
- Config: Application configuration and settings
"""

from .database import Database, db
from .models import Event, Location, ContactInfo, EventSource, ScrapeRequest, QueryRequest
from .config import Settings, settings

__all__ = [
    "Database", "db",
    "Event", "Location", "ContactInfo", "EventSource", "ScrapeRequest", "QueryRequest",
    "Settings", "settings"
]
