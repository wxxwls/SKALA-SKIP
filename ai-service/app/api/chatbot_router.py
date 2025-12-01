"""
ESG Chatbot API Router (CHT-001)

RAG 기반 ESG Q&A 챗봇 API

아키텍처 참고:
- FastAPI는 RAG 검색 및 LLM 답변 생성만 담당
- 대화 히스토리 저장/조회는 Spring Boot → RDB
- 이 API들은 Spring Boot에서만 호출 (프론트엔드 직접 호출 금지)

Data Flow:
1. Spring Boot가 사용자 질문 + 대화 히스토리 전달
2. FastAPI가 VectorDB 검색 + LLM 답변 생성
3. FastAPI가 답변 + 출처 반환
4. Spring Boot가 대화 내역을 RDB에 저장
"""

from typing import List, Optional

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/internal/v1/chatbot",
    tags=["ESG 챗봇"],
)


# ============ Schemas ============

class ChatbotQueryRequest(BaseModel):
    """Chatbot query request"""
    query: str = Field(..., min_length=1, max_length=2000, description="사용자 질문")
    company_id: Optional[str] = Field(None, description="회사 ID (컨텍스트 필터링용)")
    year: Optional[int] = Field(None, description="연도 (컨텍스트 필터링용)")
    session_id: Optional[str] = Field(None, description="세션 ID (대화 히스토리용)")


class SourceInfo(BaseModel):
    """Source attribution info"""
    document_id: str
    document_title: str
    page: Optional[int] = None
    relevance_score: float


class ChatbotQueryResponse(BaseModel):
    """Chatbot query response"""
    success: bool
    answer: str
    sources: List[SourceInfo]
    used_collections: List[str]
    confidence: float = Field(ge=0.0, le=1.0)
    message: Optional[str] = None


# ============ Endpoints ============

@router.post(
    "/query",
    response_model=ChatbotQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="ESG Q&A 챗봇 질의 (CHT-001)",
    description="""
    ESG 관련 질문에 대해 RAG 기반으로 답변합니다.

    **특징:**
    - ESG 표준, 내부 문서, 벤치마킹 보고서 등을 기반으로 답변
    - 반드시 출처(source)를 함께 제공
    - 컨텍스트에 없는 내용은 답변하지 않음 (hallucination 방지)

    **주의사항:**
    - 보고서 전체 생성은 이 API가 아닌 Report API 사용
    - 임의의 수치나 데이터 생성 금지
    """,
)
async def chatbot_query(
    request: ChatbotQueryRequest,
) -> ChatbotQueryResponse:
    """
    ESG 챗봇 질의 API (CHT-001)

    RAG 기반으로 ESG 관련 질문에 답변합니다.
    """
    logger.info(
        f"POST /internal/v1/chatbot/query - query={request.query[:50]}..., "
        f"company_id={request.company_id}"
    )

    # =========================================================================
    # TODO: [SPRING-BOOT-INPUT] Spring Boot에서 입력 데이터 수신
    # =========================================================================
    # Spring Boot가 이 API를 호출할 때 다음 데이터를 함께 전달해야 함:
    #
    # ▶ 필수 데이터:
    # - query: 사용자 질문 (request.query)
    # - user_id: 사용자 ID (인증된 사용자 정보)
    #   → Spring Boot가 JWT 토큰에서 추출
    #
    # ▶ 선택 데이터:
    # - session_id: 대화 세션 ID (request.session_id)
    #   → 없으면 Spring Boot가 새 UUID 생성
    # - company_id: 회사 ID (request.company_id)
    #   → 컨텍스트 필터링용, users.company_id에서 조회 가능
    # - year: 연도 (request.year)
    #   → 컨텍스트 필터링용
    #
    # ▶ 대화 히스토리 (Spring Boot가 RDB에서 조회하여 전달):
    # - chat_history: 이전 대화 내역 리스트
    #   → Spring Boot가 chatbot_histories 테이블에서 조회:
    #     SELECT question_text, answer_text, created_at
    #     FROM chatbot_histories
    #     WHERE user_id = ? AND session_id = ?
    #     ORDER BY created_at ASC
    #     LIMIT 10  -- 최근 10개 대화만 컨텍스트로 사용
    #
    #   → 전달 형식:
    #     [
    #       {"role": "user", "content": "<question_text>"},
    #       {"role": "assistant", "content": "<answer_text>"},
    #       ...
    #     ]
    #
    # ▶ request 스키마에 추가 권장 필드:
    # class ChatbotQueryRequest(BaseModel):
    #     query: str
    #     user_id: int  # 필수 추가
    #     company_id: Optional[str] = None
    #     year: Optional[int] = None
    #     session_id: Optional[str] = None
    #     chat_history: Optional[List[dict]] = Field(None, description="이전 대화 내역")
    # =========================================================================

    # =========================================================================
    # TODO: [AI-RAG-1] 질문 임베딩 생성
    # =========================================================================
    # - BGE-M3 또는 OpenAI 임베딩 모델 사용
    # - 질문 텍스트를 벡터로 변환
    #
    # from app.ai.embedding import get_embedding_model
    # embedding_model = get_embedding_model()
    # query_embedding = await embedding_model.embed(request.query)
    # =========================================================================

    # =========================================================================
    # TODO: [AI-RAG-2] VectorDB에서 관련 문서 검색
    # =========================================================================
    # ▶ 검색 대상 컬렉션 (ChromaDB/Qdrant):
    #
    # 1. esg_standards 컬렉션:
    #    - GRI/SASB/ISSB 표준 문서
    #    - RDB 연계: standards 테이블
    #      → standards.standard_id, standards.framework, standards.code, standards.title
    #    - 메타데이터: {standard_id, framework, code, title, esg_category}
    #
    # 2. internal_docs 컬렉션:
    #    - 회사 내부 문서 (정책, 전략, KPI 등)
    #    - RDB 연계: documents 테이블
    #      → documents.document_id, documents.company_id, documents.title, documents.doc_type
    #    - 메타데이터: {document_id, company_id, title, doc_type, year}
    #    - 필터: company_id = request.company_id
    #
    # 3. benchmarks 컬렉션:
    #    - 경쟁사/동종업계 벤치마킹 보고서
    #    - RDB 연계: documents 테이블 (doc_type='BENCHMARK')
    #    - 필터: industry 기반 필터링
    #
    # 4. news 컬렉션:
    #    - 뉴스/미디어 분석 결과
    #    - RDB 연계: news_articles 테이블
    #      → news_articles.article_id, news_articles.title, news_articles.source
    #    - RDB 연계: news_sentiments 테이블
    #      → news_sentiments.sentiment_label, news_sentiments.sentiment_score
    #    - 메타데이터: {article_id, title, source, published_at, sentiment_label}
    #
    # ▶ 검색 구현:
    # from app.infra.vector_db import get_chroma_client
    # chroma_client = get_chroma_client()
    #
    # retrieved_docs = []
    # for collection_name in ["esg_standards", "internal_docs", "benchmarks", "news"]:
    #     results = await chroma_client.search(
    #         collection=collection_name,
    #         query_embedding=query_embedding,
    #         top_k=5,
    #         filter={"company_id": request.company_id} if request.company_id else None
    #     )
    #     retrieved_docs.extend(results)
    #
    # # 관련성 점수로 정렬 후 상위 10개 선택
    # retrieved_docs = sorted(retrieved_docs, key=lambda x: x.score, reverse=True)[:10]
    # =========================================================================

    # =========================================================================
    # TODO: [AI-RAG-3] LLM 답변 생성
    # =========================================================================
    # 프롬프트 구성:
    # - 시스템 프롬프트: ESG 전문가 역할, 제약사항 명시
    # - 컨텍스트: 검색된 문서 내용
    # - 대화 히스토리: 이전 대화 내용 (멀티턴 대화 지원)
    # - 사용자 질문: 현재 질문
    #
    # 제약사항:
    # - 컨텍스트에 없는 내용은 "해당 정보가 없습니다" 응답
    # - 임의의 수치나 데이터 생성 금지
    # - 출처 명시 필수
    #
    # from app.llm.clients.openai_client import get_openai_client
    # openai_client = get_openai_client()
    #
    # context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    # answer = await openai_client.generate_rag_answer(
    #     query=request.query,
    #     context=context,
    #     chat_history=request.chat_history,
    #     system_prompt=ESG_CHATBOT_SYSTEM_PROMPT
    # )
    # =========================================================================

    # =========================================================================
    # TODO: [AI-RAG-4] 출처 정보 구성
    # =========================================================================
    # ▶ 검색된 문서에서 출처 정보 추출:
    #
    # sources = []
    # for doc in retrieved_docs:
    #     source_type = doc.metadata.get("collection")  # 컬렉션명
    #
    #     if source_type == "esg_standards":
    #         # RDB 연계: standards 테이블
    #         sources.append(SourceInfo(
    #             document_id=str(doc.metadata.get("standard_id")),
    #             document_title=f"{doc.metadata.get('framework')} {doc.metadata.get('code')}: {doc.metadata.get('title')}",
    #             page=doc.metadata.get("page"),
    #             relevance_score=doc.score
    #         ))
    #
    #     elif source_type == "internal_docs":
    #         # RDB 연계: documents 테이블
    #         sources.append(SourceInfo(
    #             document_id=str(doc.metadata.get("document_id")),
    #             document_title=doc.metadata.get("title"),
    #             page=doc.metadata.get("page"),
    #             relevance_score=doc.score
    #         ))
    #
    #     elif source_type == "news":
    #         # RDB 연계: news_articles 테이블
    #         sources.append(SourceInfo(
    #             document_id=str(doc.metadata.get("article_id")),
    #             document_title=f"[{doc.metadata.get('source')}] {doc.metadata.get('title')}",
    #             page=None,
    #             relevance_score=doc.score
    #         ))
    #
    # used_collections = list(set(doc.metadata.get("collection") for doc in retrieved_docs))
    #
    # ▶ SourceInfo 응답 형식:
    # - document_id: RDB 테이블의 PK (standard_id, document_id, article_id)
    # - document_title: 출처 제목 (표준명, 문서명, 뉴스 제목)
    # - page: 페이지 번호 (있는 경우)
    # - relevance_score: 유사도 점수 (0.0 ~ 1.0)
    # =========================================================================

    # =========================================================================
    # TODO: [AI-RAG-5] 신뢰도 점수 계산
    # =========================================================================
    # - 검색된 문서의 평균 관련성 점수
    # - 답변 생성 시 컨텍스트 활용도
    #
    # confidence = sum(doc.score for doc in retrieved_docs) / len(retrieved_docs) if retrieved_docs else 0.0
    # =========================================================================

    # =========================================================================
    # [PLACEHOLDER] 현재는 샘플 응답 반환
    # 위 TODO 구현 완료 후 제거
    # =========================================================================
    return ChatbotQueryResponse(
        success=True,
        answer="현재 ESG 챗봇 기능은 개발 중입니다. RAG 파이프라인이 구현되면 ESG 표준, 내부 문서, 벤치마킹 보고서 등을 기반으로 질문에 답변드릴 수 있습니다.",
        sources=[
            SourceInfo(
                document_id="placeholder",
                document_title="시스템 메시지",
                page=None,
                relevance_score=1.0
            )
        ],
        used_collections=["system"],
        confidence=0.0,
        message="챗봇 기능 개발 중 (더미 응답)"
    )

    # =========================================================================
    # TODO: [SPRING-BOOT-OUTPUT] Spring Boot가 대화 내역을 RDB에 저장
    # =========================================================================
    # 이 API의 응답을 받은 Spring Boot는:
    #
    # ▶ chatbot_histories 테이블에 INSERT:
    # INSERT INTO chatbot_histories (
    #     user_id,           -- bigint NOT NULL (JWT에서 추출한 사용자 ID)
    #     session_id,        -- varchar(255) (대화 세션 ID)
    #     question_text,     -- text NOT NULL (request.query)
    #     answer_text,       -- text NOT NULL (response.answer)
    #     model_name,        -- varchar(100) (사용된 LLM 모델명, 예: 'gpt-4')
    #     request_tokens,    -- int (요청 토큰 수, 선택적)
    #     response_tokens,   -- int (응답 토큰 수, 선택적)
    #     created_at,        -- timestamptz DEFAULT now()
    #     updated_at         -- timestamptz DEFAULT now()
    # ) VALUES (?, ?, ?, ?, ?, ?, ?, now(), now());
    #
    # ▶ 출처 정보 저장 (별도 테이블 또는 JSON 컬럼):
    # - 현재 스키마에 chat_sources 테이블이 없음
    # - 옵션 1: chatbot_histories에 sources_json JSONB 컬럼 추가
    #   → sources_json = JSON.stringify(response.sources)
    # - 옵션 2: chat_sources 테이블 신규 생성
    #   CREATE TABLE chat_sources (
    #       source_id       bigserial PRIMARY KEY,
    #       history_id      bigint NOT NULL REFERENCES chatbot_histories(history_id),
    #       document_id     varchar(100) NOT NULL,
    #       document_title  varchar(500),
    #       page            int,
    #       relevance_score numeric(5,4),
    #       created_at      timestamptz DEFAULT now()
    #   );
    #
    # ▶ 응답에서 저장할 데이터:
    # - response.answer → chatbot_histories.answer_text
    # - response.sources → chat_sources 또는 JSON 컬럼
    # - response.confidence → chatbot_histories에 confidence 컬럼 추가 권장
    # - response.used_collections → JSON 컬럼 또는 별도 저장
    # =========================================================================


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="ESG 챗봇 서비스 헬스체크",
    description="ESG 챗봇 서비스 상태를 확인합니다.",
)
async def health_check() -> dict:
    """ESG 챗봇 서비스 헬스체크"""
    return {
        "status": "healthy",
        "module": "esg_chatbot",
    }
