"""VectorDB repository for vector storage operations."""
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import VectorDBException

logger = get_logger(__name__)


class VectorDBRepository:
    """Repository for VectorDB (ChromaDB) operations."""

    def __init__(self) -> None:
        self._client: Optional[chromadb.Client] = None
        self._collection = None

    def _get_client(self) -> chromadb.Client:
        """Get or create ChromaDB client."""
        if self._client is None:
            try:
                self._client = chromadb.HttpClient(
                    host=settings.CHROMA_HOST,
                    port=settings.CHROMA_PORT,
                )
            except Exception as e:
                logger.error(f"Failed to connect to ChromaDB: {e}")
                raise VectorDBException(
                    message="Failed to connect to VectorDB",
                    details={"error": str(e)},
                )
        return self._client

    def _get_collection(self, collection_name: Optional[str] = None):
        """Get or create collection."""
        client = self._get_client()
        name = collection_name or settings.CHROMA_COLLECTION_NAME
        return client.get_or_create_collection(name=name)

    async def add_documents(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        collection_name: Optional[str] = None,
    ) -> None:
        """Add documents with embeddings to the vector store."""
        try:
            collection = self._get_collection(collection_name)
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas or [{}] * len(ids),
            )
            logger.info(f"Added {len(ids)} documents to collection")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise VectorDBException(
                message="Failed to add documents to VectorDB",
                details={"error": str(e)},
            )

    async def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Query similar documents from vector store."""
        try:
            collection = self._get_collection(collection_name)
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
            )
            return results
        except Exception as e:
            logger.error(f"Failed to query documents: {e}")
            raise VectorDBException(
                message="Failed to query VectorDB",
                details={"error": str(e)},
            )

    async def delete_documents(
        self,
        ids: List[str],
        collection_name: Optional[str] = None,
    ) -> None:
        """Delete documents from vector store."""
        try:
            collection = self._get_collection(collection_name)
            collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from collection")
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            raise VectorDBException(
                message="Failed to delete documents from VectorDB",
                details={"error": str(e)},
            )
