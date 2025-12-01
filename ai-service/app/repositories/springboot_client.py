"""Spring Boot backend API client."""
from typing import Any, Dict, Optional

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import ExternalServiceException

logger = get_logger(__name__)


class SpringBootClient:
    """HTTP client for Spring Boot backend communication."""

    def __init__(self) -> None:
        self.base_url = settings.SPRING_BOOT_URL
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make GET request to Spring Boot backend."""
        try:
            client = await self._get_client()
            response = await client.get(path, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Spring Boot: {e}")
            raise ExternalServiceException(
                message="Spring Boot request failed",
                details={"status_code": e.response.status_code, "path": path},
            )
        except Exception as e:
            logger.error(f"Failed to call Spring Boot: {e}")
            raise ExternalServiceException(
                message="Failed to connect to Spring Boot",
                details={"error": str(e)},
            )

    async def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make POST request to Spring Boot backend."""
        try:
            client = await self._get_client()
            response = await client.post(path, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Spring Boot: {e}")
            raise ExternalServiceException(
                message="Spring Boot request failed",
                details={"status_code": e.response.status_code, "path": path},
            )
        except Exception as e:
            logger.error(f"Failed to call Spring Boot: {e}")
            raise ExternalServiceException(
                message="Failed to connect to Spring Boot",
                details={"error": str(e)},
            )
