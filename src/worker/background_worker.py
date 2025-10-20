"""Continuous background refresh worker.

Starts on application boot and continuously refreshes data, aiming to keep the
database as up-to-date as possible within box limits.

Environment variables:
- WORKER_LOOP_SECONDS: base delay between passes (default: 600)
- WORKER_MAX_BACKOFF_SECONDS: maximum backoff after failures (default: 900)
"""

import asyncio
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


async def _run_single_pass() -> None:
    """Run a single refresh pass using the shared cron routine."""
    logger.info("[worker] ============================================")
    logger.info("[worker] STARTING SINGLE REFRESH PASS")
    logger.info("[worker] ============================================")
    
    try:
        # Reuse the same implementation as our scheduled job
        logger.info("[worker] Importing cron_hourly_refresh module...")
        from scripts.cron_hourly_refresh import run_hourly_refresh
        logger.info("[worker] ✅ Successfully imported cron_hourly_refresh")
        
        logger.info("[worker] 🚀 Starting hourly refresh routine...")
        await run_hourly_refresh()
        logger.info("[worker] ✅ Refresh pass completed successfully")
        
    except Exception as e:
        logger.error(f"[worker] ❌ Error in refresh pass: {e}")
        logger.error(f"[worker] ❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"[worker] ❌ Traceback: {traceback.format_exc()}")
        raise


async def _refresh_loop(stop_event: asyncio.Event) -> None:
    base_delay = int(os.getenv("WORKER_LOOP_SECONDS", "600"))
    max_backoff = int(os.getenv("WORKER_MAX_BACKOFF_SECONDS", "900"))
    backoff = 5
    
    logger.info(f"[worker] ============================================")
    logger.info(f"[worker] BACKGROUND REFRESH LOOP STARTED")
    logger.info(f"[worker] Base delay: {base_delay} seconds")
    logger.info(f"[worker] Max backoff: {max_backoff} seconds")
    logger.info(f"[worker] ============================================")

    iteration_count = 0
    while not stop_event.is_set():
        iteration_count += 1
        try:
            logger.info(f"[worker] 🔄 Starting refresh loop iteration #{iteration_count}")
            await _run_single_pass()
            # Successful pass: reset backoff
            backoff = 5
            logger.info(f"[worker] ✅ Iteration #{iteration_count} completed successfully")
        except Exception as e:  # noqa: BLE001
            logger.error(f"[worker] ❌ Iteration #{iteration_count} failed: {e}")
            logger.error(f"[worker] ❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"[worker] ❌ Traceback: {traceback.format_exc()}")
            # Exponential backoff up to cap
            logger.info(f"[worker] ⏳ Backing off for {backoff} seconds...")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, max_backoff)
            continue

        # Idle briefly before the next pass
        try:
            # Allow immediate wakeup on shutdown
            logger.info(f"[worker] 😴 Sleeping {base_delay}s before next pass")
            await asyncio.wait_for(stop_event.wait(), timeout=max(0, base_delay))
        except asyncio.TimeoutError:
            logger.info(f"[worker] ⏰ Sleep timeout reached, starting next iteration")
            pass


class BackgroundRefreshWorker:
    """Lifecycle wrapper for the continuous background worker."""

    def __init__(self) -> None:
        self._task: Optional[asyncio.Task] = None
        self._stop_event: Optional[asyncio.Event] = None

    def start(self) -> None:
        logger.info("[worker] ============================================")
        logger.info("[worker] STARTING BACKGROUND REFRESH WORKER")
        logger.info("[worker] ============================================")
        
        if self._task is not None:
            logger.warning("[worker] ⚠️ Worker already started, ignoring start request")
            return
            
        try:
            self._stop_event = asyncio.Event()
            logger.info("[worker] ✅ Created stop event")
            
            self._task = asyncio.create_task(_refresh_loop(self._stop_event))
            logger.info("[worker] ✅ Created background task")
            
            logger.info("[worker] 🚀 Background refresh worker started successfully")
            logger.info("[worker] ============================================")
        except Exception as e:
            logger.error(f"[worker] ❌ Failed to start background worker: {e}")
            logger.error(f"[worker] ❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"[worker] ❌ Traceback: {traceback.format_exc()}")
            raise

    async def stop(self) -> None:
        logger.info("[worker] ============================================")
        logger.info("[worker] STOPPING BACKGROUND REFRESH WORKER")
        logger.info("[worker] ============================================")
        
        if self._task is None or self._stop_event is None:
            logger.warning("[worker] ⚠️ Worker not running, nothing to stop")
            return
            
        try:
            logger.info("[worker] 🛑 Setting stop event...")
            self._stop_event.set()
            
            logger.info("[worker] ⏳ Waiting for task to complete (30s timeout)...")
            await asyncio.wait_for(self._task, timeout=30)
            logger.info("[worker] ✅ Task completed gracefully")
            
        except asyncio.TimeoutError:
            logger.warning("[worker] ⚠️ Task did not complete in time, cancelling...")
            self._task.cancel()
        except Exception as e:  # noqa: BLE001
            logger.error(f"[worker] ❌ Error stopping worker: {e}")
            self._task.cancel()
        finally:
            self._task = None
            self._stop_event = None
            logger.info("[worker] 🛑 Background refresh worker stopped")
            logger.info("[worker] ============================================")


