"""News ingestion batch job."""
from app.core.logging import get_logger

logger = get_logger(__name__)


async def run_news_ingest_job() -> None:
    """Run news ingestion pipeline.

    This job:
    1. Fetches new articles from news APIs
    2. Cleans and preprocesses text
    3. Generates embeddings
    4. Stores in VectorDB
    """
    logger.info("Starting news ingestion job")

    # TODO: Implement news ingestion pipeline
    # 1. Call ai.pipelines.embedding_pipeline
    # 2. Store results in VectorDB

    logger.info("News ingestion job completed")
