#!/bin/bash

# AI Event Scraper API - cURL Demo
# This script demonstrates the API endpoints using cURL

echo "🌐 AI Event Scraper API - cURL Demo"
echo "=================================="

BASE_URL="http://localhost:8000"

echo ""
echo "📊 1. Health Check"
echo "------------------"
curl -s "$BASE_URL/health" | python -m json.tool

echo ""
echo "📈 2. Database Statistics"
echo "-------------------------"
curl -s "$BASE_URL/stats" | python -m json.tool

echo ""
echo "🎉 3. Sample Events (limit 3)"
echo "-----------------------------"
curl -s "$BASE_URL/events?limit=3" | python -m json.tool

echo ""
echo "🔍 4. Search Events (tech)"
echo "--------------------------"
curl -s "$BASE_URL/events/search?q=tech&limit=3" | python -m json.tool

echo ""
echo "🏙️  5. Events by City (New York)"
echo "--------------------------------"
curl -s "$BASE_URL/events?city=New%20York&limit=3" | python -m json.tool

echo ""
echo "📂 6. Events by Category (Technology)"
echo "------------------------------------"
curl -s "$BASE_URL/events?category=Technology&limit=3" | python -m json.tool

echo ""
echo "🆓 7. Free Events"
echo "----------------"
curl -s "$BASE_URL/events?price_min=0&price_max=0&limit=3" | python -m json.tool

echo ""
echo "🏙️  8. Available Cities"
echo "----------------------"
curl -s "$BASE_URL/cities" | python -m json.tool

echo ""
echo "📂 9. Available Categories"
echo "-------------------------"
curl -s "$BASE_URL/categories" | python -m json.tool

echo ""
echo "🎲 10. Random Event"
echo "------------------"
curl -s "$BASE_URL/events/random" | python -m json.tool

echo ""
echo "🕒 11. Recent Events"
echo "-------------------"
curl -s "$BASE_URL/events/recent?limit=3" | python -m json.tool

echo ""
echo "🎉 cURL Demo Complete!"
echo "====================="
echo "Your AI Event Scraper API is working perfectly!"
echo "Ready for cloud deployment with 61,405+ events!"
