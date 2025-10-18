# AI Event Scraper - Setup Guide

This guide will help you set up the AI Event Scraper system for development and production use.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **MongoDB** - [Download MongoDB](https://www.mongodb.com/try/download/community) or use [MongoDB Atlas](https://www.mongodb.com/atlas)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **OpenAI API Key** - [Get API Key](https://platform.openai.com/api-keys)

## Quick Setup (5 Minutes)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI-EventScraper
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp config/dev/env.example .env

# Edit the .env file with your settings
nano .env
```

**Required Environment Variables:**
```bash
# Database Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=event_scraper

# AI Processing
OPENAI_API_KEY=your_openai_api_key_here

# Performance Settings
MAX_CONCURRENT_REQUESTS=50
REQUEST_DELAY_SECONDS=0.5
AI_BATCH_SIZE=20
```

### 4. Start MongoDB

**Option A: Local MongoDB**
```bash
# Start MongoDB service
./scripts/setup/start_mongodb.sh

# Or manually
mongod --dbpath /path/to/your/db
```

**Option B: MongoDB Atlas (Cloud)**
```bash
# Update .env with your Atlas connection string
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/event_scraper?retryWrites=true&w=majority
```

### 5. Test the Installation

```bash
# Check system status
python main.py status

# Run a test scrape
python main.py scrape "New York" "United States" --limit 10

# Start the API server
python api_server.py
```

## Detailed Setup

### Database Setup

#### Local MongoDB Installation

**macOS (using Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb/brew/mongodb-community
```

**Ubuntu/Debian:**
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

**Windows:**
1. Download MongoDB Community Server from [mongodb.com](https://www.mongodb.com/try/download/community)
2. Run the installer
3. Start MongoDB service

#### MongoDB Atlas Setup (Recommended for Production)

1. **Create Account**: Sign up at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. **Create Cluster**: Choose a free tier or paid cluster
3. **Configure Access**: Add your IP address to the whitelist
4. **Create Database User**: Create a user with read/write permissions
5. **Get Connection String**: Copy the connection string and update your `.env` file

### OpenAI API Setup

1. **Create Account**: Sign up at [OpenAI Platform](https://platform.openai.com/)
2. **Get API Key**: Navigate to API Keys section and create a new key
3. **Add Credits**: Add credits to your account for API usage
4. **Update Configuration**: Add the API key to your `.env` file

### Environment Configuration

Create a `.env` file in the project root with the following variables:

```bash
# Environment
ENVIRONMENT=development

# Database
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=event_scraper

# AI Processing
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Performance Settings
MAX_CONCURRENT_REQUESTS=50
REQUEST_DELAY_SECONDS=0.5
AI_BATCH_SIZE=20

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
```

### Development Setup

#### Using Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # If available
```

#### Using Docker (Optional)

```bash
# Build Docker image
docker build -t ai-event-scraper .

# Run with Docker Compose
docker-compose up -d
```

## Verification

### Test Database Connection

```bash
python -c "
import asyncio
from src.core.database import db

async def test():
    await db.connect()
    print('✅ Database connection successful')
    await db.disconnect()

asyncio.run(test())
"
```

### Test OpenAI Integration

```bash
python -c "
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
response = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=[{'role': 'user', 'content': 'Hello, world!'}]
)
print('✅ OpenAI API connection successful')
"
```

### Test Scraping

```bash
# Test with a small scrape
python main.py scrape "New York" "United States" --limit 5 --verbose
```

### Test API Server

```bash
# Start API server
python api_server.py

# In another terminal, test the API
curl http://localhost:8000/health
curl http://localhost:8000/stats
```

## Production Setup

### Environment Configuration

For production, update your `.env` file:

```bash
# Environment
ENVIRONMENT=production

# Database (use MongoDB Atlas)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/event_scraper?retryWrites=true&w=majority
MONGODB_DATABASE=event_scraper

# Performance (optimized for production)
MAX_CONCURRENT_REQUESTS=100
REQUEST_DELAY_SECONDS=0.1
AI_BATCH_SIZE=50

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=your_secret_key_here
```

### Deployment Options

#### Option 1: Traditional Server

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv nginx

# Clone and setup
git clone <repository-url>
cd AI-EventScraper
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp config/prod/env.example .env
# Edit .env with production settings

# Start services
python api_server.py --host 0.0.0.0 --port 8000
```

#### Option 2: Docker Deployment

```bash
# Build and run
docker build -t ai-event-scraper .
docker run -d -p 8000:8000 --env-file .env ai-event-scraper
```

#### Option 3: Cloud Deployment

**AWS EC2:**
```bash
# Launch EC2 instance
# Install Docker
sudo yum install docker
sudo service docker start

# Deploy application
docker run -d -p 8000:8000 --env-file .env ai-event-scraper
```

**Google Cloud Run:**
```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-event-scraper

# Deploy to Cloud Run
gcloud run deploy --image gcr.io/PROJECT_ID/ai-event-scraper --platform managed
```

## Troubleshooting

### Common Issues

#### MongoDB Connection Failed

```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Check connection string
echo $MONGODB_URI

# Test connection
mongosh $MONGODB_URI
```

#### OpenAI API Errors

```bash
# Check API key
echo $OPENAI_API_KEY

# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

#### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python api_server.py --port 8001
```

#### Permission Errors

```bash
# Fix script permissions
chmod +x scripts/setup/*.sh

# Fix Python path issues
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Logs and Debugging

```bash
# Enable verbose logging
python main.py scrape "New York" "United States" --verbose

# Check API logs
python api_server.py --reload

# Check database logs
tail -f /var/log/mongodb/mongod.log
```

## Next Steps

After successful setup:

1. **Run Initial Scrape**: `python main.py scrape "New York" "United States"`
2. **Start API Server**: `python api_server.py`
3. **Test API**: Visit `http://localhost:8000/docs`
4. **Explore Data**: Use the API to query events
5. **Scale Up**: Configure for multiple cities and higher throughput

## Support

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review the logs for error messages
3. Ensure all prerequisites are installed
4. Verify environment configuration
5. Check network connectivity for external APIs

For additional help, please refer to the main [README.md](README.md) or create an issue in the repository.

---

**🎉 You're all set! The AI Event Scraper is ready to collect and serve event data.**
