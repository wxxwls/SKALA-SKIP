"""Embedding service for text vectorization."""
from typing import List, Optional

from ai.models.embedding import EmbeddingModel
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service for embedding operations."""

    def __init__(self, model_name: Optional[str] = None) -> None:
        self._model = EmbeddingModel(model_name)

    def encode_texts(
        self,
        texts: List[str],
        batch_size: int = 32,
    ) -> List[List[float]]:
        """Encode multiple texts to embeddings."""
        logger.info(f"Encoding {len(texts)} texts")
        return self._model.encode(texts, batch_size=batch_size)

    def encode_text(self, text: str) -> List[float]:
        """Encode single text to embedding."""
        return self._model.encode_single(text)

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self._model.embedding_dimension
