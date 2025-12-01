"""FastAPI dependency injection utilities."""
from typing import AsyncGenerator

import httpx

from app.core.config import settings


async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide an async HTTP client for dependency injection."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


async def get_spring_boot_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide an HTTP client configured for Spring Boot backend."""
    async with httpx.AsyncClient(
        base_url=settings.SPRING_BOOT_URL,
        timeout=30.0,
    ) as client:
        yield client
