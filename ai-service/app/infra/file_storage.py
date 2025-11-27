"""
File Storage Infrastructure Adapter

Handles file upload, storage, and retrieval operations.
This keeps file I/O logic out of API routers (RULE F-LAYER-001).
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from app.config.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Base directory for all uploads
_BASE_DIR = Path(__file__).parent.parent.parent


class FileStorageService:
    """
    File storage service for handling document uploads.

    Centralizes file I/O operations to maintain clean separation of concerns.
    """

    def __init__(self):
        """Initialize storage directories."""
        self.benchmark_dir = _BASE_DIR / settings.BENCHMARK_UPLOADS_DIR
        self.esg_dir = _BASE_DIR / settings.ESG_UPLOADS_DIR

        # Ensure directories exist
        self.benchmark_dir.mkdir(parents=True, exist_ok=True)
        self.esg_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"FileStorageService initialized: benchmark={self.benchmark_dir}, esg={self.esg_dir}")

    async def save_benchmark_file(
        self,
        file: UploadFile,
        company_name: Optional[str] = None,
    ) -> dict:
        """
        Save a benchmark PDF file.

        Args:
            file: Uploaded file
            company_name: Optional company name (extracted from filename if not provided)

        Returns:
            Dict with file info: id, name, path, size, uploadedAt
        """
        return await self._save_file(file, self.benchmark_dir, "bench", company_name)

    async def save_esg_file(
        self,
        file: UploadFile,
    ) -> dict:
        """
        Save an ESG standards PDF file.

        Args:
            file: Uploaded file

        Returns:
            Dict with file info: id, name, path, size, uploadedAt
        """
        return await self._save_file(file, self.esg_dir, "esg")

    async def _save_file(
        self,
        file: UploadFile,
        target_dir: Path,
        prefix: str,
        company_name: Optional[str] = None,
    ) -> dict:
        """
        Internal method to save a file.

        Args:
            file: Uploaded file
            target_dir: Target directory path
            prefix: ID prefix (e.g., 'bench', 'esg')
            company_name: Optional company name

        Returns:
            Dict with file info
        """
        if not file.filename:
            raise ValueError("File has no filename")

        if not file.filename.lower().endswith(".pdf"):
            raise ValueError(f"Only PDF files are allowed: {file.filename}")

        # Generate unique ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = company_name or file.filename.rsplit(".", 1)[0]
        doc_id = f"{prefix}_{timestamp}_{base_name}"
        filename = f"{doc_id}.pdf"
        filepath = target_dir / filename

        # Read and save file
        content = await file.read()
        file_size = len(content)

        with open(filepath, "wb") as buffer:
            buffer.write(content)

        logger.info(f"Saved file: {file.filename} -> {filepath} ({file_size} bytes)")

        return {
            "id": doc_id,
            "name": file.filename,
            "path": str(filepath),
            "size": file_size,
            "uploadedAt": datetime.now().isoformat(),
            "status": "pending",
        }

    def delete_file(self, filepath: str) -> bool:
        """
        Delete a file by path.

        Args:
            filepath: Full path to the file

        Returns:
            True if deleted, False if not found
        """
        path = Path(filepath)
        if path.exists():
            path.unlink()
            logger.info(f"Deleted file: {filepath}")
            return True
        return False

    def delete_by_id(self, doc_id: str, target_dir: Optional[Path] = None) -> bool:
        """
        Delete a file by document ID.

        Args:
            doc_id: Document ID
            target_dir: Optional specific directory to search

        Returns:
            True if deleted, False if not found
        """
        search_dirs = [target_dir] if target_dir else [self.benchmark_dir, self.esg_dir]

        for directory in search_dirs:
            for filename in os.listdir(directory):
                if filename.startswith(doc_id) or doc_id in filename:
                    filepath = directory / filename
                    filepath.unlink()
                    logger.info(f"Deleted file by ID: {doc_id} -> {filepath}")
                    return True
        return False

    def list_files(self, target_dir: Path) -> list:
        """
        List all PDF files in a directory.

        Args:
            target_dir: Directory to list

        Returns:
            List of file info dicts
        """
        files = []
        if target_dir.exists():
            for filename in os.listdir(target_dir):
                if filename.lower().endswith(".pdf"):
                    filepath = target_dir / filename
                    file_stat = filepath.stat()
                    doc_id = filename.rsplit(".", 1)[0]

                    files.append({
                        "id": doc_id,
                        "name": filename,
                        "path": str(filepath),
                        "size": file_stat.st_size,
                        "uploadedAt": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        "status": "embedded",
                    })
        return files

    def list_benchmark_files(self) -> list:
        """List all benchmark PDF files."""
        return self.list_files(self.benchmark_dir)

    def list_esg_files(self) -> list:
        """List all ESG PDF files."""
        return self.list_files(self.esg_dir)

    def get_file_path(self, doc_id: str) -> Optional[str]:
        """
        Get file path by document ID.

        Args:
            doc_id: Document ID

        Returns:
            File path or None if not found
        """
        for directory in [self.benchmark_dir, self.esg_dir]:
            for filename in os.listdir(directory):
                if filename.startswith(doc_id) or doc_id in filename:
                    return str(directory / filename)
        return None


# Singleton instance
_file_storage_service: Optional[FileStorageService] = None


def get_file_storage_service() -> FileStorageService:
    """Get or create FileStorageService singleton."""
    global _file_storage_service
    if _file_storage_service is None:
        _file_storage_service = FileStorageService()
    return _file_storage_service
