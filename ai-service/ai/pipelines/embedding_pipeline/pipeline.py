"""Embedding pipeline for document processing."""
from typing import List, Dict, Any

from ai.services.embedding_service import EmbeddingService
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingPipeline:
    """Pipeline for document embedding and indexing."""

    def __init__(self) -> None:
        self._embedding_service = EmbeddingService()

    def run(
        self,
        documents: List[Dict[str, Any]],
        batch_size: int = 32,
    ) -> List[Dict[str, Any]]:
        """Run embedding pipeline on documents.

        Args:
            documents: List of documents with 'id' and 'content' keys
            batch_size: Batch size for embedding

        Returns:
            Documents with added 'embedding' key
        """
        logger.info(f"Running embedding pipeline on {len(documents)} documents")

        texts = [doc["content"] for doc in documents]
        embeddings = self._embedding_service.encode_texts(texts, batch_size)

        results = []
        for doc, embedding in zip(documents, embeddings):
            results.append({
                **doc,
                "embedding": embedding,
            })

        logger.info(f"Embedded {len(results)} documents")
        return results
