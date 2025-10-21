#!/usr/bin/env python3
"""
Test Event Validation
Tests that our event validation correctly identifies real events vs non-events
"""

import asyncio
import sys
from datetime import datetime

# Add the src directory to the path
sys.path.append('src')

from scrapers.rss_scraper import RSSEventScraper

async def test_event_validation():
    """Test the event validation logic."""
    print("🧪 ============================================")
    print("🧪 TESTING EVENT VALIDATION")
    print("🧪 ============================================")
    
    scraper = RSSEventScraper()
    
    # Test cases
    test_cases = [
        # Real events (should return True)
        ("Tech Meetup: AI and Machine Learning", "Join us for an evening of networking and learning about AI and ML technologies. Date: March 15, 2024. Time: 6:00 PM. Location: Tech Hub Downtown."),
        ("Concert: Jazz Night at the Blue Note", "Experience an amazing jazz performance featuring local artists. Doors open at 7 PM. Tickets available online."),
        ("Workshop: Introduction to Python Programming", "Learn the basics of Python programming in this hands-on workshop. Perfect for beginners. Register now!"),
        ("Conference: Future of Technology 2024", "Annual technology conference featuring industry leaders. March 20-22, 2024. Early bird tickets available."),
        ("Art Exhibition Opening: Modern Masters", "Join us for the opening of our new art exhibition featuring works by contemporary artists. Free admission."),
        
        # Non-events (should return False)
        ("Top 10 AI Tools That Will Transform Your Life", "Here are the best AI tools you need to know about. These tools will make your life easier and more productive."),
        ("ProWritingAid VS Grammarly: Which is Better?", "A detailed comparison of two popular grammar checking tools. Find out which one is right for you."),
        ("Most Frequently Asked Questions About NFTs", "Everything you need to know about non-fungible tokens. Learn about blockchain technology and digital assets."),
        ("Breaking News: Tech Company Announces New Product", "A major technology company has announced a revolutionary new product that will change the industry."),
        ("How to Start a Successful Blog in 2024", "Complete guide to starting and growing a successful blog. Tips, tricks, and strategies for new bloggers."),
    ]
    
    print("🔍 Testing event validation logic...")
    print()
    
    correct_predictions = 0
    total_tests = len(test_cases)
    
    for i, (title, description) in enumerate(test_cases):
        is_event = scraper._is_likely_event(title, description)
        expected = i < 5  # First 5 are real events, last 5 are non-events
        
        status = "✅" if is_event == expected else "❌"
        if is_event == expected:
            correct_predictions += 1
        
        event_type = "EVENT" if is_event else "NON-EVENT"
        expected_type = "EVENT" if expected else "NON-EVENT"
        
        print(f"{status} Test {i+1}: {event_type} (expected: {expected_type})")
        print(f"   Title: {title[:50]}...")
        print(f"   Description: {description[:80]}...")
        print()
    
    accuracy = (correct_predictions / total_tests) * 100
    print(f"📊 Validation Test Results:")
    print(f"   ✅ Correct predictions: {correct_predictions}/{total_tests}")
    print(f"   📈 Accuracy: {accuracy:.1f}%")
    
    if accuracy >= 80:
        print("🎉 Event validation is working well!")
    else:
        print("⚠️  Event validation needs improvement")
    
    return accuracy >= 80

if __name__ == "__main__":
    asyncio.run(test_event_validation())
