"""Mock events scraper for testing and demonstration purposes."""
import asyncio
import logging
from typing import List, Optional
from datetime import datetime, timedelta
import random

from core.models import Event, Location, ContactInfo, EventSource

logger = logging.getLogger(__name__)


class MockEventsScraper:
    """Mock scraper that generates sample events for testing."""
    
    def __init__(self):
        self.platform_name = "mock_events"
        
        # Sample event templates
        self.event_templates = [
            {
                "title": "Tech Meetup",
                "description": "Join us for an evening of networking and tech discussions",
                "category": "Technology",
                "tags": ["networking", "technology", "startup"]
            },
            {
                "title": "Art Gallery Opening",
                "description": "Opening reception for the new contemporary art exhibition",
                "category": "Arts & Culture",
                "tags": ["art", "culture", "exhibition"]
            },
            {
                "title": "Music Concert",
                "description": "Live music performance featuring local artists",
                "category": "Music",
                "tags": ["music", "concert", "live"]
            },
            {
                "title": "Food Festival",
                "description": "Taste the best local cuisine and craft beverages",
                "category": "Food & Drink",
                "tags": ["food", "festival", "local"]
            },
            {
                "title": "Fitness Workshop",
                "description": "Learn new fitness techniques and healthy living tips",
                "category": "Health & Wellness",
                "tags": ["fitness", "health", "workshop"]
            },
            {
                "title": "Business Conference",
                "description": "Annual business conference with industry leaders",
                "category": "Business",
                "tags": ["business", "conference", "networking"]
            },
            {
                "title": "Community Cleanup",
                "description": "Help keep our community clean and beautiful",
                "category": "Community",
                "tags": ["volunteer", "community", "environment"]
            },
            {
                "title": "Book Reading",
                "description": "Author reading and book signing event",
                "category": "Education",
                "tags": ["books", "education", "literature"]
            }
        ]
    
    async def scrape_events(
        self, 
        city: str, 
        country: str, 
        radius_km: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Event]:
        """Generate mock events for the specified city."""
        events = []
        
        try:
            # Generate 3-8 random events
            num_events = random.randint(3, 8)
            
            for i in range(num_events):
                event = await self._generate_mock_event(city, country, i)
                if event:
                    events.append(event)
            
            logger.info(f"Generated {len(events)} mock events for {city}")
            
        except Exception as e:
            logger.error(f"Error generating mock events: {e}")
        
        return events
    
    async def _generate_mock_event(self, city: str, country: str, index: int) -> Optional[Event]:
        """Generate a single mock event."""
        try:
            # Select random template
            template = random.choice(self.event_templates)
            
            # Generate random date within the next 30 days
            now = datetime.utcnow()
            days_ahead = random.randint(1, 30)
            event_date = now + timedelta(days=days_ahead)
            
            # Generate random time
            hour = random.randint(9, 20)
            minute = random.choice([0, 15, 30, 45])
            event_date = event_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Generate random venue
            venues = [
                "Community Center",
                "Downtown Convention Center", 
                "City Hall",
                "Local Library",
                "Park Pavilion",
                "University Campus",
                "Art Gallery",
                "Concert Hall"
            ]
            venue = random.choice(venues)
            
            # Generate address
            street_numbers = [100, 200, 300, 400, 500]
            street_names = ["Main St", "First Ave", "Oak St", "Pine St", "Elm St"]
            street_number = random.choice(street_numbers) + index * 10
            street_name = random.choice(street_names)
            address = f"{street_number} {street_name}, {city}, {country}"
            
            # Create event
            event = Event(
                title=f"{template['title']} - {city}",
                description=template['description'],
                start_date=event_date,
                end_date=event_date + timedelta(hours=random.randint(1, 4)),
                location=Location(
                    address=address,
                    city=city,
                    country=country,
                    latitude=round(random.uniform(40.0, 50.0), 6),
                    longitude=round(random.uniform(-80.0, -70.0), 6)
                ),
                category=template['category'],
                tags=template['tags'],
                contact_info=ContactInfo(
                    email=f"info@{city.lower().replace(' ', '')}events.com",
                    phone=f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                    website=f"https://{city.lower().replace(' ', '')}events.com"
                ),
                sources=[
                    EventSource(
                        platform="mock_events",
                        url=f"https://mock-events.com/events/{city.lower().replace(' ', '-')}-{index}",
                        scraped_at=datetime.utcnow(),
                        source_id=f"mock-{city.lower().replace(' ', '-')}-{index}"
                    )
                ],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            return event
            
        except Exception as e:
            logger.error(f"Error generating mock event: {e}")
            return None
