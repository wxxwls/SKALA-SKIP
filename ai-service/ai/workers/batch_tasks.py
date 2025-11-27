"""Batch task definitions for AI workers."""
from typing import List, Dict, Any

from app.core.logging import get_logger

logger = get_logger(__name__)


async def process_embedding_batch(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process a batch of documents for embedding."""
    from ai.pipelines.embedding_pipeline import EmbeddingPipeline

    pipeline = EmbeddingPipeline()
    return pipeline.run(documents)


async def process_sentiment_batch(texts: List[str]) -> List[Dict[str, float]]:
    """Process a batch of texts for sentiment analysis."""
    from ai.services.sentiment_service import SentimentService

    service = SentimentService()
    return service.analyze_texts(texts)


async def process_topic_extraction(documents: List[str]) -> List[Dict]:
    """Process documents for topic extraction."""
    from ai.services.topic_service import TopicService

    service = TopicService()
    return service.extract_topics(documents)
