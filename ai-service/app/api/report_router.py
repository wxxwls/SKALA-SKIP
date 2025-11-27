"""
Report Assistant Router - ESG 보고서 생성 API

내부 전용 API (Spring Boot → FastAPI)
"""

from fastapi import APIRouter, HTTPException, status

from app.core.logging import get_logger
from app.schemas.common_schema import APIResponse
from app.schemas.report_schema import (
    ReportGenerationRequest,
    ReportGenerationResponse,
    ReportModifyRequest,
    ReportModifyResponse,
)
from app.services.report_assistant_service import get_report_assistant_service

logger = get_logger(__name__)

router = APIRouter(
    prefix="/internal/v1/reports",
    tags=["보고서 생성"],
)


@router.post(
    "/generate",
    response_model=ReportGenerationResponse,
    summary="ESG 보고서 생성",
    description="""
    중대성 평가 결과를 기반으로 ESG 보고서를 생성합니다.

    **SK 지속가능경영보고서 '발생영향과 통제' 챕터 스타일**

    각 이슈별로 다음 3개 섹션이 포함됩니다:
    - 실질적/잠재적 영향
    - 대응 전략
    - 중장기 계획 (KPI 포함)

    **주의사항:**
    - 내부 데이터만 사용 (외부 검색 금지)
    - 임의 수치 생성 금지
    - NULL KPI는 안내문 포함
    """,
)
async def generate_report(
    request: ReportGenerationRequest,
) -> ReportGenerationResponse:
    """
    ESG 보고서 생성

    Args:
        request: 보고서 생성 요청 (이슈 목록, KPI 데이터 포함)

    Returns:
        생성된 보고서 HTML 및 메타데이터
    """
    logger.info(
        f"Received report generation request for company: "
        f"{request.company_context.company_id}",
        extra={
            "company_id": request.company_context.company_id,
            "year": request.company_context.year,
            "issue_count": len(request.issues),
        },
    )

    try:
        service = get_report_assistant_service()
        response = await service.generate_report(request)

        if not response.success:
            logger.error(
                f"Report generation failed: {response.error.message if response.error else 'Unknown error'}"
            )

        return response

    except Exception as e:
        logger.error(f"Unexpected error in report generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "ESG-AI-RPT-001",
                "message": "보고서 생성 중 오류가 발생했습니다",
                "details": str(e),
            },
        )


@router.post(
    "/modify",
    response_model=ReportModifyResponse,
    summary="보고서 수정 (챗봇)",
    description="""
    자연어 명령으로 보고서를 수정합니다.

    **예시 명령어:**
    - "ESG Letter를 더 전문적인 어조로 수정해줘"
    - "환경 섹션에 탄소배출 저감 목표를 2030년 50% 감축으로 수정해줘"
    - "거버넌스 섹션에 이사회 독립성 강화 내용 추가해줘"
    """,
)
async def modify_report(
    request: ReportModifyRequest,
) -> ReportModifyResponse:
    """
    보고서 수정 (챗봇 기반)

    Args:
        request: 수정 요청 (현재 보고서 + 수정 지시)

    Returns:
        수정된 보고서
    """
    logger.info(
        f"Received report modification request",
        extra={
            "instruction": request.instruction[:100],
            "company_name": request.company_name,
        },
    )

    try:
        service = get_report_assistant_service()
        response = await service.modify_report(request)

        if response.success:
            logger.info("Report modification successful")
        else:
            logger.error(f"Report modification failed: {response.message}")

        return response

    except Exception as e:
        logger.error(f"Unexpected error in report modification: {str(e)}", exc_info=True)
        return ReportModifyResponse(
            success=False,
            message=f"보고서 수정 중 오류가 발생했습니다: {str(e)}",
        )


@router.get(
    "/health",
    summary="보고서 서비스 헬스체크",
    description="보고서 생성 서비스 상태를 확인합니다.",
)
async def health_check():
    """보고서 서비스 헬스체크"""
    return {
        "status": "healthy",
        "service": "report-assistant",
    }
