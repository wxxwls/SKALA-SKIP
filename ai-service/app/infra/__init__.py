"""
Infrastructure adapters package.

Contains:
- File storage adapters
- VectorDB clients
- External API clients
"""

from app.infra.file_storage import FileStorageService, get_file_storage_service

__all__ = [
    "FileStorageService",
    "get_file_storage_service",
]
