#!/usr/bin/env python3
"""
Development Environment Setup Script

Sets up the AI Event Scraper for local development with optimized settings
for scalable event collection across US cities.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from core.config import settings
from core.database import db
from core.models import Event, Location, ContactInfo, EventSource


def create_directories():
    """Create necessary directories for the project."""
    directories = [
        "data/cities",
        "data/samples", 
        "data/exports",
        "logs",
        "config/dev",
        "config/staging",
        "config/prod"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def create_env_file():
    """Create .env file with development settings."""
    env_content = """# AI Event Scraper - Development Configuration

# Environment
EVENT_SCRAPER_ENVIRONMENT=development
EVENT_SCRAPER_DEBUG=true

# Database
EVENT_SCRAPER_MONGODB_URL=mongodb://localhost:27017
EVENT_SCRAPER_MONGODB_DATABASE=event_scraper
EVENT_SCRAPER_MONGODB_MAX_POOL_SIZE=100
EVENT_SCRAPER_MONGODB_MIN_POOL_SIZE=10

# OpenAI Configuration
EVENT_SCRAPER_OPENAI_API_KEY=your_openai_api_key_here
EVENT_SCRAPER_OPENAI_MODEL=gpt-3.5-turbo
EVENT_SCRAPER_OPENAI_MAX_TOKENS=1000
EVENT_SCRAPER_OPENAI_TEMPERATURE=0.3

# Performance Settings (Optimized for Local Development)
EVENT_SCRAPER_MAX_CONCURRENT_REQUESTS=50
EVENT_SCRAPER_REQUEST_DELAY_SECONDS=0.5
EVENT_SCRAPER_MAX_RETRIES=3
EVENT_SCRAPER_TIMEOUT_SECONDS=30

# Concurrency and Performance
EVENT_SCRAPER_MAX_CONCURRENT_SCRAPERS=10
EVENT_SCRAPER_AI_BATCH_SIZE=20
EVENT_SCRAPER_DATABASE_BATCH_SIZE=100

# Rate Limiting
EVENT_SCRAPER_REQUESTS_PER_MINUTE=120
EVENT_SCRAPER_REQUESTS_PER_HOUR=1000

# Data Processing
EVENT_SCRAPER_ENABLE_AI_PROCESSING=true
EVENT_SCRAPER_ENABLE_DEDUPLICATION=true
EVENT_SCRAPER_CONFIDENCE_THRESHOLD=0.7

# Logging
EVENT_SCRAPER_LOG_LEVEL=INFO
EVENT_SCRAPER_LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Monitoring
EVENT_SCRAPER_HEALTH_CHECK_INTERVAL=60
EVENT_SCRAPER_METRICS_ENABLED=true

# City Database
EVENT_SCRAPER_US_CITIES_FILE=data/cities/us_cities_100k_plus.json
EVENT_SCRAPER_TARGET_CITIES_COUNT=300
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Created .env file with development settings")
    else:
        print("⚠️  .env file already exists, skipping creation")


def create_us_cities_database():
    """Create comprehensive US cities database."""
    cities_data = [
        {"name": "New York", "state": "NY", "population": 8336817, "latitude": 40.7128, "longitude": -74.0060},
        {"name": "Los Angeles", "state": "CA", "population": 3979576, "latitude": 34.0522, "longitude": -118.2437},
        {"name": "Chicago", "state": "IL", "population": 2693976, "latitude": 41.8781, "longitude": -87.6298},
        {"name": "Houston", "state": "TX", "population": 2320268, "latitude": 29.7604, "longitude": -95.3698},
        {"name": "Phoenix", "state": "AZ", "population": 1680992, "latitude": 33.4484, "longitude": -112.0740},
        {"name": "Philadelphia", "state": "PA", "population": 1584064, "latitude": 39.9526, "longitude": -75.1652},
        {"name": "San Antonio", "state": "TX", "population": 1547253, "latitude": 29.4241, "longitude": -98.4936},
        {"name": "San Diego", "state": "CA", "population": 1423851, "latitude": 32.7157, "longitude": -117.1611},
        {"name": "Dallas", "state": "TX", "population": 1343573, "latitude": 32.7767, "longitude": -96.7970},
        {"name": "San Jose", "state": "CA", "population": 1035317, "latitude": 37.3382, "longitude": -121.8863},
        {"name": "Austin", "state": "TX", "population": 978908, "latitude": 30.2672, "longitude": -97.7431},
        {"name": "Jacksonville", "state": "FL", "population": 949611, "latitude": 30.3322, "longitude": -81.6557},
        {"name": "Fort Worth", "state": "TX", "population": 918915, "latitude": 32.7555, "longitude": -97.3308},
        {"name": "Columbus", "state": "OH", "population": 905748, "latitude": 39.9612, "longitude": -82.9988},
        {"name": "Charlotte", "state": "NC", "population": 885708, "latitude": 35.2271, "longitude": -80.8431},
        {"name": "San Francisco", "state": "CA", "population": 873965, "latitude": 37.7749, "longitude": -122.4194},
        {"name": "Indianapolis", "state": "IN", "population": 887642, "latitude": 39.7684, "longitude": -86.1581},
        {"name": "Seattle", "state": "WA", "population": 749256, "latitude": 47.6062, "longitude": -122.3321},
        {"name": "Denver", "state": "CO", "population": 715522, "latitude": 39.7392, "longitude": -104.9903},
        {"name": "Washington", "state": "DC", "population": 705749, "latitude": 38.9072, "longitude": -77.0369}
    ]
    
    cities_file = Path("data/cities/us_cities_100k_plus.json")
    with open(cities_file, "w") as f:
        json.dump(cities_data, f, indent=2)
    
    print(f"✅ Created US cities database with {len(cities_data)} cities")


async def test_database_connection():
    """Test database connection and create indexes."""
    try:
        await db.connect()
        print("✅ Database connection successful")
        
        # Test basic operations
        from core.models import QueryRequest
        total_events = await db.get_event_count(QueryRequest())
        print(f"✅ Database contains {total_events} events")
        
        await db.disconnect()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def create_sample_events():
    """Create sample events for testing."""
    sample_events = [
        Event(
            title="Tech Meetup: AI and Machine Learning",
            description="Join us for an evening of discussions about the latest trends in AI and ML.",
            start_date=datetime.now() + timedelta(days=3, hours=18),
            location=Location(
                address="123 Tech Street",
                city="San Francisco",
                country="United States",
                venue_name="Tech Hub SF"
            ),
            contact_info=ContactInfo(
                email="contact@techmeetup.com",
                website="https://techmeetup.com"
            ),
            price="Free",
            category="Technology & IT",
            tags=["Tech Meetup", "AI", "Machine Learning"],
            confidence_score=0.9,
            sources=[EventSource(
                platform="meetup",
                url="https://meetup.com/tech-ai-ml",
                scraped_at=datetime.utcnow()
            )]
        )
    ]
    return sample_events


async def main():
    """Main setup function."""
    print("🚀 Setting up AI Event Scraper for Development")
    print("=" * 50)
    
    # Create directories
    print("\n📁 Creating project directories...")
    create_directories()
    
    # Create environment file
    print("\n⚙️  Setting up configuration...")
    create_env_file()
    
    # Create cities database
    print("\n🏙️  Creating US cities database...")
    create_us_cities_database()
    
    # Test database connection
    print("\n🗄️  Testing database connection...")
    db_ok = await test_database_connection()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎉 Development Environment Setup Complete!")
    print("\nNext steps:")
    print("1. Add your OpenAI API key to .env file")
    print("2. Start MongoDB: ./scripts/setup/start_mongodb.sh")
    print("3. Run tests: python -m pytest tests/")
    print("4. Start scraping: python main.py scrape 'New York' 'United States'")
    
    if not db_ok:
        print("\n⚠️  Database connection failed. Make sure MongoDB is running.")
        print("   Start MongoDB: ./scripts/setup/start_mongodb.sh")


if __name__ == "__main__":
    from datetime import datetime, timedelta
    asyncio.run(main())
