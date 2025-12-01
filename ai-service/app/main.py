"""
FastAPI application factory and entry point.

This is the main entry point for the ESG AI Service.
Run with: uvicorn app.main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import (
    benchmark_router,
    issue_pool_router,
    report_router,
    media_router,
    esg_standards_router,
    carbon_router,
    chatbot_router,
    materiality_router,
)
from app.config.config import settings
from app.core.logging import get_logger, setup_logging
from app.core.middleware import (
    ErrorHandlingMiddleware,
    LoggingMiddleware,
    RequestIDMiddleware,
)

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting ESG AI Service...")
    yield
    logger.info("Shutting down ESG AI Service...")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI app instance
    """
    app = FastAPI(
        title="ESG 이중중대성 AI 서비스",
        version=settings.APP_VERSION,
        description="""
## ESG 이중중대성 평가 AI 서비스

Spring Boot 백엔드에서 호출하는 내부 AI 마이크로서비스입니다.

### 주요 기능
- **이슈풀 생성**: ESG 이슈 후보군 자동 생성 및 중대성 점수 산출
- **중대성 평가**: 이해관계자 설문 기반 이중중대성 매트릭스 생성
- **보고서 작성**: AI 기반 지속가능경영보고서 초안 작성
- **ESG 챗봇**: RAG 기반 ESG Q&A 챗봇
- **미디어 분석**: 뉴스 수집 및 ESG 이슈 분류, 감성 분석
- **탄소 시그널**: 탄소 가격 예측 및 거래 시그널 제공
- **벤치마킹**: 경쟁사 지속가능경영보고서 분석

### 참고사항
- 이 서비스는 내부 전용입니다
- 모든 요청은 Spring Boot 백엔드(8080)를 통해 전달됩니다
- 프론트엔드에서 직접 호출하지 않습니다
""",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # CORS middleware (for Spring Boot only)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middlewares (order matters!)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # Register routers
    app.include_router(issue_pool_router.router)
    app.include_router(report_router.router)
    app.include_router(benchmark_router.router)
    app.include_router(media_router.router)
    app.include_router(esg_standards_router.router)
    app.include_router(carbon_router.router)
    app.include_router(chatbot_router.router)
    app.include_router(materiality_router.router)

    # Static files for frontend
    static_dir = Path(__file__).parent.parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Frontend pages
    @app.get("/benchmark")
    async def benchmark_page():
        """Benchmark frontend page"""
        html_path = static_dir / "benchmark.html"
        if html_path.exists():
            return FileResponse(html_path)
        return {"error": "Frontend not found"}

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "status": "running",
            "pages": {
                "benchmark": "/benchmark",
                "docs": "/internal/docs",
            },
        }

    # Health check endpoint
    @app.get("/internal/health")
    async def health_check():
        """
        Health check endpoint for monitoring.

        Returns:
            Service health status
        """
        return {
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }

    logger.info(f"FastAPI app created: {settings.APP_NAME}")

    return app


# Create app instance
app = create_app()


# Entry point for uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

# uvicorn app.main:app --reload --port 8000