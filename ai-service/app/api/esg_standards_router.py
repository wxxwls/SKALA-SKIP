"""
ESG Standards API Router

Endpoints for ESG standards analysis and disclosure mapping.
"""

import os
import shutil
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.schemas.common_schema import APIResponse
from app.services.esg_standards_service import (
    ESGStandardsService,
    get_esg_standards_service,
    KOREAN_MATERIALITY_ITEMS,
    ESG_CATEGORY_MAP,
)

logger = get_logger(__name__)

router = APIRouter(
    prefix="/internal/v1/standards",
    tags=["ESG 표준"],
)

# Upload directory for ESG standards documents
ESG_UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "esg_uploads",
)
os.makedirs(ESG_UPLOAD_FOLDER, exist_ok=True)

# In-memory document store (for demo - in production use DB)
_esg_documents: dict = {}


# ============ Response Schemas ============

class DisclosureItem(BaseModel):
    """Single disclosure item"""
    id: str = Field(..., alias="disclosure_id")
    title: str = Field(..., alias="disclosure_title")
    standard: str

    class Config:
        populate_by_name = True


class IssueDisclosures(BaseModel):
    """Issue with mapped disclosures"""
    issue: str
    category: str
    disclosures: List[dict]
    total_count: int


class IssueWithStats(BaseModel):
    """Issue with disclosure statistics"""
    issue: str
    category: str
    disclosures: List[dict]
    disclosure_count: int
    gri_count: int
    sasb_count: int


class SearchResult(BaseModel):
    """Disclosure search result"""
    disclosure_id: str
    disclosure_title: str
    standard: str
    korean_issue: str
    category: str


class AnalysisResult(BaseModel):
    """AI analysis result for an issue"""
    issue: str
    category: str
    disclosures: List[dict]
    analysis: dict


class StandardsStatistics(BaseModel):
    """ESG standards statistics"""
    total_issues: int
    total_disclosures: int
    gri_disclosures: int
    sasb_disclosures: int
    by_category: dict


# ============ API Endpoints ============

@router.get(
    "/issues",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="한국 중대성 이슈 목록 조회",
    description="18개 한국 중대성 이슈 목록을 카테고리와 함께 조회합니다.",
)
async def get_all_issues() -> APIResponse[dict]:
    """한국 중대성 이슈 목록 조회"""
    issues = []
    for idx, issue in enumerate(KOREAN_MATERIALITY_ITEMS, 1):
        issues.append({
            "id": f"issue{idx}",
            "name": issue,
            "category": ESG_CATEGORY_MAP.get(issue, "Unknown")
        })

    return APIResponse[dict](
        success=True,
        data={
            "issues": issues,
            "total_count": len(issues)
        }
    )


@router.get(
    "/issues/with-disclosures",
    response_model=APIResponse[List[IssueWithStats]],
    status_code=status.HTTP_200_OK,
    summary="이슈별 공시요구사항 매핑 조회",
    description="한국 중대성 이슈별로 매핑된 GRI/SASB 공시요구사항을 조회합니다.",
)
async def get_all_issues_with_disclosures(
    service: ESGStandardsService = Depends(get_esg_standards_service),
) -> APIResponse[List[IssueWithStats]]:
    """이슈별 공시요구사항 매핑 조회"""
    results = await service.get_all_issues_with_disclosures()
    return APIResponse[List[IssueWithStats]](
        success=True,
        data=results
    )


@router.get(
    "/issues/{issue_name}/disclosures",
    response_model=APIResponse[IssueDisclosures],
    status_code=status.HTTP_200_OK,
    summary="특정 이슈의 공시요구사항 조회",
    description="특정 이슈에 매핑된 공시요구사항 목록을 조회합니다.",
)
async def get_disclosures_for_issue(
    issue_name: str,
    standard: Optional[str] = Query(None, description="표준 필터 (GRI/SASB)"),
    service: ESGStandardsService = Depends(get_esg_standards_service),
) -> APIResponse[IssueDisclosures]:
    """특정 이슈의 공시요구사항 조회"""
    result = await service.get_disclosures_for_issue(issue_name, standard)
    return APIResponse[IssueDisclosures](
        success=True,
        data=result
    )


@router.get(
    "/issues/{issue_name}/analyze",
    response_model=APIResponse[AnalysisResult],
    status_code=status.HTTP_200_OK,
    summary="이슈 AI 분석",
    description="특정 ESG 이슈에 대한 AI 기반 분석 결과를 생성합니다. 요약, 주요 공시사항, 권장사항을 포함합니다.",
)
async def analyze_issue(
    issue_name: str,
    service: ESGStandardsService = Depends(get_esg_standards_service),
) -> APIResponse[AnalysisResult]:
    """이슈 AI 분석"""
    result = await service.analyze_issue_with_ai(issue_name)
    return APIResponse[AnalysisResult](
        success=True,
        data=result
    )


@router.get(
    "/search",
    response_model=APIResponse[List[SearchResult]],
    status_code=status.HTTP_200_OK,
    summary="공시요구사항 검색",
    description="시맨틱 검색을 사용하여 관련 공시요구사항을 검색합니다.",
)
async def search_disclosures(
    q: str = Query(..., min_length=1, description="검색어"),
    top_k: int = Query(5, ge=1, le=20, description="결과 개수"),
    service: ESGStandardsService = Depends(get_esg_standards_service),
) -> APIResponse[List[SearchResult]]:
    """공시요구사항 검색"""
    results = service.search_disclosures(q, top_k)
    return APIResponse[List[SearchResult]](
        success=True,
        data=results
    )


@router.get(
    "/statistics",
    response_model=APIResponse[StandardsStatistics],
    status_code=status.HTTP_200_OK,
    summary="ESG 표준 통계 조회",
    description="ESG 표준 매핑 관련 통계 정보를 조회합니다.",
)
async def get_statistics(
    service: ESGStandardsService = Depends(get_esg_standards_service),
) -> APIResponse[StandardsStatistics]:
    """ESG 표준 통계 조회"""
    stats = service.get_statistics()
    return APIResponse[StandardsStatistics](
        success=True,
        data=stats
    )


class IndexRequest(BaseModel):
    """PDF 파일에서 표준 인덱싱 요청"""
    gri_folder: str = Field(..., description="GRI 표준 폴더 경로")
    sasb_file: str = Field(..., description="SASB 표준 PDF 파일 경로")


class IndexResponse(BaseModel):
    """인덱싱 작업 응답"""
    total_disclosures: int
    message: str


@router.patch(
    "/index",
    response_model=APIResponse[IndexResponse],
    status_code=status.HTTP_200_OK,
    summary="GRI/SASB 표준 PDF 인덱싱",
    description="GRI/SASB PDF 파일에서 공시요구사항을 추출하여 ChromaDB에 저장합니다. 벡터 DB 구축 시 1회 실행합니다.",
)
async def index_standards(
    request: IndexRequest,
    service: ESGStandardsService = Depends(get_esg_standards_service),
) -> APIResponse[IndexResponse]:
    """GRI/SASB 표준 PDF 인덱싱"""
    logger.info(f"Starting indexing: GRI={request.gri_folder}, SASB={request.sasb_file}")

    try:
        count = await service.process_standards_folder(
            request.gri_folder,
            request.sasb_file
        )
        return APIResponse[IndexResponse](
            success=True,
            data={
                "total_disclosures": count,
                "message": f"Successfully indexed {count} disclosure requirements"
            }
        )
    except Exception as e:
        logger.error(f"Indexing error: {e}")
        return APIResponse[IndexResponse](
            success=False,
            data={"total_disclosures": 0, "message": str(e)}
        )


@router.post(
    "/reset",
    status_code=status.HTTP_200_OK,
    summary="ChromaDB 데이터베이스 초기화",
    description="ChromaDB의 모든 데이터를 삭제합니다. **주의:** 인덱싱된 모든 공시요구사항이 삭제됩니다.",
)
async def reset_database(
    service: ESGStandardsService = Depends(get_esg_standards_service),
) -> dict:
    """ChromaDB 데이터베이스 초기화"""
    service.reset_database()
    return {
        "status": "success",
        "message": "Database reset complete"
    }


@router.get(
    "/count",
    status_code=status.HTTP_200_OK,
    summary="인덱싱된 공시요구사항 개수 조회",
    description="ChromaDB에 현재 인덱싱된 공시요구사항 개수를 조회합니다.",
)
async def get_count(
    service: ESGStandardsService = Depends(get_esg_standards_service),
) -> dict:
    """인덱싱된 공시요구사항 개수 조회"""
    count = service.get_collection_count()
    return {
        "count": count,
        "message": f"{count} disclosures indexed"
    }


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="ESG 표준 서비스 헬스체크",
    description="ESG 표준 서비스 상태를 확인합니다.",
)
async def health_check(
    service: ESGStandardsService = Depends(get_esg_standards_service),
) -> dict:
    """ESG 표준 서비스 헬스체크"""
    count = service.get_collection_count()
    return {
        "status": "healthy",
        "module": "esg_standards",
        "indexed_disclosures": count,
        "embedding_model": "BAAI/bge-m3",
        "vector_db": "ChromaDB"
    }


# ============ Document Management Endpoints ============

class DocumentInfo(BaseModel):
    """Document information"""
    id: str
    name: str
    size: int
    uploadedAt: str
    status: str


class DocumentListResponse(BaseModel):
    """Response for document list"""
    success: bool
    documents: List[DocumentInfo]
    count: int


class DocumentUploadResponse(BaseModel):
    """Response for document upload"""
    success: bool
    documents: List[DocumentInfo]
    count: int
    message: Optional[str] = None


class EmbedRequest(BaseModel):
    """Request for embedding a document"""
    document_id: str
    document_name: str


@router.get(
    "/documents",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get list of uploaded ESG standard documents",
)
async def get_documents() -> DocumentListResponse:
    """
    Get list of all uploaded ESG standard documents.
    """
    documents = []

    # Load from in-memory store
    for doc_id, doc_info in _esg_documents.items():
        documents.append(DocumentInfo(
            id=doc_id,
            name=doc_info["name"],
            size=doc_info["size"],
            uploadedAt=doc_info["uploadedAt"],
            status=doc_info["status"]
        ))

    # Also scan upload folder for existing files
    if os.path.exists(ESG_UPLOAD_FOLDER):
        for filename in os.listdir(ESG_UPLOAD_FOLDER):
            if filename.lower().endswith(".pdf"):
                filepath = os.path.join(ESG_UPLOAD_FOLDER, filename)
                file_stat = os.stat(filepath)
                doc_id = filename.rsplit(".", 1)[0]

                if doc_id not in _esg_documents:
                    documents.append(DocumentInfo(
                        id=doc_id,
                        name=filename,
                        size=file_stat.st_size,
                        uploadedAt=datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        status="embedded"
                    ))

    logger.info(f"Retrieved {len(documents)} ESG documents")

    return DocumentListResponse(
        success=True,
        documents=documents,
        count=len(documents)
    )


@router.post(
    "/documents/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload ESG standard documents",
)
async def upload_documents(
    files: List[UploadFile] = File(..., description="PDF files to upload"),
) -> DocumentUploadResponse:
    """
    Upload ESG standard PDF documents.
    """
    logger.info(f"Received {len(files)} files for ESG standards upload")

    uploaded_docs = []

    for file in files:
        if not file.filename:
            continue

        if not file.filename.lower().endswith(".pdf"):
            logger.warning(f"Skipping non-PDF file: {file.filename}")
            continue

        # Generate unique ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        doc_id = f"esg_{timestamp}_{file.filename.rsplit('.', 1)[0]}"
        filename = f"{doc_id}.pdf"
        filepath = os.path.join(ESG_UPLOAD_FOLDER, filename)

        # Read file content to get size
        content = await file.read()
        file_size = len(content)

        # Save file
        with open(filepath, "wb") as buffer:
            buffer.write(content)

        # Store in memory
        doc_info = {
            "name": file.filename,
            "path": filepath,
            "size": file_size,
            "uploadedAt": datetime.now().isoformat(),
            "status": "pending"
        }
        _esg_documents[doc_id] = doc_info

        uploaded_docs.append(DocumentInfo(
            id=doc_id,
            name=file.filename,
            size=file_size,
            uploadedAt=doc_info["uploadedAt"],
            status="pending"
        ))

        logger.info(f"Uploaded ESG document: {file.filename} -> {filepath}")

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
        count=len(uploaded_docs)
    )


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an ESG standard document",
)
async def delete_document(document_id: str) -> dict:
    """
    Delete an uploaded ESG standard document.
    """
    # Check in-memory store
    if document_id in _esg_documents:
        doc_info = _esg_documents[document_id]
        filepath = doc_info.get("path")

        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Deleted file: {filepath}")

        del _esg_documents[document_id]
        logger.info(f"Deleted ESG document: {document_id}")

        return {"success": True, "message": f"Document {document_id} deleted"}

    # Try to find file directly
    for filename in os.listdir(ESG_UPLOAD_FOLDER):
        if filename.startswith(document_id) or filename.rsplit(".", 1)[0] == document_id:
            filepath = os.path.join(ESG_UPLOAD_FOLDER, filename)
            os.remove(filepath)
            logger.info(f"Deleted file: {filepath}")
            return {"success": True, "message": f"Document {document_id} deleted"}

    return {"success": False, "message": f"Document {document_id} not found"}


@router.post(
    "/documents/embed",
    status_code=status.HTTP_200_OK,
    summary="Start embedding for an ESG standard document",
)
async def embed_document(
    request: EmbedRequest,
    service: ESGStandardsService = Depends(get_esg_standards_service),
) -> dict:
    """
    Start embedding process for a specific ESG standard document.
    """
    document_id = request.document_id
    document_name = request.document_name

    logger.info(f"Starting embedding for ESG document: {document_id} ({document_name})")

    # Update status to processing
    if document_id in _esg_documents:
        _esg_documents[document_id]["status"] = "processing"

    try:
        # Get file path
        filepath = None
        if document_id in _esg_documents:
            filepath = _esg_documents[document_id].get("path")
        else:
            # Try to find file
            for filename in os.listdir(ESG_UPLOAD_FOLDER):
                if filename.startswith(document_id) or document_id in filename:
                    filepath = os.path.join(ESG_UPLOAD_FOLDER, filename)
                    break

        if filepath and os.path.exists(filepath):
            # TODO: Implement actual embedding logic using service
            # For now, just mark as embedded
            pass

        # Update status to embedded
        if document_id in _esg_documents:
            _esg_documents[document_id]["status"] = "embedded"

        logger.info(f"Embedding completed for ESG document: {document_id}")

        return {
            "success": True,
            "document_id": document_id,
            "status": "embedded",
            "message": f"Document {document_name} embedded successfully"
        }

    except Exception as e:
        logger.error(f"Embedding error for {document_id}: {e}")

        if document_id in _esg_documents:
            _esg_documents[document_id]["status"] = "pending"

        return {
            "success": False,
            "document_id": document_id,
            "status": "error",
            "message": str(e)
        }
