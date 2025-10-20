#!/usr/bin/env python3
"""
Test script to manually trigger the background worker and see what happens.
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

from worker.background_worker import BackgroundRefreshWorker

async def test_background_worker():
    """Test the background worker manually."""
    print("🧪 Testing Background Worker")
    print("=" * 50)
    
    try:
        # Create and start worker
        print("🔧 Creating BackgroundRefreshWorker...")
        worker = BackgroundRefreshWorker()
        
        print("🚀 Starting worker...")
        worker.start()
        
        print("⏳ Letting worker run for 30 seconds...")
        await asyncio.sleep(30)
        
        print("🛑 Stopping worker...")
        await worker.stop()
        
        print("✅ Test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_background_worker())
