"""AI worker scheduler."""
from app.core.logging import get_logger

logger = get_logger(__name__)


class AIWorkerScheduler:
    """Scheduler for AI batch workers."""

    def __init__(self) -> None:
        self._running = False

    def start(self) -> None:
        """Start the AI worker scheduler."""
        logger.info("Starting AI worker scheduler")
        self._running = True

    def stop(self) -> None:
        """Stop the AI worker scheduler."""
        logger.info("Stopping AI worker scheduler")
        self._running = False

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running
