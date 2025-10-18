#!/usr/bin/env python3
"""
Cloud Deployment Helper Script

This script helps with the cloud deployment process by:
1. Validating environment variables
2. Testing database connection
3. Running database migrations
4. Starting the application

Usage:
    python scripts/deploy_to_cloud.py --validate
    python scripts/deploy_to_cloud.py --migrate
    python scripts/deploy_to_cloud.py --start
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from core.database import db
from core.config import settings

async def validate_environment():
    """Validate that all required environment variables are set."""
    print("🔍 Validating environment variables...")
    
    required_vars = [
        "MONGODB_URI",
        "OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    return True

async def test_database_connection():
    """Test connection to the cloud database."""
    print("🔍 Testing database connection...")
    
    try:
        await db.connect()
        await db.client.admin.command('ping')
        print("✅ Database connection successful")
        
        # Get database info
        db_info = await db.db.command("dbStats")
        event_count = await db.db.events.count_documents({})
        
        print(f"📊 Database: {db_info['db']}")
        print(f"📊 Events: {event_count}")
        print(f"📊 Size: {db_info['dataSize']} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    finally:
        await db.disconnect()

async def run_migrations():
    """Run database migrations and setup."""
    print("🔄 Running database migrations...")
    
    try:
        await db.connect()
        
        # Create indexes
        await db.db.events.create_index("location.city")
        await db.db.events.create_index("category")
        await db.db.events.create_index("start_date")
        await db.db.events.create_index("price")
        await db.db.events.create_index("ai_processed")
        await db.db.events.create_index([("location.city", 1), ("category", 1)])
        await db.db.events.create_index([("start_date", 1), ("location.city", 1)])
        await db.db.events.create_index([("category", 1), ("start_date", 1)])
        
        # Create text search index
        await db.db.events.create_index([
            ("title", "text"),
            ("description", "text"),
            ("category", "text"),
            ("tags", "text")
        ])
        
        print("✅ Database migrations completed")
        return True
        
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        return False
    finally:
        await db.disconnect()

async def start_application():
    """Start the application server."""
    print("🚀 Starting application server...")
    
    try:
        import uvicorn
        from api_server import app
        
        host = os.getenv("API_HOST", "0.0.0.0")
        port = int(os.getenv("API_PORT", "8000"))
        
        print(f"🌐 Starting server on {host}:{port}")
        uvicorn.run(app, host=host, port=port)
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return False

async def main():
    parser = argparse.ArgumentParser(description="Cloud deployment helper script")
    parser.add_argument("--validate", action="store_true", help="Validate environment variables")
    parser.add_argument("--test-db", action="store_true", help="Test database connection")
    parser.add_argument("--migrate", action="store_true", help="Run database migrations")
    parser.add_argument("--start", action="store_true", help="Start the application")
    parser.add_argument("--full-setup", action="store_true", help="Run full setup (validate, migrate, start)")
    
    args = parser.parse_args()
    
    if args.full_setup:
        print("🚀 Running full cloud deployment setup...")
        
        # Validate environment
        if not await validate_environment():
            sys.exit(1)
        
        # Test database connection
        if not await test_database_connection():
            sys.exit(1)
        
        # Run migrations
        if not await run_migrations():
            sys.exit(1)
        
        # Start application
        await start_application()
        
    elif args.validate:
        if not await validate_environment():
            sys.exit(1)
    elif args.test_db:
        if not await test_database_connection():
            sys.exit(1)
    elif args.migrate:
        if not await run_migrations():
            sys.exit(1)
    elif args.start:
        await start_application()
    else:
        print("Please specify an action. Use --help for options.")

if __name__ == "__main__":
    asyncio.run(main())
