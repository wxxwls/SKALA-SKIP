"""External News API client."""
from typing import Any, Dict, List, Optional

import httpx

from app.core.logging import get_logger
from app.core.exceptions import ExternalServiceException

logger = get_logger(__name__)


class NewsApiClient:
    """HTTP client for external news API calls."""

    def __init__(self, base_url: str, api_key: Optional[str] = None) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
                headers=headers,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def fetch_news(
        self,
        query: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Fetch news articles from external API."""
        try:
            client = await self._get_client()
            params = {
                "q": query,
                "limit": limit,
            }
            if from_date:
                params["from"] = from_date
            if to_date:
                params["to"] = to_date

            response = await client.get("/news", params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("articles", [])
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from News API: {e}")
            raise ExternalServiceException(
                message="News API request failed",
                details={"status_code": e.response.status_code},
            )
        except Exception as e:
            logger.error(f"Failed to fetch news: {e}")
            raise ExternalServiceException(
                message="Failed to connect to News API",
                details={"error": str(e)},
            )
