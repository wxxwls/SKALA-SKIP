"""
Benchmark Analysis Router - ESG 벤치마킹 분석 API

경쟁사 지속가능경영 보고서를 분석하여 벤치마킹 결과를 생성하는 API
내부 전용 API (Spring Boot → FastAPI)
"""

import os
import shutil
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.core.logging import get_logger
from app.infra.file_storage import FileStorageService, get_file_storage_service
from app.schemas.benchmark_schema import (
    BenchmarkAnalyzeRequest,
    BenchmarkAnalyzeResponse,
    BenchmarkPDFListResponse,
    BenchmarkUploadResponse,
    CompanyPDF,
    KeywordAnalysisResult,
)
from app.services.benchmark_service import get_benchmark_service, reload_benchmark_service

logger = get_logger(__name__)

router = APIRouter(
    prefix="/internal/v1/benchmarks",
    tags=["벤치마킹 분석"],
)


@router.post(
    "/upload",
    response_model=BenchmarkUploadResponse,
    summary="벤치마킹용 PDF 업로드",
    description="""
    경쟁사 지속가능경영 보고서 PDF 파일을 업로드합니다.

    **파일명 규칙:**
    - 파일명에서 회사명을 추출합니다 (예: 삼성전자_2023.pdf → 삼성전자)

    **제한사항:**
    - 최대 파일 크기: 200MB
    - 허용 형식: PDF만 가능
    """,
)
async def upload_pdfs(
    files: List[UploadFile] = File(..., description="PDF 파일들"),
    storage: FileStorageService = Depends(get_file_storage_service),
) -> BenchmarkUploadResponse:
    """
    PDF 파일 업로드

    Args:
        files: 업로드할 PDF 파일 목록
        storage: 파일 저장 서비스 (DI)

    Returns:
        업로드된 회사 정보
    """
    logger.info(f"Received {len(files)} files for upload")

    try:
        uploaded_companies = []

        for file in files:
            if not file.filename:
                continue

            if not file.filename.lower().endswith(".pdf"):
                logger.warning(f"Skipping non-PDF file: {file.filename}")
                continue

            # Delegate to infra layer
            doc_info = await storage.save_benchmark_file(file)

            uploaded_companies.append(
                CompanyPDF(
                    name=doc_info["name"].rsplit(".", 1)[0],
                    path=doc_info["path"],
                    filename=os.path.basename(doc_info["path"]),
                )
            )

        if not uploaded_companies:
            return BenchmarkUploadResponse(
                success=False,
                message="유효한 PDF 파일이 없습니다",
            )

        return BenchmarkUploadResponse(
            success=True,
            companies=uploaded_companies,
            count=len(uploaded_companies),
        )

    except Exception as e:
        logger.error(f"Error uploading files: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "ESG-AI-BENCH-001",
                "message": "파일 업로드 중 오류가 발생했습니다",
                "details": str(e),
            },
        )


@router.post(
    "/analyze",
    response_model=BenchmarkAnalyzeResponse,
    summary="ESG 키워드 벤치마킹 분석",
    description="""
    특정 ESG 키워드에 대해 경쟁사 보고서를 분석합니다.

    **분석 결과:**
    - coverage: Yes(충분히 다룸), Partially(부분적), No(미발견)
    - response: 해당 키워드 관련 내용 요약
    - source_pages: 관련 페이지 번호

    **예시 키워드:**
    - 탄소중립
    - RE100
    - 생물다양성
    - 공급망 실사
    - 이사회 독립성
    """,
)
async def analyze_keyword(
    request: BenchmarkAnalyzeRequest,
) -> BenchmarkAnalyzeResponse:
    """
    키워드 기반 벤치마킹 분석

    Args:
        request: 분석 요청 (키워드 + 회사 PDF 목록)

    Returns:
        회사별 분석 결과
    """
    logger.info(
        f"Analyzing keyword '{request.keyword}' for {len(request.companies)} companies",
        extra={
            "keyword": request.keyword,
            "company_count": len(request.companies),
        },
    )

    if not request.keyword.strip():
        return BenchmarkAnalyzeResponse(
            success=False,
            message="키워드를 입력해주세요",
        )

    if not request.companies:
        return BenchmarkAnalyzeResponse(
            success=False,
            message="분석할 회사가 없습니다",
        )

    try:
        service = get_benchmark_service()

        # Convert to list of dicts for service
        companies_data = [
            {"name": c.name, "path": c.path} for c in request.companies
        ]

        # Perform analysis
        raw_results = await service.analyze_keyword_for_companies(
            request.keyword, companies_data
        )

        # Convert to response model
        results = {
            company: KeywordAnalysisResult(
                coverage=data["coverage"],
                response=data["response"],
                source_pages=data["source_pages"],
            )
            for company, data in raw_results.items()
        }

        # Get summary
        summary = service.get_benchmark_summary(raw_results)

        logger.info(
            f"Analysis complete: {summary['full_coverage']} full, "
            f"{summary['partial_coverage']} partial, {summary['no_coverage']} none"
        )

        return BenchmarkAnalyzeResponse(
            success=True,
            keyword=request.keyword,
            results=results,
            summary=summary,
        )

    except Exception as e:
        logger.error(f"Error analyzing keyword: {e}", exc_info=True)
        return BenchmarkAnalyzeResponse(
            success=False,
            message=f"분석 중 오류가 발생했습니다: {str(e)}",
        )


@router.get(
    "/pdfs",
    response_model=BenchmarkPDFListResponse,
    summary="업로드된 PDF 목록 조회",
    description="벤치마킹을 위해 업로드된 PDF 파일 목록을 조회합니다.",
)
async def get_uploaded_pdfs(
    storage: FileStorageService = Depends(get_file_storage_service),
) -> BenchmarkPDFListResponse:
    """
    업로드된 PDF 목록 조회

    Returns:
        PDF 파일 목록
    """
    try:
        files = storage.list_benchmark_files()
        pdfs = [
            CompanyPDF(
                name=f["name"].rsplit(".", 1)[0],
                path=f["path"],
                filename=os.path.basename(f["path"]),
            )
            for f in files
        ]

        logger.info(f"Found {len(pdfs)} uploaded PDFs")

        return BenchmarkPDFListResponse(
            success=True,
            pdfs=pdfs,
            count=len(pdfs),
        )

    except Exception as e:
        logger.error(f"Error listing PDFs: {e}", exc_info=True)
        return BenchmarkPDFListResponse(
            success=False,
            message=f"목록 조회 중 오류가 발생했습니다: {str(e)}",
        )


@router.delete(
    "/pdfs/{filename}",
    summary="업로드된 PDF 삭제",
    description="특정 PDF 파일을 삭제합니다.",
)
async def delete_pdf(
    filename: str,
    storage: FileStorageService = Depends(get_file_storage_service),
):
    """
    PDF 파일 삭제

    Args:
        filename: 삭제할 파일명

    Returns:
        삭제 결과
    """
    try:
        deleted = storage.delete_by_id(filename, storage.benchmark_dir)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "ESG-AI-BENCH-002", "message": "파일을 찾을 수 없습니다"},
            )

        return {"success": True, "message": f"{filename} 삭제 완료"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting PDF: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "ESG-AI-BENCH-003",
                "message": "파일 삭제 중 오류가 발생했습니다",
                "details": str(e),
            },
        )


@router.post(
    "/cache/clear",
    summary="분석 캐시 초기화",
    description="벤치마킹 분석 결과 캐시를 초기화합니다.",
)
async def clear_cache():
    """
    캐시 초기화

    Returns:
        초기화 결과
    """
    try:
        service = get_benchmark_service()
        service.clear_cache()

        logger.info("Benchmark cache cleared")

        return {"success": True, "message": "캐시가 초기화되었습니다"}

    except Exception as e:
        logger.error(f"Error clearing cache: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "ESG-AI-BENCH-004",
                "message": "캐시 초기화 중 오류가 발생했습니다",
                "details": str(e),
            },
        )


# =============================================================================
# SK 17개 이슈 기반 분석 API (이중중대성 평가)
# =============================================================================


@router.get(
    "/issues",
    summary="SK 17개 이슈 목록 조회",
    description="벤치마킹 기준인 SK Inc. 17개 ESG 이슈 목록을 반환합니다.",
)
async def get_sk_issues():
    """SK 17개 이슈 목록 반환"""
    service = get_benchmark_service()
    return {
        "success": True,
        "issues": service.get_sk_17_issues(),
        "count": 17,
    }


@router.get(
    "/data",
    summary="캐시된 분석 데이터 조회",
    description="이미 분석된 모든 회사의 벤치마킹 결과를 반환합니다.",
)
async def get_cached_data():
    """캐시된 전체 데이터 반환"""
    service = get_benchmark_service()
    data = service.get_cached_data()
    return {
        "success": True,
        "data": data,
        "companies": list(data.keys()),
        "count": len(data),
    }


@router.post(
    "/analyze-issues",
    summary="SK 17개 이슈 기반 벤치마킹 분석",
    description="""
    경쟁사 보고서를 SK Inc. 17개 이슈 기준으로 분석합니다.

    **분석 방식:**
    1. 보고서에서 이중중대성 평가 섹션 추출
    2. 회사의 중요 이슈 목록 식별
    3. SK 17개 이슈와 매칭하여 커버리지 판정

    **결과:**
    - 각 이슈별 coverage (Yes/Partially/No)
    - 매칭된 회사 이슈명
    - 관련 페이지 번호
    """,
)
async def analyze_company_issues(
    company_name: str,
    pdf_path: str,
):
    """
    SK 17개 이슈 기반 회사 분석

    Args:
        company_name: 회사명
        pdf_path: PDF 파일 경로

    Returns:
        17개 이슈별 분석 결과
    """
    logger.info(f"Analyzing {company_name} for SK 17 issues")

    if not os.path.exists(pdf_path):
        return {
            "success": False,
            "message": f"파일을 찾을 수 없습니다: {pdf_path}",
        }

    try:
        service = get_benchmark_service()
        result = await service.analyze_company_issues(pdf_path, company_name)

        # 요약 통계
        yes_count = sum(1 for r in result.values() if r["coverage"] == "Yes")
        partially_count = sum(1 for r in result.values() if r["coverage"] == "Partially")
        no_count = sum(1 for r in result.values() if r["coverage"] == "No")

        return {
            "success": True,
            "company_name": company_name,
            "data": result,
            "summary": {
                "total_issues": 17,
                "full_coverage": yes_count,
                "partial_coverage": partially_count,
                "no_coverage": no_count,
                "coverage_rate": round((yes_count + partially_count * 0.5) / 17 * 100, 1),
            },
        }

    except Exception as e:
        logger.error(f"Error analyzing company issues: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"분석 중 오류가 발생했습니다: {str(e)}",
        }


@router.post(
    "/upload-and-analyze",
    summary="PDF 업로드 및 SK 17개 이슈 분석",
    description="""
    여러 회사의 PDF를 업로드하고 SK 17개 이슈 기준으로 일괄 분석합니다.

    **주의:** 분석에 회사당 1-2분 소요될 수 있습니다.
    """,
)
async def upload_and_analyze(
    files: List[UploadFile] = File(..., description="PDF 파일들"),
    storage: FileStorageService = Depends(get_file_storage_service),
):
    """PDF 업로드 후 SK 17개 이슈 분석"""
    logger.info(f"Received {len(files)} files for upload and analysis")

    service = get_benchmark_service()
    success_companies = []
    failed_companies = []
    results = {}

    for file in files:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            continue

        company_name = file.filename.rsplit(".", 1)[0]

        try:
            # Delegate file storage to infra layer
            doc_info = await storage.save_benchmark_file(file, company_name)
            filepath = doc_info["path"]

            # 분석
            result = await service.analyze_company_issues(filepath, company_name)
            results[company_name] = result
            success_companies.append(company_name)

            logger.info(f"Successfully analyzed: {company_name}")

        except Exception as e:
            logger.error(f"Error analyzing {company_name}: {e}")
            failed_companies.append(company_name)

    return {
        "success": True,
        "count": len(success_companies),
        "success_companies": success_companies,
        "failed_companies": failed_companies,
        "data": results,
    }


@router.delete(
    "/data/{company_name}",
    summary="회사 분석 데이터 삭제",
    description="특정 회사의 캐시된 분석 데이터를 삭제합니다.",
)
async def delete_company_data(company_name: str):
    """회사 분석 데이터 삭제"""
    service = get_benchmark_service()

    if service.delete_company_cache(company_name):
        logger.info(f"Deleted cache for: {company_name}")
        return {"success": True, "message": f"{company_name} 데이터 삭제 완료"}
    else:
        return {"success": False, "message": f"{company_name} 데이터를 찾을 수 없습니다"}


@router.get(
    "/health",
    summary="벤치마킹 서비스 헬스체크",
    description="벤치마킹 서비스 상태를 확인합니다.",
)
async def health_check():
    """벤치마킹 서비스 헬스체크"""
    service = get_benchmark_service()
    cached_companies = service.get_cached_companies()

    return {
        "status": "healthy",
        "service": "benchmark-analysis",
        "cached_companies": len(cached_companies),
        "sk_issues_count": 18,
    }


@router.post(
    "/reanalyze-all",
    summary="전체 회사 재분석 (새 이슈 기준)",
    description="""
    기존 벤치마킹 폴더의 모든 PDF를 새 18개 이슈 기준으로 재분석합니다.

    **주의:**
    - 기존 캐시를 모두 삭제합니다
    - 분석에 상당한 시간이 소요됩니다 (회사당 1-2분)
    """,
)
async def reanalyze_all():
    """
    기존 벤치마킹 폴더의 모든 PDF를 새 18개 이슈 기준으로 재분석
    """
    from pathlib import Path
    from app.services.benchmark_service import LEGACY_UPLOADS_DIR, LEGACY_CACHE_FILE

    logger.info("Starting full re-analysis with 18 issues...")

    # 1. 기존 캐시 백업 및 삭제
    if LEGACY_CACHE_FILE.exists():
        backup_path = LEGACY_CACHE_FILE.with_suffix('.json.bak')
        shutil.copy(LEGACY_CACHE_FILE, backup_path)
        logger.info(f"Backed up cache to {backup_path}")

        # 캐시 파일 비우기
        with open(LEGACY_CACHE_FILE, 'w') as f:
            f.write('{}')
        logger.info("Cleared cache file")

    # 2. 서비스 재초기화 (캐시 다시 로드)
    from app.services import benchmark_service as bs
    bs._benchmark_service = None
    service = get_benchmark_service()

    # 3. PDF 파일 목록 수집 (회사별 최신 파일만)
    if not LEGACY_UPLOADS_DIR.exists():
        return {
            "success": False,
            "message": f"업로드 폴더가 없습니다: {LEGACY_UPLOADS_DIR}",
        }

    # 회사별 최신 PDF 찾기
    company_pdfs = {}
    for pdf_file in LEGACY_UPLOADS_DIR.glob("*.pdf"):
        filename = pdf_file.name
        # 회사명 추출 (타임스탬프 제거)
        parts = filename.rsplit("_", 2)
        if len(parts) >= 3 and parts[-1].endswith('.pdf'):
            company_name = parts[0]
        else:
            company_name = filename.rsplit(".", 1)[0]

        # 최신 파일 유지
        if company_name not in company_pdfs or pdf_file.stat().st_mtime > company_pdfs[company_name].stat().st_mtime:
            company_pdfs[company_name] = pdf_file

    logger.info(f"Found {len(company_pdfs)} companies to analyze")

    # 4. 회사별 재분석
    success_companies = []
    failed_companies = []

    for company_name, pdf_path in company_pdfs.items():
        try:
            logger.info(f"Analyzing {company_name}...")
            result = await service.analyze_company_issues(str(pdf_path), company_name)

            yes_count = sum(1 for r in result.values() if r["coverage"] == "Yes")
            logger.info(f"  -> {company_name}: {yes_count}/18 issues covered")

            success_companies.append({
                "name": company_name,
                "yes_count": yes_count,
            })

        except Exception as e:
            logger.error(f"Failed to analyze {company_name}: {e}")
            failed_companies.append({
                "name": company_name,
                "error": str(e),
            })

    return {
        "success": True,
        "message": f"{len(success_companies)}개 회사 재분석 완료",
        "analyzed": len(success_companies),
        "failed": len(failed_companies),
        "success_companies": success_companies,
        "failed_companies": failed_companies,
    }


@router.post(
    "/cache/clear-all",
    summary="전체 캐시 삭제",
    description="분석 캐시 파일을 완전히 삭제합니다.",
)
async def clear_all_cache():
    """전체 캐시 삭제"""
    from app.services.benchmark_service import LEGACY_CACHE_FILE

    try:
        if LEGACY_CACHE_FILE.exists():
            # 백업
            backup_path = LEGACY_CACHE_FILE.with_suffix('.json.bak')
            shutil.copy(LEGACY_CACHE_FILE, backup_path)

            # 비우기
            with open(LEGACY_CACHE_FILE, 'w') as f:
                f.write('{}')

            # 서비스 재초기화
            from app.services import benchmark_service as bs
            bs._benchmark_service = None

            logger.info("All cache cleared and service reinitialized")
            return {
                "success": True,
                "message": "캐시가 완전히 삭제되었습니다",
                "backup_path": str(backup_path),
            }
        else:
            return {
                "success": True,
                "message": "삭제할 캐시 파일이 없습니다",
            }

    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return {
            "success": False,
            "message": f"캐시 삭제 중 오류: {str(e)}",
        }


# ============ Document Management Endpoints (for Frontend compatibility) ============

class BenchmarkDocumentInfo(BaseModel):
    """Document information"""
    id: str
    name: str
    size: int
    uploadedAt: str
    status: str


class BenchmarkDocumentListResponse(BaseModel):
    """Response for document list"""
    success: bool
    documents: List[BenchmarkDocumentInfo]
    count: int


class BenchmarkDocumentUploadResponse(BaseModel):
    """Response for document upload"""
    success: bool
    documents: List[BenchmarkDocumentInfo]
    count: int
    message: Optional[str] = None


class BenchmarkEmbedRequest(BaseModel):
    """Request for embedding a document"""
    document_id: str
    document_name: str


@router.get(
    "/documents",
    response_model=BenchmarkDocumentListResponse,
    status_code=status.HTTP_200_OK,
    summary="업로드된 벤치마킹 문서 목록 조회",
    description="업로드된 모든 벤치마킹 문서 목록을 조회합니다.",
)
async def get_benchmark_documents(
    storage: FileStorageService = Depends(get_file_storage_service),
) -> BenchmarkDocumentListResponse:
    """업로드된 벤치마킹 문서 목록 조회"""
    files = storage.list_benchmark_files()
    documents = [
        BenchmarkDocumentInfo(
            id=f["id"],
            name=f["name"],
            size=f["size"],
            uploadedAt=f["uploadedAt"],
            status=f["status"],
        )
        for f in files
    ]

    logger.info(f"Retrieved {len(documents)} benchmark documents")

    return BenchmarkDocumentListResponse(
        success=True,
        documents=documents,
        count=len(documents)
    )


@router.post(
    "/documents/upload",
    response_model=BenchmarkDocumentUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="벤치마킹 문서 업로드",
    description="벤치마킹용 PDF 문서를 업로드합니다.",
)
async def upload_benchmark_documents(
    files: List[UploadFile] = File(..., description="PDF 파일들"),
    storage: FileStorageService = Depends(get_file_storage_service),
) -> BenchmarkDocumentUploadResponse:
    """벤치마킹 문서 업로드"""
    logger.info(f"Received {len(files)} files for benchmark upload")

    uploaded_docs = []

    for file in files:
        if not file.filename:
            continue

        if not file.filename.lower().endswith(".pdf"):
            logger.warning(f"Skipping non-PDF file: {file.filename}")
            continue

        # Delegate to infra layer
        doc_info = await storage.save_benchmark_file(file)

        uploaded_docs.append(BenchmarkDocumentInfo(
            id=doc_info["id"],
            name=doc_info["name"],
            size=doc_info["size"],
            uploadedAt=doc_info["uploadedAt"],
            status=doc_info["status"]
        ))

    if not uploaded_docs:
        return BenchmarkDocumentUploadResponse(
            success=False,
            documents=[],
            count=0,
            message="No valid PDF files uploaded"
        )

    return BenchmarkDocumentUploadResponse(
        success=True,
        documents=uploaded_docs,
        count=len(uploaded_docs)
    )


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="벤치마킹 문서 삭제",
    description="업로드된 벤치마킹 문서를 삭제합니다.",
)
async def delete_benchmark_document(
    document_id: str,
    storage: FileStorageService = Depends(get_file_storage_service),
) -> dict:
    """벤치마킹 문서 삭제"""
    deleted = storage.delete_by_id(document_id, storage.benchmark_dir)
    if deleted:
        return {"success": True, "message": f"Document {document_id} deleted"}
    return {"success": False, "message": f"Document {document_id} not found"}


@router.post(
    "/documents/embed",
    status_code=status.HTTP_200_OK,
    summary="벤치마킹 문서 임베딩 및 SK 18개 이슈 분석",
    description="특정 벤치마킹 문서의 임베딩 처리 및 SK 18개 이슈 기반 분석을 시작합니다.",
)
async def embed_benchmark_document(
    request: BenchmarkEmbedRequest,
    storage: FileStorageService = Depends(get_file_storage_service),
) -> dict:
    """벤치마킹 문서 임베딩 및 SK 18개 이슈 분석 시작"""
    document_id = request.document_id
    document_name = request.document_name

    logger.info(f"Starting embedding and analysis for benchmark document: {document_id} ({document_name})")

    try:
        filepath = storage.get_file_path(document_id)

        if not filepath or not os.path.exists(filepath):
            return {
                "success": False,
                "document_id": document_id,
                "status": "error",
                "message": f"파일을 찾을 수 없습니다: {document_id}"
            }

        # Extract company name from document name (remove .pdf extension)
        company_name = document_name.rsplit(".", 1)[0] if "." in document_name else document_name

        # Perform SK 18 issues analysis
        service = get_benchmark_service()
        result = await service.analyze_company_issues(filepath, company_name)

        # Calculate summary
        yes_count = sum(1 for r in result.values() if r["coverage"] == "Yes")
        partially_count = sum(1 for r in result.values() if r["coverage"] == "Partially")
        no_count = sum(1 for r in result.values() if r["coverage"] == "No")

        logger.info(f"Analysis completed for {company_name}: Yes={yes_count}, Partially={partially_count}, No={no_count}")

        return {
            "success": True,
            "document_id": document_id,
            "company_name": company_name,
            "status": "embedded",
            "message": f"Document {document_name} analyzed successfully",
            "summary": {
                "total_issues": 18,
                "full_coverage": yes_count,
                "partial_coverage": partially_count,
                "no_coverage": no_count,
                "coverage_rate": round((yes_count + partially_count * 0.5) / 18 * 100, 1),
            }
        }

    except Exception as e:
        logger.error(f"Embedding/analysis error for {document_id}: {e}", exc_info=True)

        return {
            "success": False,
            "document_id": document_id,
            "status": "error",
            "message": str(e)
        }


@router.post(
    "/cache/reload",
    status_code=status.HTTP_200_OK,
    summary="벤치마킹 캐시 리로드",
    description="캐시 파일을 다시 로드합니다 (파일 변경 시 사용).",
)
async def reload_cache():
    """캐시 리로드"""
    try:
        service = reload_benchmark_service()
        cached_companies = service.get_cached_companies()

        logger.info(f"Benchmark cache reloaded: {len(cached_companies)} companies")

        return {
            "success": True,
            "message": f"캐시가 리로드되었습니다. {len(cached_companies)}개 회사 데이터 로드됨.",
            "companies": cached_companies,
            "count": len(cached_companies),
        }

    except Exception as e:
        logger.error(f"Cache reload error: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"캐시 리로드 중 오류: {str(e)}",
        }
