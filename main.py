#!/usr/bin/env python3
"""
AI Event Scraper - Command Line Interface

A comprehensive event discovery and data collection platform that intelligently
scrapes, processes, and organizes events from multiple sources.

Usage:
    python main.py scrape "New York" "United States"
    python main.py query --city "Los Angeles" --limit 10
    python main.py status
    python main.py --help
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import and run the CLI
from cli import app

if __name__ == "__main__":
    app()
