"""Report document storage repository."""
from typing import Any, Dict, List, Optional
from pathlib import Path
import json

from app.core.logging import get_logger
from app.core.exceptions import NotFoundException

logger = get_logger(__name__)


class ReportDocumentRepository:
    """Repository for report document storage operations."""

    def __init__(self, storage_path: str = "./storage/reports") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def save_report(
        self,
        report_id: str,
        content: Dict[str, Any],
    ) -> str:
        """Save report document to storage."""
        try:
            file_path = self.storage_path / f"{report_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved report: {report_id}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            raise

    async def get_report(self, report_id: str) -> Dict[str, Any]:
        """Retrieve report document from storage."""
        file_path = self.storage_path / f"{report_id}.json"
        if not file_path.exists():
            raise NotFoundException(
                message=f"Report not found: {report_id}",
                details={"report_id": report_id},
            )
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read report: {e}")
            raise

    async def list_reports(
        self,
        company_id: Optional[str] = None,
    ) -> List[str]:
        """List available reports."""
        reports = []
        for file_path in self.storage_path.glob("*.json"):
            report_id = file_path.stem
            if company_id is None or report_id.startswith(company_id):
                reports.append(report_id)
        return reports

    async def delete_report(self, report_id: str) -> None:
        """Delete report document from storage."""
        file_path = self.storage_path / f"{report_id}.json"
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted report: {report_id}")
