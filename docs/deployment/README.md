# Deployment Guide

This guide covers deploying the AI Event Scraper to various platforms and environments.

## Table of Contents

- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Production Considerations](#production-considerations)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

## Local Development

### Prerequisites

- Python 3.11+
- MongoDB (local or Atlas)
- OpenAI API key

### Setup

```bash
# Clone repository
git clone <repository-url>
cd AI-EventScraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/dev/env.example .env
# Edit .env with your settings

# Start MongoDB (if local)
./scripts/setup/start_mongodb.sh

# Run the application
python main.py scrape "New York" "United States"
python api_server.py
```

## Docker Deployment

### Build Docker Image

```bash
# Build the image
docker build -t ai-event-scraper .

# Run the container
docker run -d \
  --name ai-event-scraper \
  -p 8000:8000 \
  --env-file .env \
  ai-event-scraper
```

### Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URI=mongodb://mongo:27017/event_scraper
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - mongo
    volumes:
      - ./data:/app/data

  mongo:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  mongo_data:
```

Run with Docker Compose:

```bash
docker-compose up -d
```

## Cloud Deployment

### AWS Deployment

#### EC2 Instance

```bash
# Launch EC2 instance (Ubuntu 22.04 LTS)
# Install Docker
sudo apt update
sudo apt install docker.io docker-compose

# Clone and deploy
git clone <repository-url>
cd AI-EventScraper
docker-compose up -d
```

#### ECS (Elastic Container Service)

```bash
# Build and push to ECR
aws ecr create-repository --repository-name ai-event-scraper
docker build -t ai-event-scraper .
docker tag ai-event-scraper:latest <account>.dkr.ecr.<region>.amazonaws.com/ai-event-scraper:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/ai-event-scraper:latest

# Deploy to ECS
aws ecs create-cluster --cluster-name ai-event-scraper
aws ecs create-service --cluster ai-event-scraper --service-name api --task-definition ai-event-scraper
```

#### Lambda (Serverless)

```bash
# Install serverless framework
npm install -g serverless

# Deploy
serverless deploy
```

### Google Cloud Platform

#### Cloud Run

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-event-scraper

# Deploy to Cloud Run
gcloud run deploy ai-event-scraper \
  --image gcr.io/PROJECT_ID/ai-event-scraper \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Compute Engine

```bash
# Create VM instance
gcloud compute instances create ai-event-scraper \
  --image-family ubuntu-2204-lts \
  --image-project ubuntu-os-cloud \
  --machine-type e2-medium

# Install Docker and deploy
gcloud compute ssh ai-event-scraper
sudo apt update && sudo apt install docker.io
git clone <repository-url>
cd AI-EventScraper
docker-compose up -d
```

### Azure Deployment

#### Container Instances

```bash
# Build and push to Azure Container Registry
az acr build --registry myregistry --image ai-event-scraper .

# Deploy to Container Instances
az container create \
  --resource-group myResourceGroup \
  --name ai-event-scraper \
  --image myregistry.azurecr.io/ai-event-scraper:latest \
  --ports 8000 \
  --environment-variables MONGODB_URI=<connection-string>
```

#### App Service

```bash
# Deploy to App Service
az webapp create \
  --resource-group myResourceGroup \
  --plan myAppServicePlan \
  --name ai-event-scraper \
  --deployment-local-git

# Configure environment variables
az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name ai-event-scraper \
  --settings MONGODB_URI=<connection-string>
```

## Production Considerations

### Environment Configuration

```bash
# Production environment variables
ENVIRONMENT=production
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/event_scraper
OPENAI_API_KEY=your_production_key
MAX_CONCURRENT_REQUESTS=100
REQUEST_DELAY_SECONDS=0.1
AI_BATCH_SIZE=50
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your_secret_key
```

### Security

- Use HTTPS in production
- Implement API authentication
- Set up rate limiting
- Use environment variables for secrets
- Enable database encryption
- Set up firewall rules
- Regular security updates

### Performance

- Use MongoDB Atlas for database
- Implement Redis caching
- Set up load balancing
- Use CDN for static assets
- Monitor resource usage
- Optimize database queries
- Implement connection pooling

### Scaling

- Horizontal scaling with load balancers
- Database sharding for large datasets
- Microservices architecture
- Container orchestration (Kubernetes)
- Auto-scaling policies
- Monitoring and alerting

## Monitoring and Maintenance

### Health Checks

```bash
# API health check
curl http://localhost:8000/health

# Database connectivity
python -c "from src.core.database import db; import asyncio; asyncio.run(db.connect())"
```

### Logging

```bash
# View application logs
docker logs ai-event-scraper

# View system logs
journalctl -u ai-event-scraper
```

### Backup

```bash
# MongoDB backup
mongodump --uri="mongodb://localhost:27017/event_scraper" --out=backup/

# Restore from backup
mongorestore --uri="mongodb://localhost:27017/event_scraper" backup/event_scraper/
```

### Updates

```bash
# Update application
git pull origin main
docker-compose down
docker-compose build
docker-compose up -d

# Update dependencies
pip install -r requirements.txt --upgrade
```

## Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check MongoDB status
sudo systemctl status mongod

# Check connection string
echo $MONGODB_URI

# Test connection
mongosh $MONGODB_URI
```

**API Not Responding**
```bash
# Check if service is running
ps aux | grep python

# Check port usage
netstat -tlnp | grep 8000

# Check logs
tail -f logs/app.log
```

**Memory Issues**
```bash
# Check memory usage
free -h

# Check process memory
ps aux --sort=-%mem | head

# Restart services
docker-compose restart
```

### Performance Issues

**Slow API Responses**
- Check database indexes
- Monitor query performance
- Implement caching
- Optimize database queries

**High Memory Usage**
- Monitor memory usage
- Implement connection pooling
- Optimize data structures
- Add memory limits

**Scraping Issues**
- Check rate limiting
- Monitor error rates
- Implement retry logic
- Update user agents

## Support

For deployment issues:

1. Check the logs for error messages
2. Verify environment configuration
3. Test database connectivity
4. Check network connectivity
5. Review security settings

For additional help, refer to the main [README](../README.md) or create an issue in the repository.

---

**Happy deploying! 🚀**
