"""
Materiality Assessment API Router (MAT-001, MAT-002, MAT-003)

이해관계자 설문 및 중대성 매트릭스 API

아키텍처 참고:
- FastAPI는 AI 기반 분석/점수 산출만 담당
- 설문 저장, 응답 저장, 매트릭스 저장은 Spring Boot → RDB
- 이 API들은 Spring Boot에서만 호출 (프론트엔드 직접 호출 금지)

Data Flow:
1. [MAT-001] 설문 생성: Spring Boot가 이슈 목록 전달 → FastAPI가 질문 생성
2. [MAT-002] 응답 제출: Spring Boot가 응답 전달 → FastAPI가 점수 산출
3. [MAT-003] 매트릭스 조회: Spring Boot가 설문 결과 전달 → FastAPI가 매트릭스 계산
"""

from typing import List, Optional

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/internal/v1",
    tags=["중대성 평가"],
)


# ============ Schemas ============

class SurveyQuestion(BaseModel):
    """Survey question"""
    id: str
    issue_id: str
    issue_name: str
    question_text: str
    question_type: str  # "likert_5", "likert_7", "open_text"


class CreateSurveyRequest(BaseModel):
    """Request to create stakeholder survey"""
    company_id: str
    year: int
    issues: List[str] = Field(..., description="이슈 ID 목록")
    stakeholder_type: str = Field(..., description="이해관계자 유형 (employee, customer, investor, supplier, community)")


class SurveyResponse(BaseModel):
    """Survey creation response"""
    success: bool
    survey_id: str
    questions: List[SurveyQuestion]
    total_questions: int
    message: Optional[str] = None


class SurveyAnswerItem(BaseModel):
    """Single survey answer"""
    question_id: str
    answer_value: int = Field(..., ge=1, le=7, description="응답 값 (1-7)")
    comment: Optional[str] = None


class SubmitSurveyRequest(BaseModel):
    """Request to submit survey responses"""
    respondent_id: str
    stakeholder_type: str
    answers: List[SurveyAnswerItem]


class SubmitSurveyResponse(BaseModel):
    """Survey submission response"""
    success: bool
    submission_id: str
    answers_count: int
    message: Optional[str] = None


class MaterialityMatrixItem(BaseModel):
    """Single item in materiality matrix"""
    issue_id: str
    issue_name: str
    category: str  # E, S, G
    financial_score: float = Field(ge=0.0, le=10.0)
    impact_score: float = Field(ge=0.0, le=10.0)
    quadrant: str  # "high_priority", "monitor", "maintain", "low_priority"
    stakeholder_importance: float = Field(ge=0.0, le=10.0)
    business_importance: float = Field(ge=0.0, le=10.0)


class MaterialityMatrixResponse(BaseModel):
    """Materiality matrix response"""
    success: bool
    company_id: str
    year: int
    matrix: List[MaterialityMatrixItem]
    total_issues: int
    high_priority_count: int
    message: Optional[str] = None


# ============ Endpoints ============

@router.post(
    "/surveys",
    response_model=SurveyResponse,
    status_code=status.HTTP_200_OK,
    summary="이해관계자 설문 생성 (MAT-001)",
    description="""
    이해관계자 중대성 평가를 위한 설문을 생성합니다.

    **설문 유형:**
    - 직원 (employee)
    - 고객 (customer)
    - 투자자 (investor)
    - 공급업체 (supplier)
    - 지역사회 (community)

    **질문 형식:**
    - 7점 리커트 척도 (매우 중요하지 않음 ~ 매우 중요함)
    """,
)
async def create_survey(
    request: CreateSurveyRequest,
) -> SurveyResponse:
    """
    이해관계자 설문 생성 API (MAT-001)
    """
    logger.info(
        f"POST /internal/v1/surveys - company_id={request.company_id}, "
        f"stakeholder_type={request.stakeholder_type}, issues={len(request.issues)}"
    )

    # =========================================================================
    # TODO: [SPRING-BOOT-INPUT] Spring Boot에서 입력 데이터 수신
    # =========================================================================
    # Spring Boot가 이 API를 호출할 때 다음 데이터를 함께 전달:
    #
    # ▶ 1. 기본 정보 (request body):
    # - company_id: bigint (companies.company_id)
    # - year: int
    # - stakeholder_type: varchar(50) -- 'employee'|'customer'|'investor'|'supplier'|'community'
    #
    # ▶ 2. 이슈 상세 정보 (Spring Boot가 RDB에서 조회하여 전달):
    # Spring Boot가 issues + issue_pools 테이블에서 조회:
    #
    # SELECT i.issue_id, i.title, i.description, i.esg_category
    # FROM issues i
    # JOIN issue_pools ip ON i.issue_pool_id = ip.issue_pool_id
    # WHERE ip.company_id = :company_id
    #   AND ip.year = :year
    #   AND ip.status = 'CONFIRMED'
    #   AND i.status IN ('CANDIDATE', 'SELECTED');
    #
    # → request에 issue_details 필드 추가 권장:
    # issue_details: List[IssueDetail] = [
    #     {
    #         "issue_id": 123,           -- bigint
    #         "title": "기후변화 대응",    -- varchar(255)
    #         "description": "...",       -- text
    #         "esg_category": "E"         -- 'E'|'S'|'G'
    #     },
    #     ...
    # ]
    #
    # ▶ 3. 이해관계자 정보 (선택적):
    # Spring Boot가 stakeholders 테이블에서 조회:
    #
    # SELECT stakeholder_id, name, email, category
    # FROM stakeholders
    # WHERE company_id = :company_id
    #   AND category = :stakeholder_type;
    # =========================================================================

    # =========================================================================
    # TODO: [AI-SURVEY] AI 기반 설문 질문 생성
    # =========================================================================
    # 1. 이해관계자 유형별 맞춤 질문 템플릿 적용
    #    - employee: 업무 관련성, 조직 영향 관점
    #    - customer: 제품/서비스 관련성 관점
    #    - investor: 재무적 리스크/기회 관점
    #    - supplier: 공급망 영향 관점
    #    - community: 지역사회 영향 관점
    #
    # 2. LLM을 활용한 질문 문구 최적화 (선택적)
    #    - 이슈별 맥락에 맞는 질문 생성
    #    - 이해하기 쉬운 표현으로 변환
    #
    # questions = await self._generate_survey_questions(
    #     issues=request.issues,
    #     stakeholder_type=request.stakeholder_type
    # )
    # =========================================================================

    # =========================================================================
    # [PLACEHOLDER] 현재는 기본 템플릿 기반 질문 생성
    # 위 TODO 구현 완료 후 개선
    # =========================================================================
    import uuid
    survey_id = str(uuid.uuid4())

    questions = []
    for i, issue_id in enumerate(request.issues, 1):
        questions.append(SurveyQuestion(
            id=f"q_{i}",
            issue_id=issue_id,
            issue_name=f"이슈 {issue_id}",  # TODO: Spring Boot에서 이슈명 전달받기
            question_text=f"귀하가 생각하시기에 '{issue_id}' 이슈가 회사에 얼마나 중요하다고 생각하십니까?",
            question_type="likert_7"
        ))

    # =========================================================================
    # TODO: [SPRING-BOOT-OUTPUT] Spring Boot가 설문을 RDB에 저장
    # =========================================================================
    # 이 API의 응답(SurveyResponse)을 받은 Spring Boot는:
    #
    # ▶ 1. surveys 테이블에 설문 생성:
    # INSERT INTO surveys (
    #     issue_pool_id,     -- bigint NOT NULL (이슈풀 ID)
    #     title,             -- varchar(255) NOT NULL (예: '2024년 이해관계자 설문')
    #     status,            -- varchar(20) NOT NULL DEFAULT 'OPEN' ('OPEN'|'CLOSED')
    #     start_date,        -- timestamptz (설문 시작일)
    #     end_date,          -- timestamptz (설문 종료일)
    #     created_at,        -- timestamptz DEFAULT now()
    #     updated_at         -- timestamptz DEFAULT now()
    # ) VALUES (
    #     :issue_pool_id,
    #     '2024년 ' || :stakeholder_type || ' 이해관계자 설문',
    #     'OPEN',
    #     now(),
    #     now() + interval '14 days',
    #     now(),
    #     now()
    # ) RETURNING survey_id;
    #
    # ▶ 2. 응답에서 질문 정보 저장 (별도 테이블 필요시):
    # 현재 스키마에 survey_questions 테이블이 없음.
    # surveys.response_json에 JSON으로 저장하거나 테이블 추가 권장:
    #
    # CREATE TABLE survey_questions (
    #     question_id      bigserial PRIMARY KEY,
    #     survey_id        bigint NOT NULL REFERENCES surveys(survey_id),
    #     issue_id         bigint NOT NULL REFERENCES issues(issue_id),
    #     question_text    text NOT NULL,
    #     question_type    varchar(20) NOT NULL,  -- 'likert_5'|'likert_7'|'open_text'
    #     order_no         int NOT NULL,
    #     created_at       timestamptz DEFAULT now()
    # );
    #
    # for question in response.questions:
    #     INSERT INTO survey_questions (
    #         survey_id, issue_id, question_text, question_type, order_no
    #     ) VALUES (
    #         :survey_id, :question.issue_id, :question.question_text,
    #         :question.question_type, :order_no
    #     );
    # =========================================================================

    return SurveyResponse(
        success=True,
        survey_id=survey_id,
        questions=questions,
        total_questions=len(questions),
        message="설문이 생성되었습니다"
    )


@router.post(
    "/surveys/{survey_id}/responses",
    response_model=SubmitSurveyResponse,
    status_code=status.HTTP_200_OK,
    summary="설문 응답 제출 (MAT-002)",
    description="""
    이해관계자 설문 응답을 제출합니다.

    **응답 형식:**
    - 각 질문에 대해 1-7 값으로 응답
    - 선택적으로 코멘트 추가 가능
    """,
)
async def submit_survey_response(
    survey_id: str,
    request: SubmitSurveyRequest,
) -> SubmitSurveyResponse:
    """
    설문 응답 제출 API (MAT-002)

    Note:
        이 API는 설문 응답 데이터를 검증하고 처리합니다.
        실제 응답 저장은 Spring Boot가 RDB에 수행합니다.
    """
    logger.info(
        f"POST /internal/v1/surveys/{survey_id}/responses - "
        f"respondent_id={request.respondent_id}, answers={len(request.answers)}"
    )

    # =========================================================================
    # TODO: [SPRING-BOOT-DELEGATE] 설문 응답 저장은 Spring Boot에서 처리
    # =========================================================================
    # 설문 응답은 RDB에 저장되어야 하므로 Spring Boot가 처리:
    #
    # ▶ 1. survey_responses 테이블에 응답 저장:
    # INSERT INTO survey_responses (
    #     survey_id,         -- bigint NOT NULL (path parameter)
    #     stakeholder_id,    -- bigint NOT NULL (respondent_id로 조회)
    #     response_json,     -- jsonb NOT NULL (전체 응답 JSON)
    #     submitted_at,      -- timestamptz DEFAULT now()
    #     created_at,        -- timestamptz DEFAULT now()
    #     updated_at         -- timestamptz DEFAULT now()
    # ) VALUES (
    #     :survey_id,
    #     (SELECT stakeholder_id FROM stakeholders WHERE email = :respondent_id),
    #     :response_json,
    #     now(),
    #     now(),
    #     now()
    # ) RETURNING response_id;
    #
    # ▶ 2. response_json 형식:
    # {
    #     "stakeholder_type": "employee",
    #     "answers": [
    #         {"question_id": "q_1", "issue_id": 123, "answer_value": 5, "comment": "..."},
    #         {"question_id": "q_2", "issue_id": 124, "answer_value": 7, "comment": null},
    #         ...
    #     ],
    #     "submitted_at": "2024-01-15T10:30:00Z"
    # }
    #
    # ▶ 3. issue_survey_scores 테이블에 이슈별 점수 집계:
    # INSERT INTO issue_survey_scores (
    #     issue_id,          -- bigint NOT NULL
    #     survey_id,         -- bigint NOT NULL
    #     avg_score,         -- numeric(5,2) (이슈별 평균 점수)
    #     response_count,    -- int (응답 수)
    #     stakeholder_type,  -- varchar(50) (이해관계자 유형별 집계)
    #     created_at,        -- timestamptz DEFAULT now()
    #     updated_at         -- timestamptz DEFAULT now()
    # )
    # SELECT
    #     :issue_id,
    #     :survey_id,
    #     AVG((response_json->'answers'->idx->>'answer_value')::numeric),
    #     COUNT(*),
    #     :stakeholder_type,
    #     now(),
    #     now()
    # FROM survey_responses
    # WHERE survey_id = :survey_id
    # GROUP BY issue_id
    # ON CONFLICT (issue_id, survey_id, stakeholder_type)
    # DO UPDATE SET avg_score = EXCLUDED.avg_score, response_count = EXCLUDED.response_count;
    #
    # ▶ 이 API의 역할:
    # - 응답 데이터 검증 (값 범위, 필수 항목 등)
    # - (선택적) AI 기반 코멘트 분석
    # - Spring Boot가 직접 RDB에 저장하고 이 API 호출을 생략할 수도 있음
    # =========================================================================

    # =========================================================================
    # TODO: [AI-ANALYSIS] 응답 분석 (선택적)
    # =========================================================================
    # 1. 코멘트 감성 분석
    #    - request.answers에서 comment가 있는 경우 분석
    #    - 긍정/부정/중립 분류
    #
    # 2. 응답 패턴 분석
    #    - 이상치 탐지 (의미없는 응답 패턴)
    #    - 응답 일관성 검증
    #
    # analysis_result = await self._analyze_responses(request.answers)
    # =========================================================================

    import uuid
    submission_id = str(uuid.uuid4())

    # =========================================================================
    # TODO: [SPRING-BOOT-OUTPUT] Spring Boot가 응답을 RDB에 저장
    # =========================================================================
    # 이 API의 응답을 받은 Spring Boot는:
    # 1. submission_id를 survey_submissions 테이블에 저장
    # 2. 각 answer를 survey_answers 테이블에 저장
    # 3. respondent_id, survey_id, timestamp 연결
    # =========================================================================

    return SubmitSurveyResponse(
        success=True,
        submission_id=submission_id,
        answers_count=len(request.answers),
        message="설문 응답이 제출되었습니다"
    )


@router.get(
    "/materiality/matrix",
    response_model=MaterialityMatrixResponse,
    status_code=status.HTTP_200_OK,
    summary="중대성 매트릭스 조회 (MAT-003)",
    description="""
    이중중대성 평가 결과 매트릭스를 조회합니다.

    **매트릭스 구성:**
    - X축: 재무적 중대성 (Financial Materiality)
    - Y축: 영향 중대성 (Impact Materiality)

    **분면 (Quadrant):**
    - high_priority: 우선 관리 (양쪽 모두 높음)
    - monitor: 모니터링 (재무 높음, 영향 낮음)
    - maintain: 유지 관리 (재무 낮음, 영향 높음)
    - low_priority: 낮은 우선순위 (양쪽 모두 낮음)
    """,
)
async def get_materiality_matrix(
    company_id: str,
    year: int,
) -> MaterialityMatrixResponse:
    """
    중대성 매트릭스 조회 API (MAT-003)

    Note:
        이 API는 설문 결과를 기반으로 중대성 매트릭스를 계산합니다.
        설문 결과 데이터는 Spring Boot가 RDB에서 조회하여 전달해야 합니다.
    """
    logger.info(f"GET /internal/v1/materiality/matrix - company_id={company_id}, year={year}")

    # =========================================================================
    # TODO: [SPRING-BOOT-INPUT] Spring Boot에서 설문 결과 데이터 수신
    # =========================================================================
    # 현재 API는 company_id, year만 받지만, 실제 구현시:
    # Spring Boot가 RDB에서 다음 데이터를 조회하여 request body로 전달해야 함:
    #
    # ▶ API 변경 권장:
    # POST /internal/v1/materiality/matrix/calculate
    # Body: MaterialityMatrixRequest
    #
    # ▶ 1. 이슈 목록 조회 (issues + issue_pools 테이블):
    # SELECT i.issue_id, i.title AS issue_name, i.esg_category,
    #        i.financial_score AS ai_financial_score,
    #        i.impact_score AS ai_impact_score
    # FROM issues i
    # JOIN issue_pools ip ON i.issue_pool_id = ip.issue_pool_id
    # WHERE ip.company_id = :company_id
    #   AND ip.year = :year
    #   AND ip.status = 'CONFIRMED'
    #   AND i.status = 'SELECTED';
    #
    # → issues = [
    #     {
    #         "issue_id": 123,
    #         "issue_name": "기후변화 대응",
    #         "esg_category": "E",
    #         "ai_financial_score": 8.5,
    #         "ai_impact_score": 9.0
    #     },
    #     ...
    # ]
    #
    # ▶ 2. 이해관계자 설문 결과 집계 (issue_survey_scores 테이블):
    # SELECT iss.issue_id, iss.stakeholder_type,
    #        iss.avg_score, iss.response_count
    # FROM issue_survey_scores iss
    # JOIN surveys s ON iss.survey_id = s.survey_id
    # JOIN issue_pools ip ON s.issue_pool_id = ip.issue_pool_id
    # WHERE ip.company_id = :company_id
    #   AND ip.year = :year;
    #
    # → survey_results = [
    #     {
    #         "issue_id": 123,
    #         "stakeholder_type": "employee",
    #         "avg_score": 7.2,
    #         "response_count": 150
    #     },
    #     ...
    # ]
    #
    # ▶ 3. 내부 평가 결과 (issues 테이블 또는 별도 평가 테이블):
    # 경영진/실무진이 직접 평가한 사업 중요도 점수
    #
    # → internal_assessments = [
    #     {
    #         "issue_id": 123,
    #         "business_score": 8.0,
    #         "evaluator_type": "management"  -- 'management'|'working_level'
    #     },
    #     ...
    # ]
    # =========================================================================

    # =========================================================================
    # TODO: [AI-MATRIX-1] 이해관계자 설문 결과 집계
    # =========================================================================
    # ▶ 이해관계자 유형별 가중치 설정:
    # STAKEHOLDER_WEIGHTS = {
    #     "employee": 0.25,    # 25%
    #     "customer": 0.25,    # 25%
    #     "investor": 0.20,    # 20%
    #     "supplier": 0.15,    # 15%
    #     "community": 0.15    # 15%
    # }
    #
    # ▶ 이슈별 가중 평균 계산:
    # stakeholder_scores = {}
    # for issue in issues:
    #     issue_id = issue["issue_id"]
    #     weighted_sum = 0.0
    #     total_weight = 0.0
    #
    #     for result in survey_results:
    #         if result["issue_id"] == issue_id:
    #             stype = result["stakeholder_type"]
    #             weight = STAKEHOLDER_WEIGHTS.get(stype, 0.1)
    #             weighted_sum += result["avg_score"] * weight
    #             total_weight += weight
    #
    #     stakeholder_importance = weighted_sum / total_weight if total_weight > 0 else 0.0
    #     stakeholder_scores[issue_id] = stakeholder_importance
    #
    # ▶ 결과 데이터 구조:
    # stakeholder_scores = {
    #     123: 7.5,   # issue_id: stakeholder_importance
    #     124: 8.2,
    #     ...
    # }
    # =========================================================================

    # =========================================================================
    # TODO: [AI-MATRIX-2] 재무적/영향 중대성 점수 산출
    # =========================================================================
    # ▶ 1. 영향 중대성 (Impact Materiality) 계산:
    # - 구성 요소:
    #   - 이해관계자 중요도 (stakeholder_importance): 60%
    #   - AI 평가 점수 (ai_impact_score): 30%
    #   - ESG 표준 요구사항 반영도: 10%
    #
    # for issue in issues:
    #     stakeholder_score = stakeholder_scores.get(issue["issue_id"], 5.0)
    #     ai_score = issue.get("ai_impact_score", 5.0)
    #     standard_score = 7.0  # ESG 표준 기반 기본값 (VectorDB 검색으로 동적 계산 가능)
    #
    #     impact_score = (
    #         stakeholder_score * 0.6 +
    #         ai_score * 0.3 +
    #         standard_score * 0.1
    #     )
    #
    # ▶ 2. 재무적 중대성 (Financial Materiality) 계산:
    # - 구성 요소:
    #   - 내부 평가 점수 (business_importance): 50%
    #   - AI 평가 점수 (ai_financial_score): 40%
    #   - 규제 영향도: 10%
    #
    # for issue in issues:
    #     business_score = internal_assessments.get(issue["issue_id"], 5.0)
    #     ai_score = issue.get("ai_financial_score", 5.0)
    #     regulation_score = 6.0  # 규제 영향도 기본값
    #
    #     financial_score = (
    #         business_score * 0.5 +
    #         ai_score * 0.4 +
    #         regulation_score * 0.1
    #     )
    #
    # ▶ 결과 데이터:
    # scores = {
    #     123: {"impact_score": 8.2, "financial_score": 7.8, "stakeholder_importance": 7.5, "business_importance": 8.0},
    #     124: {"impact_score": 6.5, "financial_score": 7.2, ...},
    #     ...
    # }
    # =========================================================================

    # =========================================================================
    # TODO: [AI-MATRIX-3] 분면(Quadrant) 결정
    # =========================================================================
    # 기준점 (threshold) 설정 (예: 5.0 또는 중앙값)
    # - high_priority: financial >= threshold AND impact >= threshold
    # - monitor: financial >= threshold AND impact < threshold
    # - maintain: financial < threshold AND impact >= threshold
    # - low_priority: financial < threshold AND impact < threshold
    #
    # quadrant = self._determine_quadrant(financial_score, impact_score, threshold=5.0)
    # =========================================================================

    # =========================================================================
    # [PLACEHOLDER] 현재는 샘플 데이터 반환
    # 위 TODO 구현 완료 후 제거
    # =========================================================================
    sample_matrix = [
        MaterialityMatrixItem(
            issue_id="climate_change",
            issue_name="기후변화 대응",
            category="E",
            financial_score=8.5,
            impact_score=9.0,
            quadrant="high_priority",
            stakeholder_importance=8.7,
            business_importance=8.3
        ),
        MaterialityMatrixItem(
            issue_id="employee_safety",
            issue_name="임직원 안전보건",
            category="S",
            financial_score=7.2,
            impact_score=8.5,
            quadrant="high_priority",
            stakeholder_importance=8.0,
            business_importance=7.5
        ),
        MaterialityMatrixItem(
            issue_id="governance",
            issue_name="이사회 독립성",
            category="G",
            financial_score=6.5,
            impact_score=5.8,
            quadrant="monitor",
            stakeholder_importance=6.0,
            business_importance=7.0
        ),
    ]

    high_priority_count = sum(1 for item in sample_matrix if item.quadrant == "high_priority")

    # =========================================================================
    # TODO: [SPRING-BOOT-OUTPUT] Spring Boot가 매트릭스 결과를 RDB에 저장
    # =========================================================================
    # 이 API의 응답(MaterialityMatrixResponse)을 받은 Spring Boot는:
    #
    # ▶ 1. issues 테이블의 점수 업데이트:
    # for item in response.matrix:
    #     UPDATE issues SET
    #         financial_score = :item.financial_score,
    #         impact_score = :item.impact_score,
    #         overall_score = (:item.financial_score + :item.impact_score) / 2,
    #         materiality_type = CASE
    #             WHEN :item.quadrant = 'high_priority' THEN 'DOUBLE'
    #             WHEN :item.quadrant = 'monitor' THEN 'FINANCIAL'
    #             WHEN :item.quadrant = 'maintain' THEN 'IMPACT'
    #             ELSE 'LOW'
    #         END,
    #         updated_at = now()
    #     WHERE issue_id = :item.issue_id;
    #
    # ▶ 2. 중대성 매트릭스 이력 저장 (선택적, 테이블 추가 필요):
    # 현재 스키마에 materiality_matrix 테이블이 없음.
    # 버전 관리가 필요한 경우 추가 권장:
    #
    # CREATE TABLE materiality_matrix_history (
    #     matrix_id        bigserial PRIMARY KEY,
    #     issue_pool_id    bigint NOT NULL REFERENCES issue_pools(issue_pool_id),
    #     matrix_data      jsonb NOT NULL,    -- 전체 매트릭스 JSON
    #     version_no       int NOT NULL,
    #     created_by       bigint REFERENCES users(user_id),
    #     created_at       timestamptz DEFAULT now()
    # );
    #
    # INSERT INTO materiality_matrix_history (
    #     issue_pool_id, matrix_data, version_no, created_by, created_at
    # ) VALUES (
    #     :issue_pool_id,
    #     :response_as_json,
    #     (SELECT COALESCE(MAX(version_no), 0) + 1 FROM materiality_matrix_history WHERE issue_pool_id = :issue_pool_id),
    #     :user_id,
    #     now()
    # );
    #
    # ▶ 3. 이슈 상태 업데이트 (high_priority 이슈 선정):
    # UPDATE issues SET
    #     status = 'SELECTED',
    #     priority_rank = :rank,
    #     updated_at = now()
    # WHERE issue_id IN (SELECT issue_id FROM response.matrix WHERE quadrant = 'high_priority');
    #
    # ▶ 4. 응답 데이터 매핑:
    # - response.matrix[].issue_id → issues.issue_id
    # - response.matrix[].financial_score → issues.financial_score
    # - response.matrix[].impact_score → issues.impact_score
    # - response.matrix[].quadrant → issues.materiality_type
    # =========================================================================

    return MaterialityMatrixResponse(
        success=True,
        company_id=company_id,
        year=year,
        matrix=sample_matrix,
        total_issues=len(sample_matrix),
        high_priority_count=high_priority_count,
        message="중대성 매트릭스 조회 완료 (더미 데이터)"
    )


@router.get(
    "/materiality/health",
    status_code=status.HTTP_200_OK,
    summary="중대성 평가 서비스 헬스체크",
    description="중대성 평가 서비스 상태를 확인합니다.",
)
async def health_check() -> dict:
    """중대성 평가 서비스 헬스체크"""
    return {
        "status": "healthy",
        "module": "materiality_assessment",
    }
