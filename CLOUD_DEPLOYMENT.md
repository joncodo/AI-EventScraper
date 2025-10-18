# Cloud Deployment Guide - Free Tier Setup

This guide will help you deploy the AI Event Scraper to the cloud using free tier services and populate it with data.

## 🆓 Free Tier Services

### Database: MongoDB Atlas (Free Tier)
- **512MB storage**
- **Shared clusters**
- **No credit card required**
- **Perfect for development and small production**

### Hosting Options (Choose One)

#### Option 1: Railway (Recommended)
- **$5/month free credits**
- **Automatic deployments from GitHub**
- **Built-in environment variables**
- **Custom domains**

#### Option 2: Render
- **Free tier available**
- **Automatic deployments**
- **Built-in monitoring**
- **Custom domains**

#### Option 3: Vercel
- **Free tier available**
- **Serverless functions**
- **Automatic deployments**
- **Global CDN**

## 🚀 Quick Deployment (Railway - Recommended)

### Step 1: Set Up MongoDB Atlas

1. **Create Account**
   - Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
   - Sign up for free account
   - No credit card required

2. **Create Cluster**
   - Click "Build a Database"
   - Choose "FREE" tier (M0)
   - Select a region close to you
   - Name your cluster (e.g., "ai-event-scraper")

3. **Create Database User**
   - Go to "Database Access"
   - Click "Add New Database User"
   - Choose "Password" authentication
   - Username: `ai-event-scraper`
   - Password: Generate a strong password
   - Database User Privileges: "Read and write to any database"

4. **Whitelist IP Address**
   - Go to "Network Access"
   - Click "Add IP Address"
   - Choose "Allow Access from Anywhere" (0.0.0.0/0)
   - Or add your specific IP

5. **Get Connection String**
   - Go to "Clusters"
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database user password
   - Replace `<dbname>` with `event_scraper`

### Step 2: Deploy to Railway

1. **Create Railway Account**
   - Go to [Railway](https://railway.app)
   - Sign up with GitHub

2. **Deploy from GitHub**
   - Click "New Project"
   - Choose "Deploy from GitHub repo"
   - Select your AI-EventScraper repository
   - Railway will automatically detect the Python app

3. **Configure Environment Variables**
   - Go to your project settings
   - Add these environment variables:
   ```
   MONGODB_URI=mongodb+srv://ai-event-scraper:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/event_scraper?retryWrites=true&w=majority
   OPENAI_API_KEY=your_openai_api_key_here
   ENVIRONMENT=production
   API_HOST=0.0.0.0
   API_PORT=$PORT
   MAX_CONCURRENT_REQUESTS=50
   REQUEST_DELAY_SECONDS=0.5
   AI_BATCH_SIZE=20
   ```

4. **Deploy**
   - Railway will automatically build and deploy
   - Your app will be available at `https://your-app-name.railway.app`

### Step 3: Populate Database

1. **Run Database Migration**
   ```bash
   # Clone your repository locally
   git clone https://github.com/your-username/AI-EventScraper.git
   cd AI-EventScraper
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment
   cp config/dev/env.example .env
   # Edit .env with your MongoDB Atlas connection string
   
   # Run migration script
   python scripts/migrate_to_cloud.py
   ```

2. **Start Scraping**
   ```bash
   # Scrape events for major cities
   python scripts/populate_cloud_db.py
   ```

## 🚀 Alternative: Render Deployment

### Step 1: Set Up MongoDB Atlas
(Same as Railway steps 1-5 above)

### Step 2: Deploy to Render

1. **Create Render Account**
   - Go to [Render](https://render.com)
   - Sign up with GitHub

2. **Create Web Service**
   - Click "New +"
   - Choose "Web Service"
   - Connect your GitHub repository
   - Select your AI-EventScraper repository

3. **Configure Service**
   - **Name**: `ai-event-scraper`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python api_server.py --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**
   ```
   MONGODB_URI=mongodb+srv://ai-event-scraper:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/event_scraper?retryWrites=true&w=majority
   OPENAI_API_KEY=your_openai_api_key_here
   ENVIRONMENT=production
   API_HOST=0.0.0.0
   API_PORT=$PORT
   MAX_CONCURRENT_REQUESTS=50
   REQUEST_DELAY_SECONDS=0.5
   AI_BATCH_SIZE=20
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy automatically
   - Your app will be available at `https://ai-event-scraper.onrender.com`

## 🚀 Alternative: Vercel Deployment

### Step 1: Set Up MongoDB Atlas
(Same as above)

### Step 2: Deploy to Vercel

1. **Create Vercel Account**
   - Go to [Vercel](https://vercel.com)
   - Sign up with GitHub

2. **Import Project**
   - Click "New Project"
   - Import your AI-EventScraper repository
   - Vercel will auto-detect Python

3. **Configure Environment Variables**
   ```
   MONGODB_URI=mongodb+srv://ai-event-scraper:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/event_scraper?retryWrites=true&w=majority
   OPENAI_API_KEY=your_openai_api_key_here
   ENVIRONMENT=production
   ```

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy automatically
   - Your app will be available at `https://ai-event-scraper.vercel.app`

## 📊 Database Population

### Option 1: Migrate Existing Data

If you have existing data locally:

```bash
# Export local data
python scripts/export_local_data.py

# Import to cloud database
python scripts/import_to_cloud.py
```

### Option 2: Fresh Data Collection

Start fresh with cloud scraping:

```bash
# Scrape events for major cities
python scripts/populate_cloud_db.py --cities "New York,Los Angeles,Chicago,Houston,Phoenix" --limit 1000
```

### Option 3: Sample Data

Load sample data for testing:

```bash
# Generate sample events
python scripts/generate_sample_data.py --count 1000
```

## 🔧 Environment Variables

### Required Variables

```bash
# Database
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/event_scraper?retryWrites=true&w=majority

# AI Processing
OPENAI_API_KEY=your_openai_api_key_here

# Application
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=$PORT
```

### Optional Variables

```bash
# Performance
MAX_CONCURRENT_REQUESTS=50
REQUEST_DELAY_SECONDS=0.5
AI_BATCH_SIZE=20

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# Monitoring
LOG_LEVEL=INFO
ENABLE_METRICS=true
```

## 🧪 Testing Your Deployment

### 1. Health Check
```bash
curl https://your-app-url.railway.app/health
```

### 2. API Documentation
Visit: `https://your-app-url.railway.app/docs`

### 3. Test Endpoints
```bash
# Get statistics
curl https://your-app-url.railway.app/stats

# Get events
curl https://your-app-url.railway.app/events?limit=5

# Search events
curl https://your-app-url.railway.app/events/search?q=tech
```

## 📈 Monitoring and Maintenance

### Railway
- Built-in metrics and logs
- Automatic deployments on git push
- Custom domains available

### Render
- Built-in monitoring dashboard
- Automatic deployments
- Health checks

### Vercel
- Built-in analytics
- Automatic deployments
- Global CDN

## 🔄 Continuous Deployment

All platforms support automatic deployments:

1. **Push to GitHub**: Any push to main branch triggers deployment
2. **Environment Variables**: Update in platform dashboard
3. **Database Changes**: Handled automatically by MongoDB Atlas

## 💰 Cost Breakdown (Free Tier)

### MongoDB Atlas
- **Free**: 512MB storage, shared clusters
- **Upgrade**: $9/month for 2GB storage

### Railway
- **Free**: $5/month credits
- **Usage**: ~$2-3/month for small app

### Render
- **Free**: 750 hours/month
- **Upgrade**: $7/month for always-on

### Vercel
- **Free**: 100GB bandwidth/month
- **Upgrade**: $20/month for Pro

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check MongoDB Atlas IP whitelist
   - Verify connection string
   - Check database user permissions

2. **Build Failures**
   - Check Python version compatibility
   - Verify requirements.txt
   - Check build logs

3. **Environment Variables**
   - Ensure all required variables are set
   - Check variable names and values
   - Restart service after changes

### Getting Help

1. Check platform logs
2. Verify environment variables
3. Test database connection
4. Check API endpoints

## 🎯 Next Steps

1. **Deploy**: Choose a platform and deploy
2. **Populate**: Run database population scripts
3. **Test**: Verify all endpoints work
4. **Monitor**: Set up monitoring and alerts
5. **Scale**: Upgrade as needed

---

**🎉 Your AI Event Scraper is now ready for the cloud!**
