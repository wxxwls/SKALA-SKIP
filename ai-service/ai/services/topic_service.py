"""Topic modeling service."""
from typing import List, Dict

from ai.models.topic_model import TopicModel
from app.core.logging import get_logger

logger = get_logger(__name__)


class TopicService:
    """Service for topic modeling operations."""

    def __init__(self, n_topics: int = 10) -> None:
        self._model = TopicModel(n_topics)

    def extract_topics(self, documents: List[str]) -> List[Dict]:
        """Extract topics from documents."""
        logger.info(f"Extracting topics from {len(documents)} documents")
        return self._model.get_topics(documents)

    def get_document_topics(
        self, document: str, top_k: int = 3
    ) -> List[Dict]:
        """Get topics for a single document."""
        return self._model.get_document_topics(document, top_k)

    def train(self, documents: List[str]) -> None:
        """Train topic model on documents."""
        logger.info(f"Training topic model on {len(documents)} documents")
        self._model.fit(documents)
