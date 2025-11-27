"""
Issue Pool API Router

Endpoints for ESG issue pool generation and topic scoring.

IMPORTANT: These are internal APIs called only by Spring Boot, not by the frontend.
"""

import os
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, UploadFile, status
from pydantic import BaseModel

from app.core.logging import get_logger
from app.schemas.common_schema import APIResponse
from app.schemas.issue_pool_schema import (
    GenerateIssuePoolRequest,
    IssuePoolResponse,
    ScoreTopicRequest,
    ScoreTopicResponse,
)
from app.services.issue_pool_service import IssuePoolService

logger = get_logger(__name__)

# Create router with prefix
router = APIRouter(
    prefix="/internal/v1/issue-pools",
    tags=["이슈풀 생성"],
)

# Upload directories
STANDARDS_UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "esg_uploads",
)
BENCHMARK_UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "benchmark_uploads",
)
os.makedirs(STANDARDS_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BENCHMARK_UPLOAD_FOLDER, exist_ok=True)


# ============ Document Upload Schemas ============

class UploadedDocumentInfo(BaseModel):
    """Uploaded document information"""
    id: str
    name: str
    size: int
    uploadedAt: str
    status: str


class DocumentUploadResponse(BaseModel):
    """Response for document upload"""
    success: bool
    documents: List[UploadedDocumentInfo]
    count: int
    message: Optional[str] = None


def get_issue_pool_service() -> IssuePoolService:
    """
    Dependency injection for IssuePoolService.

    Returns:
        IssuePoolService instance
    """
    return IssuePoolService()


@router.post(
    "/generate",
    response_model=APIResponse[IssuePoolResponse],
    status_code=status.HTTP_200_OK,
    summary="ESG 이슈풀 생성",
    description="""
다양한 소스를 기반으로 회사의 ESG 이슈풀을 생성합니다.

**소스:**
- ESG 표준 (GRI, SASB, ISSB, KCGS 등)
- 내부 문서 (정책, KPI, 전략)
- 벤치마킹 보고서 (경쟁사 지속가능경영보고서)
- 뉴스 및 미디어 분석

**참고:** 결과는 최대 20개 토픽으로 제한됩니다.
""",
)
async def generate_issue_pool(
    request: GenerateIssuePoolRequest,
    service: IssuePoolService = Depends(get_issue_pool_service),
) -> APIResponse[IssuePoolResponse]:
    """
    Generate ESG issue pool for a company.

    This endpoint:
    1. Retrieves context from multiple sources using RAG
    2. Generates candidate topics using LLM
    3. Scores topics for double materiality
    4. Selects top 20 topics
    5. Returns structured issue pool

    Args:
        request: Issue pool generation request
        service: Issue pool service (injected)

    Returns:
        APIResponse with issue pool data
    """
    logger.info(
        f"POST /internal/api/v1/issue-pool/generate - "
        f"company_id={request.company_context.company_id}, "
        f"year={request.company_context.year}"
    )

    # Call service layer
    result = await service.generate_issue_pool(request)

    # Return standard response envelope
    return APIResponse[IssuePoolResponse](
        success=True,
        data=result,
    )


@router.post(
    "/score-topic",
    response_model=APIResponse[ScoreTopicResponse],
    status_code=status.HTTP_200_OK,
    summary="토픽 이중중대성 점수 산출",
    description="""
단일 ESG 토픽에 대한 재무적 중대성과 영향 중대성 점수를 산출합니다.

**결과:**
- 점수 범위: 0.0 ~ 10.0
- 점수 산출 근거 포함
- 출처 정보 포함
""",
)
async def score_topic(
    request: ScoreTopicRequest,
    service: IssuePoolService = Depends(get_issue_pool_service),
) -> APIResponse[ScoreTopicResponse]:
    """
    Score a single topic for double materiality.

    This endpoint:
    1. Retrieves relevant context from vector DB
    2. Uses LLM to score the topic
    3. Returns financial_score and impact_score (0.0-10.0)
    4. Includes source attribution

    Args:
        request: Topic scoring request
        service: Issue pool service (injected)

    Returns:
        APIResponse with materiality scores
    """
    logger.info(
        f"POST /internal/api/v1/issue-pool/score-topic - "
        f"topic={request.topic_title}, "
        f"company_id={request.company_context.company_id}"
    )

    # Call service layer
    result = await service.score_topic(request)

    # Return standard response envelope
    return APIResponse[ScoreTopicResponse](
        success=True,
        data=result,
    )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="이슈풀 서비스 헬스체크",
    description="이슈풀 서비스 상태를 확인합니다.",
)
async def health_check() -> dict:
    """이슈풀 서비스 헬스체크"""
    return {
        "status": "healthy",
        "module": "issue_pool",
    }


# ============ Document Upload Endpoints (ISS-001, ISS-002) ============

@router.patch(
    "/s_upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="표준 문서 업로드 (ISS-001)",
    description="""
    ESG 표준 문서(GRI, SASB 등)를 업로드합니다.

    **지원 형식:** PDF
    **용도:** 이슈풀 생성 시 표준 기반 이슈 도출에 사용
    """,
)
async def upload_standards_documents(
    files: List[UploadFile] = File(..., description="PDF 파일들"),
) -> DocumentUploadResponse:
    """
    표준 문서 업로드 API (ISS-001)

    ESG 표준 문서를 업로드하여 이슈풀 생성에 활용합니다.
    """
    logger.info(f"PATCH /internal/v1/issue-pools/s_upload - {len(files)} files")

    uploaded_docs = []

    for file in files:
        if not file.filename:
            continue

        if not file.filename.lower().endswith(".pdf"):
            logger.warning(f"Skipping non-PDF file: {file.filename}")
            continue

        # Generate unique ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        doc_id = f"std_{timestamp}_{file.filename.rsplit('.', 1)[0]}"
        filename = f"{doc_id}.pdf"
        filepath = os.path.join(STANDARDS_UPLOAD_FOLDER, filename)

        # Read and save file
        content = await file.read()
        file_size = len(content)

        with open(filepath, "wb") as buffer:
            buffer.write(content)

        uploaded_docs.append(UploadedDocumentInfo(
            id=doc_id,
            name=file.filename,
            size=file_size,
            uploadedAt=datetime.now().isoformat(),
            status="pending"
        ))

        logger.info(f"Uploaded standards document: {file.filename} -> {filepath}")

    if not uploaded_docs:
        return DocumentUploadResponse(
            success=False,
            documents=[],
            count=0,
            message="No valid PDF files uploaded"
        )

    return DocumentUploadResponse(
        success=True,
        documents=uploaded_docs,
        count=len(uploaded_docs),
        message=f"{len(uploaded_docs)}개 표준 문서 업로드 완료"
    )


@router.patch(
    "/b_upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="벤치마킹 문서 업로드 (ISS-002)",
    description="""
    경쟁사 지속가능경영 보고서를 업로드합니다.

    **지원 형식:** PDF
    **파일명 규칙:** 파일명에서 회사명을 추출합니다 (예: 삼성전자_2023.pdf → 삼성전자)
    **용도:** 이슈풀 생성 시 벤치마킹 기반 이슈 도출에 사용
    """,
)
async def upload_benchmark_documents(
    files: List[UploadFile] = File(..., description="PDF 파일들"),
) -> DocumentUploadResponse:
    """
    벤치마킹 문서 업로드 API (ISS-002)

    경쟁사 보고서를 업로드하여 이슈풀 생성에 활용합니다.
    """
    logger.info(f"PATCH /internal/v1/issue-pools/b_upload - {len(files)} files")

    uploaded_docs = []

    for file in files:
        if not file.filename:
            continue

        if not file.filename.lower().endswith(".pdf"):
            logger.warning(f"Skipping non-PDF file: {file.filename}")
            continue

        # Generate unique ID (extract company name from filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        company_name = file.filename.rsplit(".", 1)[0]
        doc_id = f"bench_{timestamp}_{company_name}"
        filename = f"{doc_id}.pdf"
        filepath = os.path.join(BENCHMARK_UPLOAD_FOLDER, filename)

        # Read and save file
        content = await file.read()
        file_size = len(content)

        with open(filepath, "wb") as buffer:
            buffer.write(content)

        uploaded_docs.append(UploadedDocumentInfo(
            id=doc_id,
            name=file.filename,
            size=file_size,
            uploadedAt=datetime.now().isoformat(),
            status="pending"
        ))

        logger.info(f"Uploaded benchmark document: {file.filename} -> {filepath}")

    if not uploaded_docs:
        return DocumentUploadResponse(
            success=False,
            documents=[],
            count=0,
            message="No valid PDF files uploaded"
        )

    return DocumentUploadResponse(
        success=True,
        documents=uploaded_docs,
        count=len(uploaded_docs),
        message=f"{len(uploaded_docs)}개 벤치마킹 문서 업로드 완료"
    )
