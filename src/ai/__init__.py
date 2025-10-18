"""
AI module for AI Event Scraper

OpenAI-powered data processing and enhancement:
- Event categorization and tagging
- Data quality enhancement and validation
- Duplicate detection and merging
- Confidence scoring and validation

Features:
- Batch processing for efficiency
- Error handling and fallbacks
- Configurable AI models and parameters
- Cost optimization through smart batching
"""

from .ai_processor import AIProcessor, ai_processor

__all__ = ["AIProcessor", "ai_processor"]
