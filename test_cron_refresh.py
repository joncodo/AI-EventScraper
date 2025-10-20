#!/usr/bin/env python3
"""
Test script to manually run the cron refresh function.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add src to path
project_root = Path(__file__).resolve().parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)

async def test_cron_refresh():
    """Test the cron refresh function manually."""
    print("🧪 Testing Cron Refresh Function")
    print("=" * 50)
    
    try:
        print("📥 Importing cron_hourly_refresh...")
        from scripts.cron_hourly_refresh import run_hourly_refresh
        
        print("🚀 Running hourly refresh...")
        await run_hourly_refresh()
        
        print("✅ Cron refresh test completed")
        
    except Exception as e:
        print(f"❌ Cron refresh test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_cron_refresh())
