"""Background worker for monitoring endpoints."""

import asyncio
import signal

import structlog

from app.config import get_settings

logger = structlog.get_logger()


class GracefulShutdown:
    """Handle graceful shutdown on SIGTERM/SIGINT."""

    def __init__(self):
        self.shutdown_event = asyncio.Event()
        self.tasks: set[asyncio.Task] = set()

    def register_signals(self):
        """Register signal handlers."""
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._signal_handler)

    def _signal_handler(self, signum: int, frame):
        """Handle shutdown signal."""
        logger.info("shutdown_signal_received", signal=signum)
        self.shutdown_event.set()

    async def wait_for_shutdown(self):
        """Wait for shutdown signal."""
        await self.shutdown_event.wait()

    async def cleanup(self):
        """Cleanup resources on shutdown."""
        logger.info("cleanup_started", task_count=len(self.tasks))

        for task in self.tasks:
            task.cancel()

        if self.tasks:
            await asyncio.wait(self.tasks, timeout=get_settings().graceful_shutdown_timeout)

        # TODO: Close database connections
        # TODO: Flush remaining logs

        logger.info("cleanup_complete")


async def monitoring_loop():
    """Main monitoring loop - checks all monitors periodically."""
    settings = get_settings()
    logger.info("monitoring_loop_started", interval=settings.check_interval)

    while True:
        try:
            # TODO: Fetch all active monitors from database
            # TODO: Perform health checks concurrently
            # TODO: Save results to database
            # TODO: Trigger alerts if needed

            logger.debug("monitoring_cycle_complete")
            await asyncio.sleep(settings.check_interval)

        except asyncio.CancelledError:
            logger.info("monitoring_loop_cancelled")
            break
        except Exception as e:
            logger.error("monitoring_loop_error", error=str(e), exc_info=True)
            await asyncio.sleep(5)


async def main():
    """Worker main entry point."""
    settings = get_settings()
    logger.info(
        "worker_starting",
        environment=settings.environment,
        check_interval=settings.check_interval,
    )

    shutdown_handler = GracefulShutdown()
    shutdown_handler.register_signals()

    # TODO: Initialize database
    # TODO: Run migrations
    # TODO: Seed default monitors

    monitor_task = asyncio.create_task(monitoring_loop())
    shutdown_handler.tasks.add(monitor_task)

    await shutdown_handler.wait_for_shutdown()

    await shutdown_handler.cleanup()

    logger.info("worker_stopped")


if __name__ == "__main__":
    asyncio.run(main())
