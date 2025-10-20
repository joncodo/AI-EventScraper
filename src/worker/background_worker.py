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
    # Reuse the same implementation as our scheduled job
    from scripts.cron_hourly_refresh import run_hourly_refresh

    await run_hourly_refresh()


async def _refresh_loop(stop_event: asyncio.Event) -> None:
    base_delay = int(os.getenv("WORKER_LOOP_SECONDS", "600"))
    max_backoff = int(os.getenv("WORKER_MAX_BACKOFF_SECONDS", "900"))
    backoff = 5

    while not stop_event.is_set():
        try:
            await _run_single_pass()
            # Successful pass: reset backoff
            backoff = 5
        except Exception as e:  # noqa: BLE001
            logger.error(f"Background refresh pass failed: {e}")
            # Exponential backoff up to cap
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, max_backoff)
            continue

        # Idle briefly before the next pass
        try:
            # Allow immediate wakeup on shutdown
            await asyncio.wait_for(stop_event.wait(), timeout=max(0, base_delay))
        except asyncio.TimeoutError:
            pass


class BackgroundRefreshWorker:
    """Lifecycle wrapper for the continuous background worker."""

    def __init__(self) -> None:
        self._task: Optional[asyncio.Task] = None
        self._stop_event: Optional[asyncio.Event] = None

    def start(self) -> None:
        if self._task is not None:
            return
        self._stop_event = asyncio.Event()
        self._task = asyncio.create_task(_refresh_loop(self._stop_event))
        logger.info("Background refresh worker started")

    async def stop(self) -> None:
        if self._task is None or self._stop_event is None:
            return
        self._stop_event.set()
        try:
            await asyncio.wait_for(self._task, timeout=30)
        except Exception:  # noqa: BLE001
            self._task.cancel()
        finally:
            self._task = None
            self._stop_event = None
            logger.info("Background refresh worker stopped")


