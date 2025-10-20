"""
Configuration settings for the AI Event Scraper.

Supports multiple environments (dev, staging, prod) with scalable settings
for local development and cloud deployment.
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from enum import Enum


class Environment(str, Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application settings with environment-specific configurations."""
    
    # Environment Configuration
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_uri: Optional[str] = None  # Alternative to mongodb_url for cloud deployments
    mongodb_database: str = "event_scraper"
    mongodb_max_pool_size: int = 100
    mongodb_min_pool_size: int = 10
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.3
    
    # Event Platform API Keys
    eventbrite_api_key: Optional[str] = None
    meetup_api_key: Optional[str] = None
    facebook_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # Additional API Keys
    newsapi_key: Optional[str] = None
    prnewswire_api_key: Optional[str] = None
    cityspark_api_key: Optional[str] = None
    eventful_api_key: Optional[str] = None
    
    # Scraping Configuration - Scalable Settings
    default_radius_km: int = 100
    max_concurrent_requests: int = 50  # Increased for better performance
    request_delay_seconds: float = 0.5  # Reduced for faster scraping
    max_retries: int = 3
    timeout_seconds: int = 30
    
    # Concurrency and Performance
    max_concurrent_scrapers: int = 10
    ai_batch_size: int = 20
    database_batch_size: int = 100
    
    # Rate Limiting
    requests_per_minute: int = 120
    requests_per_hour: int = 1000
    
    # User Agent and Headers
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # Data Processing
    enable_ai_processing: bool = True
    enable_deduplication: bool = True
    confidence_threshold: float = 0.7
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Monitoring and Health Checks
    health_check_interval: int = 60
    metrics_enabled: bool = True
    
    # City Database
    us_cities_file: str = "data/cities/us_cities_100k_plus.json"
    target_cities_count: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = "EVENT_SCRAPER_"
    
    def get_mongodb_config(self) -> dict:
        """Get MongoDB configuration for the current environment."""
        if self.environment == Environment.PRODUCTION:
            return {
                "url": self.mongodb_url,
                "database": self.mongodb_database,
                "max_pool_size": 200,
                "min_pool_size": 20,
                "retry_writes": True,
                "w": "majority"
            }
        else:
            return {
                "url": self.mongodb_url,
                "database": self.mongodb_database,
                "max_pool_size": self.mongodb_max_pool_size,
                "min_pool_size": self.mongodb_min_pool_size
            }
    
    def get_scraping_config(self) -> dict:
        """Get scraping configuration optimized for current environment."""
        if self.environment == Environment.PRODUCTION:
            return {
                "max_concurrent_requests": 100,
                "request_delay_seconds": 0.2,
                "max_retries": 5,
                "timeout_seconds": 45
            }
        else:
            return {
                "max_concurrent_requests": self.max_concurrent_requests,
                "request_delay_seconds": self.request_delay_seconds,
                "max_retries": self.max_retries,
                "timeout_seconds": self.timeout_seconds
            }


# Global settings instance
settings = Settings()
