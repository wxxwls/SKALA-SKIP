"""
Issue Pool Service - ESG 이슈풀 생성 서비스

기능:
- ESG 이슈 후보군 생성 (RAG 기반)
- 이중중대성 점수 산출
- 토픽 클러스터링 및 순위화

아키텍처:
- FastAPI는 AI 연산만 수행
- 모든 RDB 저장/조회는 Spring Boot를 통해 처리
"""
from typing import List, Optional

from app.core.logging import get_logger
from app.schemas.issue_pool_schema import (
    GenerateIssuePoolRequest,
    IssuePoolResponse,
    ScoreTopicRequest,
    ScoreTopicResponse,
    TopicItem,
    SourceAttribution,
)

logger = get_logger(__name__)


class IssuePoolService:
    """
    ESG 이슈풀 생성 서비스

    Responsibilities:
    - ESG 표준/벤치마킹/내부문서/뉴스 기반 이슈 후보 생성
    - 이중중대성(재무적/영향) 점수 산출
    - 토픽 클러스터링 및 최종 이슈 선정

    Data Flow:
    - Input: Spring Boot에서 전달받은 회사 정보, 내부 문서 데이터
    - Output: AI가 생성한 이슈풀 후보 (Spring Boot가 RDB에 저장)
    """

    def __init__(self):
        """Initialize IssuePoolService with AI components."""
        # TODO: [AI-INIT] AI 컴포넌트 초기화
        # - OpenAI/LLM 클라이언트 초기화
        # - VectorDB 클라이언트 초기화 (ChromaDB/Qdrant)
        # - 임베딩 모델 로드 (BGE-M3 등)
        pass

    async def generate_issue_pool(
        self, request: GenerateIssuePoolRequest
    ) -> IssuePoolResponse:
        """
        ESG 이슈풀 생성

        Args:
            request: 이슈풀 생성 요청 (회사 컨텍스트, 소스 선택 옵션)

        Returns:
            IssuePoolResponse: 생성된 이슈 목록 및 메타데이터
        """
        logger.info(
            f"Generating issue pool for company: {request.company_context.company_id}, "
            f"year: {request.company_context.year}"
        )

        # =====================================================================
        # TODO: [SPRING-BOOT-INPUT] Spring Boot에서 입력 데이터 수신
        # =====================================================================
        # Spring Boot가 이 API를 호출할 때 다음 데이터를 함께 전달해야 함:
        #
        # ▶ 1. company_context (회사 기본 정보):
        # Spring Boot가 companies 테이블에서 조회:
        #
        # SELECT company_id, company_name, industry, sector, employee_count, revenue
        # FROM companies
        # WHERE company_id = :company_id;
        #
        # → company_context = {
        #     "company_id": row.company_id,      -- bigint
        #     "company_name": row.company_name,  -- varchar(255)
        #     "industry": row.industry,          -- varchar(100)
        #     "sector": row.sector,              -- varchar(100)
        #     "year": 2024                       -- 요청 연도
        # }
        #
        # ▶ 2. internal_documents (내부 문서 텍스트):
        # Spring Boot가 documents 테이블에서 조회:
        #
        # SELECT document_id, title, doc_type, content_text, year
        # FROM documents
        # WHERE company_id = :company_id
        #   AND year = :year
        #   AND doc_type IN ('POLICY', 'STRATEGY', 'KPI', 'REPORT');
        #
        # → internal_documents = [
        #     {
        #         "document_id": row.document_id,
        #         "title": row.title,
        #         "doc_type": row.doc_type,  -- 'POLICY'|'STRATEGY'|'KPI'|'REPORT'
        #         "content_text": row.content_text,
        #         "year": row.year
        #     },
        #     ...
        # ]
        #
        # ▶ 3. previous_issues (전년도 이슈풀):
        # Spring Boot가 issue_pools + issues 테이블에서 조회:
        #
        # SELECT i.issue_id, i.esg_category, i.title, i.description,
        #        i.financial_score, i.impact_score, i.overall_score, i.status
        # FROM issues i
        # JOIN issue_pools ip ON i.issue_pool_id = ip.issue_pool_id
        # WHERE ip.company_id = :company_id
        #   AND ip.year = :previous_year
        #   AND ip.status = 'CONFIRMED';
        #
        # → previous_issues = [
        #     {
        #         "issue_id": row.issue_id,
        #         "esg_category": row.esg_category,  -- 'E'|'S'|'G'
        #         "title": row.title,
        #         "description": row.description,
        #         "financial_score": row.financial_score,
        #         "impact_score": row.impact_score,
        #         "status": row.status  -- 'CANDIDATE'|'SELECTED'|'DROPPED'
        #     },
        #     ...
        # ]
        # =====================================================================

        # =====================================================================
        # TODO: [AI-STEP-1] ESG 표준 기반 이슈 후보 추출
        # =====================================================================
        # if request.use_standards:
        #
        # ▶ RDB 연계: standards 테이블
        # 테이블 구조:
        # - standard_id: bigserial PRIMARY KEY
        # - framework: varchar(50) NOT NULL  -- 'GRI'|'SASB'|'ISSB'|'TCFD'|'TNFD'
        # - code: varchar(50) NOT NULL       -- 예: '305-1', 'EM-CM-110a.1'
        # - title: varchar(500) NOT NULL     -- 표준 제목
        # - description: text                -- 상세 설명
        # - esg_category: varchar(10)        -- 'E'|'S'|'G'
        # - industry_applicability: jsonb    -- 산업별 적용 가능성
        # - created_at, updated_at: timestamptz
        #
        # ▶ VectorDB 컬렉션: esg_standards
        # - 메타데이터: {standard_id, framework, code, title, esg_category}
        # - 임베딩: description + title 텍스트
        #
        # ▶ 검색 로직:
        # 1. VectorDB에서 산업군 관련 표준 검색
        #    results = await chroma_client.search(
        #        collection="esg_standards",
        #        query=f"{company_context.industry} ESG 공시 요구사항",
        #        filter={"industry_applicability": {"$contains": company_context.industry}},
        #        top_k=20
        #    )
        #
        # 2. 검색 결과에서 이슈 후보 추출
        #    standards_issues = [
        #        {
        #            "source_type": "standard",
        #            "source_id": doc.metadata["standard_id"],
        #            "source_name": f"{doc.metadata['framework']} {doc.metadata['code']}",
        #            "title": doc.metadata["title"],
        #            "esg_category": doc.metadata["esg_category"],
        #            "relevance_score": doc.score
        #        }
        #        for doc in results
        #    ]
        # =====================================================================

        # =====================================================================
        # TODO: [AI-STEP-2] 벤치마킹 보고서 기반 이슈 후보 추출
        # =====================================================================
        # if request.use_benchmarks:
        #
        # ▶ RDB 연계: documents 테이블 (doc_type='BENCHMARK')
        # 테이블 구조:
        # - document_id: bigserial PRIMARY KEY
        # - company_id: bigint (벤치마크 대상 회사, NULL이면 일반 벤치마크)
        # - title: varchar(500) NOT NULL
        # - doc_type: varchar(50) NOT NULL  -- 'BENCHMARK'
        # - file_path: varchar(1000)
        # - content_text: text              -- 문서 전문 텍스트
        # - year: int
        # - industry: varchar(100)          -- 산업군 (동종업계 필터용)
        # - created_at, updated_at: timestamptz
        #
        # ▶ VectorDB 컬렉션: benchmarks
        # - 메타데이터: {document_id, title, industry, year}
        # - 임베딩: content_text 청크
        #
        # ▶ 검색 로직:
        # 1. 동종업계 벤치마킹 보고서 검색
        #    results = await chroma_client.search(
        #        collection="benchmarks",
        #        query=f"{company_context.industry} 지속가능경영 보고서 중대 이슈",
        #        filter={"industry": company_context.industry},
        #        top_k=15
        #    )
        #
        # 2. LLM으로 벤치마크 보고서에서 이슈 추출
        #    prompt = f"""
        #    다음 벤치마킹 보고서들에서 주요 ESG 이슈를 추출하세요.
        #    산업군: {company_context.industry}
        #    보고서 내용: {context}
        #    출력 형식: JSON 배열 [{{"title": "...", "esg_category": "E/S/G", "description": "..."}}]
        #    """
        #    benchmark_issues = await llm_client.generate(prompt)
        #
        # 3. 출처 정보 매핑
        #    for issue in benchmark_issues:
        #        issue["source_type"] = "benchmark"
        #        issue["source_id"] = doc.metadata["document_id"]
        #        issue["source_name"] = doc.metadata["title"]
        # =====================================================================

        # =====================================================================
        # TODO: [AI-STEP-3] 내부 문서 기반 이슈 후보 추출
        # =====================================================================
        # if request.use_internal:
        #
        # ▶ 입력 데이터: request.internal_documents (Spring Boot에서 전달)
        # Spring Boot가 documents 테이블에서 조회한 데이터:
        # [
        #     {
        #         "document_id": 123,           -- bigint
        #         "title": "2024 환경경영 정책",  -- varchar(500)
        #         "doc_type": "POLICY",         -- 'POLICY'|'STRATEGY'|'KPI'|'REPORT'
        #         "content_text": "...",        -- text (문서 전문)
        #         "year": 2024                  -- int
        #     },
        #     ...
        # ]
        #
        # ▶ AI 처리:
        # 1. 내부 문서 텍스트 임베딩 (필요시)
        #    embeddings = await embedding_model.embed_documents(
        #        [doc["content_text"] for doc in internal_documents]
        #    )
        #
        # 2. 토픽 모델링 적용 (BERTopic 권장)
        #    from bertopic import BERTopic
        #    topic_model = BERTopic(language="korean")
        #    topics, probs = topic_model.fit_transform(
        #        [doc["content_text"] for doc in internal_documents]
        #    )
        #
        # 3. ESG 관련 토픽 필터링 및 이슈 추출
        #    topic_info = topic_model.get_topic_info()
        #    internal_issues = []
        #    for topic_id, topic_words in topic_info.iterrows():
        #        # LLM으로 ESG 관련성 판단 및 이슈 생성
        #        issue = await self._classify_topic_to_esg_issue(
        #            topic_words=topic_words,
        #            source_documents=internal_documents
        #        )
        #        if issue:
        #            issue["source_type"] = "internal"
        #            issue["source_ids"] = [doc["document_id"] for doc in related_docs]
        #            internal_issues.append(issue)
        #
        # 4. 출처 연결 (issue_refs 테이블용)
        #    for issue in internal_issues:
        #        issue["refs"] = [
        #            {"ref_type": "DOCUMENT", "ref_id": doc_id}
        #            for doc_id in issue["source_ids"]
        #        ]
        # =====================================================================

        # =====================================================================
        # TODO: [AI-STEP-4] 뉴스/미디어 기반 이슈 후보 추출
        # =====================================================================
        # if request.use_news:
        #
        # ▶ RDB 연계: news_articles + news_sentiments 테이블
        #
        # news_articles 테이블:
        # - article_id: bigserial PRIMARY KEY
        # - title: varchar(500) NOT NULL
        # - source: varchar(100)            -- 언론사명 (예: '한경', '매경')
        # - url: varchar(1000)
        # - published_at: timestamptz
        # - content_text: text              -- 뉴스 본문
        # - company_id: bigint              -- 관련 회사 ID (nullable)
        # - industry: varchar(100)          -- 관련 산업군
        # - created_at, updated_at: timestamptz
        #
        # news_sentiments 테이블:
        # - sentiment_id: bigserial PRIMARY KEY
        # - article_id: bigint NOT NULL REFERENCES news_articles(article_id)
        # - sentiment_label: varchar(20)    -- 'POSITIVE'|'NEGATIVE'|'NEUTRAL'
        # - sentiment_score: numeric(5,4)   -- -1.0 ~ 1.0
        # - esg_category: varchar(10)       -- 'E'|'S'|'G'|null
        # - keywords: jsonb                 -- 추출된 키워드 배열
        # - created_at: timestamptz
        #
        # ▶ VectorDB 컬렉션: news
        # - 메타데이터: {article_id, title, source, published_at, sentiment_label, esg_category}
        # - 임베딩: content_text
        #
        # ▶ 검색 로직:
        # 1. 회사/산업 관련 최근 뉴스 검색
        #    results = await chroma_client.search(
        #        collection="news",
        #        query=f"{company_context.company_name} {company_context.industry} ESG",
        #        filter={
        #            "published_at": {"$gte": "2024-01-01"},
        #            "$or": [
        #                {"company_id": company_context.company_id},
        #                {"industry": company_context.industry}
        #            ]
        #        },
        #        top_k=20
        #    )
        #
        # 2. 뉴스 클러스터링 및 이슈 추출
        #    # 감성 분석 결과 활용
        #    negative_news = [doc for doc in results if doc.metadata["sentiment_label"] == "NEGATIVE"]
        #
        #    # LLM으로 뉴스에서 이슈 추출
        #    prompt = f"""
        #    다음 뉴스 기사들에서 ESG 관련 이슈를 추출하세요.
        #    특히 부정적 뉴스에서 리스크 요인을 식별하세요.
        #    뉴스: {news_context}
        #    """
        #    news_issues = await llm_client.generate(prompt)
        #
        # 3. 출처 연결 (issue_refs 테이블용)
        #    for issue in news_issues:
        #        issue["source_type"] = "news"
        #        issue["refs"] = [
        #            {"ref_type": "NEWS", "ref_id": article_id}
        #            for article_id in related_article_ids
        #        ]
        # =====================================================================

        # =====================================================================
        # TODO: [AI-STEP-5] 이슈 후보 통합 및 클러스터링
        # =====================================================================
        # ▶ 이슈 통합:
        # all_issues = standards_issues + benchmark_issues + internal_issues + news_issues
        #
        # ▶ 클러스터링 로직:
        # 1. 모든 이슈 제목+설명 임베딩
        #    issue_texts = [f"{issue['title']} {issue.get('description', '')}" for issue in all_issues]
        #    issue_embeddings = await embedding_model.embed_documents(issue_texts)
        #
        # 2. 유사도 기반 클러스터링
        #    from sklearn.cluster import AgglomerativeClustering
        #    clustering = AgglomerativeClustering(
        #        n_clusters=None,
        #        distance_threshold=0.3,  # 코사인 유사도 임계값
        #        metric='cosine',
        #        linkage='average'
        #    )
        #    cluster_labels = clustering.fit_predict(issue_embeddings)
        #
        # 3. 클러스터별 대표 이슈 선정
        #    clustered_issues = []
        #    for cluster_id in set(cluster_labels):
        #        cluster_members = [issue for issue, label in zip(all_issues, cluster_labels) if label == cluster_id]
        #        # 가장 높은 relevance_score를 가진 이슈를 대표로 선정
        #        representative = max(cluster_members, key=lambda x: x.get("relevance_score", 0))
        #        # 모든 출처 통합
        #        representative["all_sources"] = [m.get("refs", []) for m in cluster_members]
        #        representative["source_count"] = len(cluster_members)  # 출처 수 (중요도 지표)
        #        clustered_issues.append(representative)
        #
        # ▶ issue_origin_methods 테이블 연계:
        # 각 이슈의 생성 방법 추적:
        # - origin_method_id: bigserial PRIMARY KEY
        # - issue_id: bigint NOT NULL REFERENCES issues(issue_id)
        # - method: varchar(50) NOT NULL  -- 'STD'|'BMK'|'INT'|'NEWS'|'MDA'
        # - source_detail: jsonb          -- {"standard_id": 123} 또는 {"document_id": 456}
        # - created_at: timestamptz
        # =====================================================================

        # =====================================================================
        # TODO: [AI-STEP-6] 이중중대성 점수 산출
        # =====================================================================
        # ▶ 이중중대성(Double Materiality) 평가:
        # - 재무적 중대성 (Financial Materiality): 이슈가 기업 재무에 미치는 영향
        # - 영향 중대성 (Impact Materiality): 기업 활동이 환경/사회에 미치는 영향
        #
        # for issue in clustered_issues:
        #     # 1. 재무적 중대성 점수 산출
        #     financial_prompt = f"""
        #     다음 ESG 이슈가 {company_context.company_name} ({company_context.industry})의
        #     재무적 성과에 미치는 영향을 1-10점으로 평가하세요.
        #
        #     이슈: {issue['title']}
        #     설명: {issue['description']}
        #
        #     평가 기준:
        #     - 규제 리스크 및 벌금 가능성
        #     - 시장 기회 및 경쟁 우위
        #     - 운영 비용 영향
        #     - 투자자/금융기관 관심도
        #
        #     출력 형식: {{"score": 8.5, "rationale": "..."}}
        #     """
        #     financial_result = await llm_client.generate(financial_prompt)
        #
        #     # 2. 영향 중대성 점수 산출
        #     impact_prompt = f"""
        #     다음 ESG 이슈가 환경 및 사회에 미치는 영향을 1-10점으로 평가하세요.
        #
        #     이슈: {issue['title']}
        #     설명: {issue['description']}
        #
        #     평가 기준:
        #     - 환경 영향 (기후변화, 오염, 자원 고갈)
        #     - 사회 영향 (인권, 노동, 지역사회)
        #     - 이해관계자 관심도
        #     - 글로벌 ESG 트렌드 부합도
        #
        #     출력 형식: {{"score": 9.0, "rationale": "..."}}
        #     """
        #     impact_result = await llm_client.generate(impact_prompt)
        #
        #     # 3. 점수 할당
        #     issue["financial_score"] = financial_result["score"]
        #     issue["financial_rationale"] = financial_result["rationale"]
        #     issue["impact_score"] = impact_result["score"]
        #     issue["impact_rationale"] = impact_result["rationale"]
        #     issue["overall_score"] = (issue["financial_score"] + issue["impact_score"]) / 2
        #
        # ▶ RDB 저장 시 컬럼 매핑 (issues 테이블):
        # - issues.financial_score: numeric(5,2) -- 재무적 중대성 점수
        # - issues.impact_score: numeric(5,2)    -- 영향 중대성 점수
        # - issues.overall_score: numeric(5,2)   -- 종합 점수
        # - issues.materiality_type: varchar(20) -- 'FINANCIAL'|'IMPACT'|'DOUBLE' (둘 다 높은 경우)
        # =====================================================================

        # =====================================================================
        # TODO: [AI-STEP-7] 최종 이슈 선정 및 순위화
        # =====================================================================
        # ▶ 순위화 로직:
        # 1. 이중중대성 점수 기준 정렬
        #    final_topics = sorted(
        #        clustered_issues,
        #        key=lambda x: x["overall_score"],
        #        reverse=True
        #    )
        #
        # 2. 상위 N개 선정 (request.max_topics)
        #    final_topics = final_topics[:request.max_topics]
        #
        # 3. 우선순위 순위 부여
        #    for rank, topic in enumerate(final_topics, start=1):
        #        topic["priority_rank"] = rank
        #
        # ▶ 응답 데이터 구성 (TopicItem):
        # final_response_topics = [
        #     TopicItem(
        #         topic_id=f"topic_{uuid.uuid4().hex[:8]}",  # 임시 ID
        #         topic_title=topic["title"],
        #         category=topic["esg_category"],           # 'E'|'S'|'G'
        #         description=topic["description"],
        #         financial_score=topic["financial_score"],
        #         impact_score=topic["impact_score"],
        #         sources=[
        #             SourceAttribution(
        #                 source_type=ref["ref_type"],     # 'STANDARD'|'DOCUMENT'|'NEWS'
        #                 source_name=ref.get("source_name", ""),
        #                 relevance_score=ref.get("relevance_score", 0.0)
        #             )
        #             for ref in topic.get("refs", [])
        #         ],
        #         keywords=topic.get("keywords", [])
        #     )
        #     for topic in final_topics
        # ]
        # =====================================================================

        # =====================================================================
        # [PLACEHOLDER] 현재는 샘플 데이터 반환
        # 위 TODO 구현 완료 후 제거
        # =====================================================================
        sample_topics: List[TopicItem] = [
            TopicItem(
                topic_id="topic_001",
                topic_title="기후변화 대응",
                category="E",
                description="온실가스 배출 관리 및 탄소중립 목표 수립",
                financial_score=8.5,
                impact_score=9.0,
                sources=[
                    SourceAttribution(
                        source_type="standard",
                        source_name="GRI 305",
                        relevance_score=0.95
                    )
                ],
                keywords=["탄소중립", "온실가스", "기후변화", "Net Zero"]
            ),
            TopicItem(
                topic_id="topic_002",
                topic_title="임직원 안전보건",
                category="S",
                description="작업장 안전 관리 및 건강 증진 프로그램",
                financial_score=7.5,
                impact_score=8.5,
                sources=[
                    SourceAttribution(
                        source_type="standard",
                        source_name="GRI 403",
                        relevance_score=0.90
                    )
                ],
                keywords=["산업안전", "보건", "작업환경", "안전관리"]
            ),
            TopicItem(
                topic_id="topic_003",
                topic_title="윤리경영 및 컴플라이언스",
                category="G",
                description="반부패 정책 및 윤리경영 체계 구축",
                financial_score=7.0,
                impact_score=7.5,
                sources=[
                    SourceAttribution(
                        source_type="standard",
                        source_name="GRI 205",
                        relevance_score=0.88
                    )
                ],
                keywords=["윤리경영", "반부패", "컴플라이언스", "준법경영"]
            ),
        ]

        sources_used = []
        if request.use_standards:
            sources_used.append("ESG 표준 (GRI, SASB)")
        if request.use_benchmarks:
            sources_used.append("벤치마킹 보고서")
        if request.use_internal:
            sources_used.append("내부 문서")
        if request.use_news:
            sources_used.append("뉴스/미디어")

        # =====================================================================
        # TODO: [SPRING-BOOT-OUTPUT] Spring Boot가 결과를 RDB에 저장
        # =====================================================================
        # 이 API의 응답(IssuePoolResponse)을 받은 Spring Boot는:
        #
        # ▶ 1. issue_pools 테이블에 이슈풀 생성:
        # INSERT INTO issue_pools (
        #     company_id,      -- bigint NOT NULL (request.company_context.company_id)
        #     year,            -- int NOT NULL (request.company_context.year)
        #     name,            -- varchar(255) NOT NULL (예: '2024년 이슈풀 초안')
        #     generated_by,    -- varchar(50) NOT NULL ('STD'|'MDA'|'INT'|'BMK'|'FINAL')
        #     status,          -- varchar(20) NOT NULL ('DRAFT'|'CONFIRMED'|'ARCHIVED')
        #     created_at,      -- timestamptz DEFAULT now()
        #     updated_at       -- timestamptz DEFAULT now()
        # ) VALUES (
        #     :company_id, :year, :name, 'STD', 'DRAFT', now(), now()
        # ) RETURNING issue_pool_id;
        #
        # ▶ 2. issues 테이블에 각 이슈 저장:
        # for topic in response.topics:
        #     INSERT INTO issues (
        #         issue_pool_id,     -- bigint NOT NULL (위에서 생성된 issue_pool_id)
        #         esg_category,      -- varchar(10) NOT NULL ('E'|'S'|'G')
        #         title,             -- varchar(255) NOT NULL (topic.topic_title)
        #         description,       -- text (topic.description)
        #         financial_score,   -- numeric(5,2) (topic.financial_score)
        #         impact_score,      -- numeric(5,2) (topic.impact_score)
        #         overall_score,     -- numeric(5,2) ((financial + impact) / 2)
        #         priority_rank,     -- int (순위)
        #         materiality_type,  -- varchar(20) ('FINANCIAL'|'IMPACT'|'DOUBLE')
        #         status,            -- varchar(20) NOT NULL ('CANDIDATE'|'SELECTED'|'DROPPED')
        #         created_at,        -- timestamptz DEFAULT now()
        #         updated_at         -- timestamptz DEFAULT now()
        #     ) VALUES (...) RETURNING issue_id;
        #
        # ▶ 3. issue_refs 테이블에 출처 연결:
        # for source in topic.sources:
        #     INSERT INTO issue_refs (
        #         ref_type,          -- varchar(50) NOT NULL ('STANDARD'|'DOCUMENT'|'NEWS')
        #         ref_id,            -- bigint NOT NULL (standard_id, document_id, or article_id)
        #         title,             -- varchar(500) (출처 제목)
        #         url,               -- varchar(1000) (출처 URL, 있는 경우)
        #         created_at         -- timestamptz DEFAULT now()
        #     ) VALUES (...) RETURNING ref_id;
        #
        # ▶ 4. issue_issue_refs 테이블에 이슈-출처 매핑:
        #     INSERT INTO issue_issue_refs (
        #         issue_id,          -- bigint NOT NULL (위에서 생성된 issue_id)
        #         ref_id,            -- bigint NOT NULL (위에서 생성된 ref_id)
        #         relevance_score,   -- numeric(5,4) (유사도 점수)
        #         created_at         -- timestamptz DEFAULT now()
        #     ) VALUES (...);
        #
        # ▶ 5. issue_origin_methods 테이블에 생성 방법 기록:
        #     INSERT INTO issue_origin_methods (
        #         issue_id,          -- bigint NOT NULL
        #         method,            -- varchar(50) NOT NULL ('STD'|'BMK'|'INT'|'NEWS')
        #         source_detail,     -- jsonb (상세 소스 정보)
        #         created_at         -- timestamptz DEFAULT now()
        #     ) VALUES (...);
        # =====================================================================

        return IssuePoolResponse(
            company_id=request.company_context.company_id,
            year=request.company_context.year,
            topics=sample_topics[:request.max_topics],
            total_count=len(sample_topics),
            sources_used=sources_used,
        )

    async def score_topic(
        self, request: ScoreTopicRequest
    ) -> ScoreTopicResponse:
        """
        단일 토픽 이중중대성 점수 산출

        Args:
            request: 점수 산출 요청 (회사 컨텍스트, 토픽 정보)

        Returns:
            ScoreTopicResponse: 재무적/영향 중대성 점수 및 근거
        """
        logger.info(
            f"Scoring topic '{request.topic_title}' for company: "
            f"{request.company_context.company_id}"
        )

        # =====================================================================
        # TODO: [AI-SCORE-1] 관련 컨텍스트 검색 (RAG)
        # =====================================================================
        # ▶ VectorDB에서 토픽 관련 문서 검색:
        #
        # 1. 검색 쿼리 생성
        #    query = f"{request.topic_title} {request.topic_description}"
        #    query_embedding = await embedding_model.embed(query)
        #
        # 2. 다중 컬렉션 검색
        #    relevant_docs = []
        #
        #    # ESG 표준 검색 (standards 테이블 연계)
        #    standards_results = await chroma_client.search(
        #        collection="esg_standards",
        #        query_embedding=query_embedding,
        #        top_k=5
        #    )
        #    relevant_docs.extend(standards_results)
        #
        #    # 내부 문서 검색 (documents 테이블 연계)
        #    internal_results = await chroma_client.search(
        #        collection="internal_docs",
        #        query_embedding=query_embedding,
        #        filter={"company_id": request.company_context.company_id},
        #        top_k=5
        #    )
        #    relevant_docs.extend(internal_results)
        #
        #    # 벤치마킹 보고서 검색
        #    benchmark_results = await chroma_client.search(
        #        collection="benchmarks",
        #        query_embedding=query_embedding,
        #        filter={"industry": request.company_context.industry},
        #        top_k=3
        #    )
        #    relevant_docs.extend(benchmark_results)
        #
        # 3. 컨텍스트 구성
        #    context = "\n\n".join([
        #        f"[{doc.metadata.get('source_type')}] {doc.page_content}"
        #        for doc in relevant_docs
        #    ])
        # =====================================================================

        # =====================================================================
        # TODO: [AI-SCORE-2] 재무적 중대성 점수 산출
        # =====================================================================
        # ▶ LLM 프롬프트:
        # financial_prompt = f"""
        # 당신은 ESG 전문 분석가입니다.
        # 다음 ESG 이슈가 {request.company_context.company_name} ({request.company_context.industry})의
        # 재무적 성과에 미치는 영향을 평가하세요.
        #
        # 이슈: {request.topic_title}
        # 설명: {request.topic_description}
        #
        # 참고 자료:
        # {context}
        #
        # 평가 기준 (각 항목 1-10점):
        # 1. 규제 리스크: 관련 법규 강화 가능성 및 벌금/제재 위험
        # 2. 시장 기회: 신규 시장 진입, 경쟁 우위 확보 가능성
        # 3. 운영 비용: 해당 이슈 대응을 위한 비용 증감
        # 4. 투자자 관심: ESG 투자자/금융기관의 관심도
        #
        # 출력 형식 (JSON):
        # {{
        #     "score": 8.5,  // 1.0 ~ 10.0
        #     "rationale": "근거 설명 (3-5문장)",
        #     "risk_factors": ["리스크 요인 1", "리스크 요인 2"],
        #     "opportunity_factors": ["기회 요인 1", "기회 요인 2"]
        # }}
        # """
        # financial_result = await llm_client.generate(financial_prompt)
        # =====================================================================

        # =====================================================================
        # TODO: [AI-SCORE-3] 영향 중대성 점수 산출
        # =====================================================================
        # ▶ LLM 프롬프트:
        # impact_prompt = f"""
        # 당신은 ESG 전문 분석가입니다.
        # 다음 ESG 이슈가 환경 및 사회에 미치는 영향을 평가하세요.
        #
        # 이슈: {request.topic_title}
        # 설명: {request.topic_description}
        # 회사: {request.company_context.company_name} ({request.company_context.industry})
        #
        # 참고 자료:
        # {context}
        #
        # 평가 기준 (각 항목 1-10점):
        # 1. 환경 영향: 기후변화, 오염, 자원 고갈, 생물다양성 영향
        # 2. 사회 영향: 인권, 노동 조건, 지역사회, 소비자 안전
        # 3. 이해관계자 관심: 직원, 고객, 지역사회, NGO 등의 관심도
        # 4. 글로벌 트렌드: UN SDGs, 국제 ESG 표준과의 부합도
        #
        # 출력 형식 (JSON):
        # {{
        #     "score": 9.0,  // 1.0 ~ 10.0
        #     "rationale": "근거 설명 (3-5문장)",
        #     "environmental_impact": "환경 영향 설명",
        #     "social_impact": "사회 영향 설명"
        # }}
        # """
        # impact_result = await llm_client.generate(impact_prompt)
        #
        # ▶ 응답 데이터 구성:
        # return ScoreTopicResponse(
        #     topic_title=request.topic_title,
        #     financial_score=financial_result["score"],
        #     impact_score=impact_result["score"],
        #     financial_rationale=financial_result["rationale"],
        #     impact_rationale=impact_result["rationale"],
        #     sources=[
        #         SourceAttribution(
        #             source_type=doc.metadata.get("source_type"),
        #             source_name=doc.metadata.get("title"),
        #             relevance_score=doc.score
        #         )
        #         for doc in relevant_docs[:5]  # 상위 5개 출처
        #     ]
        # )
        # =====================================================================

        # =====================================================================
        # [PLACEHOLDER] 현재는 샘플 데이터 반환
        # 위 TODO 구현 완료 후 제거
        # =====================================================================
        return ScoreTopicResponse(
            topic_title=request.topic_title,
            financial_score=7.5,
            impact_score=8.0,
            financial_rationale="해당 이슈는 기업의 재무 성과에 중요한 영향을 미칠 수 있습니다. "
                               "규제 강화 및 시장 변화에 따른 비용 증가 가능성이 있습니다.",
            impact_rationale="해당 이슈는 환경 및 사회에 상당한 영향을 미칩니다. "
                            "이해관계자들의 관심도가 높은 주제입니다.",
            sources=[
                SourceAttribution(
                    source_type="standard",
                    source_name="GRI Standards",
                    relevance_score=0.85
                )
            ]
        )

    # =========================================================================
    # TODO: [AI-HELPER] 내부 헬퍼 메서드 구현
    # =========================================================================
    # async def _extract_issues_from_standards(self, industry: str) -> List[dict]:
    #     """ESG 표준에서 산업별 이슈 후보 추출"""
    #     pass
    #
    # async def _extract_issues_from_benchmarks(self, company_id: str) -> List[dict]:
    #     """벤치마킹 보고서에서 이슈 후보 추출"""
    #     pass
    #
    # async def _extract_issues_from_internal_docs(self, documents: List[str]) -> List[dict]:
    #     """내부 문서에서 이슈 후보 추출 (토픽 모델링)"""
    #     pass
    #
    # async def _extract_issues_from_news(self, company_name: str) -> List[dict]:
    #     """뉴스에서 이슈 후보 추출"""
    #     pass
    #
    # async def _cluster_issues(self, issues: List[dict]) -> List[dict]:
    #     """이슈 클러스터링 및 중복 제거"""
    #     pass
    #
    # async def _calculate_materiality_scores(self, issue: dict, company_context) -> dict:
    #     """이중중대성 점수 산출"""
    #     pass
    #
    # async def _retrieve_context_for_topic(self, topic_title: str, ...) -> List[dict]:
    #     """토픽 관련 컨텍스트 검색"""
    #     pass
    #
    # async def _assess_financial_materiality(self, topic: str, ...) -> dict:
    #     """재무적 중대성 평가"""
    #     pass
    #
    # async def _assess_impact_materiality(self, topic: str, ...) -> dict:
    #     """영향 중대성 평가"""
    #     pass
    # =========================================================================
