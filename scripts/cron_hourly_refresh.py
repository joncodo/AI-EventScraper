#!/usr/bin/env python3
"""
Hourly refresh job

This job runs periodically to:
- Refresh the most valuable/popular data (top cities/categories) with latest info
- Scan for new events in those regions

Strategy:
- Determine top cities by event volume in the last 30 days (fallback to a static list)
- For each top city, scrape events for the next 60 days
- De-duplicate and upsert to the database
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
import hashlib

# Ensure src is on path
project_root = Path(__file__).resolve().parents[1]
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from core.database import db  # noqa: E402
from core.models import ScrapeRequest  # noqa: E402
from scrapers.scraper_manager import ScraperManager  # noqa: E402


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("cron_hourly_refresh")


DEFAULT_FALLBACK_CITIES: List[str] = [
    "New York", "Los Angeles", "Chicago", "San Francisco", "Boston",
    "Austin", "Seattle", "Toronto", "London", "Berlin"
]

# Curated list of major metros and large-venue hubs to bias towards popularity
MAJOR_METRO_CITIES: List[str] = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    "Austin", "Jacksonville", "San Francisco", "Columbus", "Fort Worth",
    "Indianapolis", "Charlotte", "Seattle", "Denver", "Washington"
]


async def get_top_cities(limit: int = 10) -> List[str]:
    """Return top cities by recent event volume. Fallback to a static list if unavailable.

    Uses events in the last 30 days as a proxy for popularity/volume.
    """
    try:
        if db.db is None:
            await db.connect()

        date_from = datetime.utcnow() - timedelta(days=30)
        pipeline = [
            {"$match": {"created_at": {"$gte": date_from}}},
            {"$group": {"_id": "$location.city", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]

        results = []
        async for row in db.db.events.aggregate(pipeline):
            city = row.get("_id")
            if city and isinstance(city, str) and city.strip():
                results.append(city)

        if results:
            # Blend major metros with data-driven top cities, keeping order and uniqueness
            blended: List[str] = []
            for city in (MAJOR_METRO_CITIES + results):
                if city not in blended:
                    blended.append(city)
            return blended[:limit]

        logger.warning("Top cities aggregation returned no results. Using fallback list.")
        return DEFAULT_FALLBACK_CITIES[:limit]
    except Exception as e:
        logger.warning(f"Failed to compute top cities: {e}. Using fallback list.")
        return DEFAULT_FALLBACK_CITIES[:limit]


POPULAR_KEYWORDS = [
    # Headliners / large acts indicators
    "u2", "taylor swift", "beyonce", "coldplay", "drake", "ed sheeran",
    # Large event types
    "festival", "conference", "summit", "expo", "convention", "world tour",
    # Large venues
    "stadium", "arena", "center", "centre", "amphitheater", "amphitheatre",
]


def _popularity_score_from_text(text: str) -> int:
    score = 0
    lower = (text or "").lower()
    for kw in POPULAR_KEYWORDS:
        if kw in lower:
            score += 1
    return score


async def refresh_city(scraper_manager: ScraperManager, city: str, country: str = "United States") -> int:
    """Scrape and upsert events for a single city. Returns number of saved/updated events."""
    try:
        logger.info(f"[cron] Begin city refresh: city='{city}', country='{country}'")
        # Define the date window to fetch upcoming events
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=60)

        request = ScrapeRequest(
            city=city,
            country=country,
            radius_km=75,
            start_date=start_date,
            end_date=end_date
        )

        events = await scraper_manager.scrape_all_events(request)
        logger.info(f"[cron] City '{city}': scraped {len(events)} events (pre-dedup)")
        if not events:
            logger.info(f"[cron] City '{city}': no events scraped")
            return 0

        # Prioritize logging/popularity to monitor impact (saving remains full to ensure coverage)
        popular_events = []
        for ev in events:
            title_score = _popularity_score_from_text(getattr(ev, "title", ""))
            venue_bits = [
                getattr(getattr(ev, "location", None), "address", ""),
                getattr(getattr(ev, "location", None), "city", ""),
            ]
            venue_score = _popularity_score_from_text(" ".join([v for v in venue_bits if v]))
            total_score = title_score + venue_score
            if total_score >= 2:
                popular_events.append(ev)

        if popular_events:
            logger.info(f"[cron] City '{city}': identified {len(popular_events)} potentially popular events")

        saved_ids = await scraper_manager.save_events_to_database(events)
        logger.info(f"[cron] City '{city}': saved/updated {len(saved_ids)} events")
        return len(saved_ids)
    except Exception as e:
        logger.error(f"[cron] Error refreshing city '{city}': {e}")
        return 0


async def run_hourly_refresh():
    """Main entry for the hourly refresh job."""
    logger.info("[cron] Starting hourly refresh job")

    # Ensure DB connection
    await db.connect()

    # Resolve top cities, bias towards where users are likely to watch
    top_cities = await get_top_cities(limit=int(os.getenv("CRON_TOP_CITIES_LIMIT", "12")))
    logger.info(f"[cron] Top cities to refresh: {top_cities}")

    scraper_manager = ScraperManager()

    # Limit concurrent city refreshes to avoid rate limits
    semaphore = asyncio.Semaphore(int(os.getenv("CRON_CITY_CONCURRENCY", "2")))

    async def _city_has_due_events(city_name: str, now_dt: datetime) -> bool:
        try:
            if db.db is None:
                await db.connect()
            filter_query = {
                "location.city": {"$regex": city_name, "$options": "i"},
                "next_refresh_at": {"$lte": now_dt}
            }
            due_count = await db.db.events.count_documents(filter_query)
            return due_count > 0
        except Exception as e:
            logger.warning(f"Failed checking due events for {city_name}: {e}")
            return True  # fail-open to avoid missing updates

    def _city_cadence_ok(city_name: str, now_dt: datetime) -> bool:
        force_every_hours = int(os.getenv("CRON_FORCE_REFRESH_EVERY_HOURS", "6"))
        if force_every_hours <= 0:
            return True
        hour = now_dt.hour
        # Create stable offset per city to spread load
        offset = int(hashlib.sha1(city_name.encode()).hexdigest(), 16) % force_every_hours
        return (hour % force_every_hours) == offset

    async def sem_task(city_name: str) -> int:
        async with semaphore:
            now_dt = datetime.utcnow()
            has_due = await _city_has_due_events(city_name, now_dt)
            cadence_ok = _city_cadence_ok(city_name, now_dt)
            if not has_due and not cadence_ok:
                logger.info(f"[cron] Skip city '{city_name}': no due events and cadence window not reached")
                return 0
            return await refresh_city(scraper_manager, city_name)

    tasks = [sem_task(city) for city in top_cities]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    total = 0
    for r in results:
        if isinstance(r, Exception):
            logger.error(f"Task error: {r}")
        else:
            total += int(r)

    logger.info(f"[cron] Refresh complete. Cities processed: {len(top_cities)}; total saved/updated events: {total}")

    try:
        await db.disconnect()
    except Exception:
        pass


def main():
    asyncio.run(run_hourly_refresh())


if __name__ == "__main__":
    main()


