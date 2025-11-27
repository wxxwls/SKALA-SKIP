"""Batch job scheduler."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.logging import get_logger
from app.batch.jobs.news_ingest_job import run_news_ingest_job
from app.batch.jobs.embedding_refresh_job import run_embedding_refresh_job

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


def setup_scheduler() -> None:
    """Configure and start the job scheduler."""
    # News ingestion: Run every 6 hours
    scheduler.add_job(
        run_news_ingest_job,
        CronTrigger(hour="*/6"),
        id="news_ingest",
        name="News Ingestion Job",
        replace_existing=True,
    )

    # Embedding refresh: Run daily at 2 AM
    scheduler.add_job(
        run_embedding_refresh_job,
        CronTrigger(hour=2, minute=0),
        id="embedding_refresh",
        name="Embedding Refresh Job",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Batch scheduler started")


def shutdown_scheduler() -> None:
    """Shutdown the job scheduler."""
    scheduler.shutdown()
    logger.info("Batch scheduler stopped")
