"""Main entry point for the AI Event Scraper."""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import app

if __name__ == "__main__":
    app()

