"""
Carbon Trading Signals API Router (CBN-001)

Endpoints for carbon price prediction and trading signals.

IMPORTANT: These are internal APIs called only by Spring Boot, not by the frontend.
"""

from typing import Literal, Optional

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/internal/v1/carbon",
    tags=["탄소 시그널"],
)


# ============ Schemas ============

class CarbonSignalResponse(BaseModel):
    """Carbon trading signal response"""
    signal: Literal["BUY", "SELL", "HOLD"]
    confidence: float = Field(ge=0.0, le=1.0)
    predicted_price: float
    current_price: float
    price_change_percent: float
    recommendation: str
    analysis_date: str


class CarbonSignalsListResponse(BaseModel):
    """List of carbon signals response"""
    success: bool
    signals: list[CarbonSignalResponse]
    count: int
    message: Optional[str] = None


# ============ Endpoints ============

@router.get(
    "/signals",
    response_model=CarbonSignalsListResponse,
    status_code=status.HTTP_200_OK,
    summary="탄소 시그널 조회 (CBN-001)",
    description="""
    탄소 가격 예측 및 거래 시그널을 조회합니다.

    **시그널 종류:**
    - BUY: 매수 추천 (예측 가격 > 현재 가격 5% 이상, 신뢰도 70% 이상)
    - SELL: 매도 추천 (예측 가격 < 현재 가격 5% 이상, 신뢰도 70% 이상)
    - HOLD: 관망 추천

    **응답 내용:**
    - 시그널 (BUY/SELL/HOLD)
    - 신뢰도 (0.0 ~ 1.0)
    - 예측 가격
    - 현재 가격
    - 추천 근거
    """,
)
async def get_carbon_signals() -> CarbonSignalsListResponse:
    """
    탄소 시그널 조회 API (CBN-001)

    현재는 더미 데이터를 반환합니다.
    실제 구현 시 ML 모델 또는 외부 API를 연동합니다.
    """
    logger.info("GET /internal/v1/carbon/signals")

    # TODO: Implement actual carbon price prediction
    # For now, return placeholder data
    from datetime import datetime

    dummy_signal = CarbonSignalResponse(
        signal="HOLD",
        confidence=0.65,
        predicted_price=85000.0,
        current_price=84500.0,
        price_change_percent=0.59,
        recommendation="현재 탄소 가격은 안정적인 추세를 보이고 있습니다. 단기적인 변동성이 낮아 관망을 권장합니다.",
        analysis_date=datetime.now().isoformat()
    )

    return CarbonSignalsListResponse(
        success=True,
        signals=[dummy_signal],
        count=1,
        message="탄소 시그널 조회 완료 (더미 데이터)"
    )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="탄소 시그널 서비스 헬스체크",
    description="탄소 시그널 서비스 상태를 확인합니다.",
)
async def health_check() -> dict:
    """탄소 시그널 서비스 헬스체크"""
    return {
        "status": "healthy",
        "module": "carbon_trading",
    }
