"""
ESG Benchmark Analysis Service

경쟁사 지속가능경영 보고서를 분석하여 벤치마킹 결과 생성
- 키워드 기반 분석
- SK Inc. 17개 이슈풀 기반 이중중대성 분석
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import pdfplumber
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.config.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# =============================================================================
# 경로 설정 - 벤치마킹 데이터 활용
# =============================================================================

# 기본 경로는 settings에서 가져오고, 절대 경로로 변환
_BASE_DIR = Path(__file__).parent.parent.parent

DATA_DIR = _BASE_DIR / settings.DATA_DIR
BENCHMARK_VECTOR_STORE_DIR = _BASE_DIR / settings.BENCHMARK_VECTORS_DIR
BENCHMARK_UPLOADS_DIR = _BASE_DIR / settings.BENCHMARK_UPLOADS_DIR
BENCHMARK_CACHE_FILE = _BASE_DIR / settings.BENCHMARK_CACHE_FILE

# Legacy 경로는 환경변수로 설정 가능 (없으면 기본 경로 사용)
LEGACY_BENCHMARK_DIR = Path(os.environ.get("LEGACY_BENCHMARK_DIR", str(BENCHMARK_UPLOADS_DIR)))
LEGACY_VECTOR_STORE_DIR = LEGACY_BENCHMARK_DIR / "vector_stores" if LEGACY_BENCHMARK_DIR != BENCHMARK_UPLOADS_DIR else BENCHMARK_VECTOR_STORE_DIR
LEGACY_UPLOADS_DIR = LEGACY_BENCHMARK_DIR / "uploads" if LEGACY_BENCHMARK_DIR != BENCHMARK_UPLOADS_DIR else BENCHMARK_UPLOADS_DIR
LEGACY_CACHE_FILE = LEGACY_BENCHMARK_DIR / "analysis_cache.json" if LEGACY_BENCHMARK_DIR != BENCHMARK_UPLOADS_DIR else BENCHMARK_CACHE_FILE

# 디렉토리 생성
BENCHMARK_VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
BENCHMARK_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# SK Inc. 18개 이슈풀 (2024년 기준)
# =============================================================================

SK_INC_18_ISSUES = [
    "기후변화 대응",
    "신재생에너지 확대 및 전력 효율화",
    "환경영향 관리",
    "생물다양성 보호",
    "친환경 사업/기술 투자",
    "인재양성 및 다양성",
    "인권경영 고도화",
    "안전보건 관리",
    "공급망 ESG 관리",
    "책임있는 제품/서비스 관리",
    "정보보안 및 프라이버시",
    "지역사회 공헌",
    "포트폴리오 ESG 관리",
    "투명한 이사회 경영",
    "윤리 및 컴플라이언스",
    "주주가치 제고",
    "리스크 관리",
    "ESG 공시 의무화 대응",
]

# 기존 17개 이슈 (호환성 유지)
SK_INC_17_ISSUES = SK_INC_18_ISSUES[:17]  # Deprecated, use SK_INC_18_ISSUES

# 이슈별 관련 키워드 맵 (2024년 18개 이슈 기준)
ISSUE_KEYWORDS = {
    "기후변화 대응": [
        "기후변화", "탄소", "온실가스", "감축", "Net Zero", "탄소중립", "배출량", "RE100",
        "기후 리스크", "GHG", "Scope", "climate change", "carbon", "greenhouse gas",
        "emission", "mitigation", "adaptation", "decarbonization", "net zero"
    ],
    "신재생에너지 확대 및 전력 효율화": [
        "신재생", "재생에너지", "태양광", "풍력", "그린에너지", "청정에너지", "재생가능",
        "전력 효율", "에너지 효율", "renewable", "PPA", "REC", "renewable energy", "solar", "wind"
    ],
    "환경영향 관리": [
        "환경영향평가", "대기", "수질", "토양", "폐기물", "오염물질", "배출", "환경법규",
        "environmental impact", "air quality", "water", "waste", "pollution"
    ],
    "생물다양성 보호": [
        "생물다양성", "생태계", "서식지", "멸종위기", "보전", "biodiversity", "자연자본",
        "ecosystem", "habitat", "conservation", "natural capital"
    ],
    "친환경 사업/기술 투자": [
        "친환경 기술", "녹색기술", "그린 뉴딜", "청정기술", "환경 R&D", "친환경 투자",
        "green technology", "sustainable technology", "eco-friendly"
    ],
    "인재양성 및 다양성": [
        "인재 육성", "교육", "훈련", "역량 개발", "인적자원", "HRD", "리더십", "인재 관리",
        "다양성", "포용", "DEI", "talent development", "training", "human capital", "diversity"
    ],
    "인권경영 고도화": [
        "인권", "노동인권", "아동노동", "강제노동", "차별금지", "인권실사", "인권영향평가",
        "인권경영", "human rights", "labor rights", "child labor", "forced labor", "discrimination"
    ],
    "안전보건 관리": [
        "안전", "보건", "산업재해", "안전사고", "작업환경", "위험성 평가", "KOSHA", "중대재해",
        "safety", "health", "occupational health", "workplace safety"
    ],
    "공급망 ESG 관리": [
        "협력사", "공급망", "SCM", "협력업체", "동반성장", "공급망 실사", "공급망 리스크",
        "supply chain", "supplier", "vendor", "supply chain management"
    ],
    "책임있는 제품/서비스 관리": [
        "제품 책임", "서비스 품질", "고객만족", "품질관리", "서비스 안정성", "SLA",
        "product responsibility", "service quality", "customer satisfaction", "quality management"
    ],
    "정보보안 및 프라이버시": [
        "정보보안", "개인정보", "사이버 보안", "데이터 보호", "ISMS", "GDPR", "해킹", "프라이버시",
        "information security", "cybersecurity", "data protection", "privacy"
    ],
    "지역사회 공헌": [
        "사회공헌", "지역사회", "기부", "봉사", "CSR", "사회적 가치", "지역경제",
        "community", "social contribution", "donation", "volunteering"
    ],
    "포트폴리오 ESG 관리": [
        "포트폴리오", "투자", "자회사", "계열사", "ESG 투자", "지분", "자산관리",
        "손자회사", "멤버사", "portfolio", "investment", "subsidiary"
    ],
    "투명한 이사회 경영": [
        "이사회", "독립이사", "사외이사", "이사회 구성", "ESG 위원회", "지배구조",
        "board of directors", "independent director", "corporate governance"
    ],
    "윤리 및 컴플라이언스": [
        "윤리", "부패", "컴플라이언스", "반부패", "청렴", "윤리규범", "비윤리", "준법",
        "ethics", "anti-corruption", "compliance", "integrity", "code of conduct"
    ],
    "주주가치 제고": [
        "주주", "배당", "주주환원", "IR", "주주총회", "주가", "기업가치", "ROE",
        "shareholder", "dividend", "investor relations", "shareholder value"
    ],
    "리스크 관리": [
        "리스크", "위기관리", "ERM", "리스크 평가", "BCP", "재무리스크", "운영리스크",
        "risk management", "crisis management", "enterprise risk", "business continuity"
    ],
    "ESG 공시 의무화 대응": [
        "ESG 공시", "CSRD", "ISSB", "지속가능성 보고", "공시", "TCFD", "ESRS", "K-ESG",
        "disclosure", "sustainability reporting", "ESG reporting", "mandatory disclosure"
    ],
}


class BenchmarkService:
    """ESG Benchmarking Service for analyzing competitor sustainability reports."""

    def __init__(self):
        """Initialize Benchmark Service."""
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
        )
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0,
            max_tokens=1000,
        )
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._load_legacy_cache()
        logger.info("BenchmarkService initialized")

    def _load_legacy_cache(self):
        """기존 분석 캐시 로드"""
        if LEGACY_CACHE_FILE.exists():
            try:
                with open(LEGACY_CACHE_FILE, "r", encoding="utf-8") as f:
                    self._analysis_cache = json.load(f)
                logger.info(f"Loaded legacy cache with {len(self._analysis_cache)} companies")
            except Exception as e:
                logger.error(f"Failed to load legacy cache: {e}")
                self._analysis_cache = {}
        else:
            self._analysis_cache = {}

    def _save_analysis_cache(self):
        """분석 캐시 저장"""
        try:
            with open(LEGACY_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self._analysis_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def _extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """PDF에서 텍스트 추출"""
        text_content = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        text_content.append({"page": i + 1, "text": text})
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
        return text_content

    def _get_pdf_hash(self, pdf_path: str) -> str:
        """PDF 파일의 해시값 생성 (캐싱용)"""
        hash_md5 = hashlib.md5()
        try:
            with open(pdf_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
        except Exception as e:
            logger.error(f"Error hashing {pdf_path}: {e}")
            return hashlib.md5(pdf_path.encode()).hexdigest()[:16]
        return hash_md5.hexdigest()[:16]

    def _detect_language(self, text_content: List[Dict[str, Any]]) -> str:
        """보고서 언어 감지 (한국어 vs 영어)"""
        if not text_content:
            return "en"
        sample_text = " ".join([item["text"][:500] for item in text_content[:5]])
        korean_chars = sum(1 for c in sample_text if "\uac00" <= c <= "\ud7a3")
        total_chars = len([c for c in sample_text if c.strip()])
        if total_chars == 0:
            return "en"
        korean_ratio = korean_chars / total_chars
        return "ko" if korean_ratio > 0.1 else "en"

    def _get_vector_store(self, pdf_path: str, text_content: List[Dict[str, Any]]) -> Chroma:
        """벡터 스토어 로드 또는 생성 (기존 데이터 우선 사용)"""
        pdf_hash = self._get_pdf_hash(pdf_path)

        # 1. 기존 벤치마킹 폴더에서 먼저 찾기
        legacy_persist_dir = LEGACY_VECTOR_STORE_DIR / pdf_hash
        if legacy_persist_dir.exists() and list(legacy_persist_dir.iterdir()):
            logger.info(f"Loading existing vector DB from legacy: {pdf_hash}")
            return Chroma(
                persist_directory=str(legacy_persist_dir),
                embedding_function=self.embeddings,
            )

        # 2. ai-service 데이터 폴더에서 찾기
        new_persist_dir = BENCHMARK_VECTOR_STORE_DIR / pdf_hash
        if new_persist_dir.exists() and list(new_persist_dir.iterdir()):
            logger.info(f"Loading existing vector DB: {pdf_hash}")
            return Chroma(
                persist_directory=str(new_persist_dir),
                embedding_function=self.embeddings,
            )

        # 3. 새로 생성
        logger.info(f"Creating new vector DB: {pdf_hash}")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", "。", ". ", " ", ""],
        )

        documents = []
        metadatas = []
        for item in text_content:
            chunks = text_splitter.split_text(item["text"])
            for chunk in chunks:
                documents.append(chunk)
                metadatas.append({"page": item["page"]})

        logger.info(f"Creating vector DB with {len(documents)} chunks")

        vectorstore = Chroma.from_texts(
            texts=documents,
            embedding=self.embeddings,
            metadatas=metadatas,
            persist_directory=str(new_persist_dir),
        )
        return vectorstore

    # =========================================================================
    # SK 17개 이슈 기반 분석 (이중중대성 평가)
    # =========================================================================

    async def analyze_company_issues(
        self, pdf_path: str, company_name: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        회사별 SK 17개 이슈 커버리지 분석 (이중중대성 평가 기반)

        Returns:
            {issue_name: {coverage, response, source_pages}, ...}
        """
        logger.info(f"Analyzing {company_name} for SK 17 issues...")

        # 캐시 확인
        if company_name in self._analysis_cache:
            logger.info(f"Returning cached result for {company_name}")
            return self._analysis_cache[company_name]

        # PDF 텍스트 추출
        text_content = self._extract_text_from_pdf(pdf_path)
        if not text_content:
            return {issue: {"coverage": "No", "response": "PDF 추출 실패", "source_pages": []}
                    for issue in SK_INC_18_ISSUES}

        language = self._detect_language(text_content)
        logger.info(f"Detected language: {'Korean' if language == 'ko' else 'English'}")

        # 벡터 스토어 로드/생성
        vectorstore = self._get_vector_store(pdf_path, text_content)

        # Step 1: 이중중대성 평가에서 중요 이슈 목록 추출
        logger.info(f"[Step 1] Extracting material issues from {company_name}...")
        company_material_issues, materiality_pages = await self._extract_material_issues(
            vectorstore, language
        )
        logger.info(f"Found {len(company_material_issues)} material issues")

        # Step 2: SK 17개 이슈와 매칭
        logger.info(f"[Step 2] Matching with SK 17 issues...")
        issue_coverage = await self._match_sk_issues(
            vectorstore, language, company_material_issues, materiality_pages
        )

        # 캐시 저장
        self._analysis_cache[company_name] = issue_coverage
        self._save_analysis_cache()

        return issue_coverage

    async def _extract_material_issues(
        self, vectorstore: Chroma, language: str
    ) -> tuple[List[str], List[int]]:
        """이중중대성 평가 섹션에서 중요 이슈 목록 추출"""
        retriever = vectorstore.as_retriever(search_kwargs={"k": 70})

        if language == "ko":
            query = """
이 지속가능경영 보고서에서 회사가 이중중대성 평가(Double Materiality Assessment) 또는 중요성 평가를 통해 선정한 모든 중요 이슈의 이름을 찾아주세요.

다음과 같은 섹션을 찾아보세요:
- 이중중대성 평가
- 중요성 평가
- Materiality Assessment
- 중요 이슈
- Material Topics

출력 형식 (이슈 이름만 나열):
- 이슈1
- 이슈2
...
"""
        else:
            query = """
Find all material topics or issues that this company identified through Double Materiality Assessment or Materiality Assessment in this sustainability report.

Look for sections like:
- Double Materiality Assessment
- Materiality Assessment
- Material Topics
- Material Issues

Output format (list topic names only):
- Topic 1
- Topic 2
...
"""

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
        )

        response = qa_chain.invoke({"query": query})
        result_text = response["result"].strip()
        source_docs = response.get("source_documents", [])

        # 이슈 목록 파싱
        issues = [
            line.strip().lstrip("-•*①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳0123456789. ")
            for line in result_text.split("\n")
            if line.strip() and not line.strip().startswith("#")
        ]

        # 페이지 번호 추출
        pages = list(set([doc.metadata.get("page", 0) for doc in source_docs[:10]]))
        pages.sort()

        return issues, pages

    async def _match_sk_issues(
        self,
        vectorstore: Chroma,
        language: str,
        company_issues: List[str],
        materiality_pages: List[int],
    ) -> Dict[str, Dict[str, Any]]:
        """SK 17개 이슈와 회사 이슈 매칭"""
        issue_coverage = {}

        # 매칭 점수 계산
        company_to_sk_matches = {}
        for issue in SK_INC_18_ISSUES:
            keywords = ISSUE_KEYWORDS.get(issue, [])
            issue_normalized = issue.replace(" ", "").replace("(", "").replace(")", "").replace("/", "").lower()

            for company_issue in company_issues:
                company_normalized = company_issue.replace(" ", "").replace("(", "").replace(")", "").replace("/", "").lower()
                score = 0

                if issue_normalized == company_normalized:
                    score = 100
                elif issue_normalized in company_normalized or company_normalized in issue_normalized:
                    score = 90
                else:
                    for keyword in keywords[:10]:
                        kw_norm = keyword.replace(" ", "").lower()
                        if kw_norm in company_normalized and len(kw_norm) > 2:
                            score = max(score, 70)

                if score >= 70:
                    if company_issue not in company_to_sk_matches:
                        company_to_sk_matches[company_issue] = []
                    company_to_sk_matches[company_issue].append((issue, score))

        # 최적 할당
        sk_to_company = {}
        for company_issue, sk_matches in company_to_sk_matches.items():
            best_sk, best_score = max(sk_matches, key=lambda x: x[1])
            if best_sk not in sk_to_company or sk_to_company[best_sk][1] < best_score:
                sk_to_company[best_sk] = (company_issue, best_score)

        # 결과 생성
        retriever = vectorstore.as_retriever(search_kwargs={"k": 50})

        for issue in SK_INC_18_ISSUES:
            if issue in sk_to_company:
                matched_issue, score = sk_to_company[issue]
                issue_coverage[issue] = {
                    "coverage": "Yes",
                    "response": f"매칭: {matched_issue} (유사도 {score}%)",
                    "source_pages": materiality_pages,
                }
            else:
                # 폴백: 보고서 전체 검색
                result = await self._fallback_search(retriever, issue, language)
                issue_coverage[issue] = result

        return issue_coverage

    async def _fallback_search(
        self, retriever, issue: str, language: str
    ) -> Dict[str, Any]:
        """매칭 실패 시 보고서 전체 검색"""
        keywords = ISSUE_KEYWORDS.get(issue, [])

        if language == "ko":
            query = f'이 보고서에서 "{issue}"와 관련된 내용이 있는지 확인해주세요. 키워드: {", ".join(keywords[:5])}. 있으면: 관련 섹션명 (한 줄), 없으면: NOT_FOUND'
        else:
            query = f'Is "{issue}" mentioned in this report? Keywords: {", ".join(keywords[:5])}. If yes: Related section (one line), If no: NOT_FOUND'

        try:
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
            )
            response = qa_chain.invoke({"query": query})
            answer = response["result"].strip()
            source_docs = response.get("source_documents", [])
            source_pages = list(set([doc.metadata.get("page", 0) for doc in source_docs[:3]]))

            if "NOT_FOUND" in answer or "없" in answer:
                # 키워드 직접 체크
                combined_text = " ".join([doc.page_content for doc in source_docs[:5]]).lower()
                found_keywords = [kw for kw in keywords[:10] if kw.lower() in combined_text]

                if len(found_keywords) >= 2:
                    return {
                        "coverage": "Partially",
                        "response": f"키워드 발견: {', '.join(found_keywords[:3])}",
                        "source_pages": source_pages,
                    }
                return {"coverage": "No", "response": "이슈 미발견", "source_pages": source_pages}
            else:
                return {
                    "coverage": "Yes",
                    "response": f"폴백 매칭: {answer.split(chr(10))[0][:100]}",
                    "source_pages": source_pages,
                }
        except Exception as e:
            logger.error(f"Fallback search error: {e}")
            return {"coverage": "No", "response": f"분석 오류: {str(e)}", "source_pages": []}

    # =========================================================================
    # 키워드 기반 분석 (기존 기능 유지)
    # =========================================================================

    async def analyze_keyword_in_report(
        self, pdf_path: str, company_name: str, keyword: str
    ) -> Dict[str, Any]:
        """특정 키워드가 회사 보고서에 어떻게 다루어지는지 분석"""
        logger.info(f"Analyzing '{keyword}' for {company_name}...")

        cache_key = f"{pdf_path}:{keyword}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        text_content = self._extract_text_from_pdf(pdf_path)
        if not text_content:
            return {"coverage": "No", "response": "PDF 텍스트 추출 실패", "source_pages": []}

        language = self._detect_language(text_content)
        vectorstore = self._get_vector_store(pdf_path, text_content)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 50})

        if language == "ko":
            query = f'이 지속가능경영 보고서에서 "{keyword}"와 관련된 내용을 찾아주세요. 관련 내용이 없다면: "NOT_FOUND". 있다면: 핵심 내용을 3-5문장으로 요약'
        else:
            query = f'Find content related to "{keyword}" in this sustainability report. If not found: "NOT_FOUND". If found: Summarize key content in 3-5 sentences'

        try:
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
            )
            response = qa_chain.invoke({"query": query})
            answer = response["result"].strip()
            source_docs = response.get("source_documents", [])
            source_pages = list(set([doc.metadata.get("page", 0) for doc in source_docs[:5]]))
            source_pages.sort()

            if "NOT_FOUND" in answer or "없" in answer:
                coverage = "No"
                result_text = "관련 내용 미발견"
            else:
                combined_text = " ".join([doc.page_content for doc in source_docs[:10]]).lower()
                keyword_count = combined_text.count(keyword.lower())

                if keyword_count >= 5:
                    coverage = "Yes"
                    result_text = answer[:300]
                elif keyword_count >= 2:
                    coverage = "Partially"
                    result_text = answer[:200]
                else:
                    coverage = "No"
                    result_text = "키워드 언급이 부족함"

            result = {"coverage": coverage, "response": result_text, "source_pages": source_pages}
            self._cache[cache_key] = result
            return result

        except Exception as e:
            logger.error(f"Error analyzing {company_name}: {e}")
            return {"coverage": "No", "response": f"분석 오류: {str(e)}", "source_pages": []}

    async def analyze_keyword_for_companies(
        self, keyword: str, companies: List[Dict[str, str]]
    ) -> Dict[str, Dict[str, Any]]:
        """여러 회사에 대해 키워드 분석"""
        logger.info(f"Analyzing keyword '{keyword}' for {len(companies)} companies")
        results = {}
        for company in companies:
            company_name = company["name"]
            pdf_path = company["path"]
            if not os.path.exists(pdf_path):
                results[company_name] = {"coverage": "No", "response": "파일을 찾을 수 없습니다", "source_pages": []}
                continue
            result = await self.analyze_keyword_in_report(pdf_path, company_name, keyword)
            results[company_name] = result
        return results

    # =========================================================================
    # 유틸리티
    # =========================================================================

    def get_sk_17_issues(self) -> List[str]:
        """SK 18개 이슈 목록 반환 (2024년 기준)"""
        return SK_INC_18_ISSUES

    def get_cached_companies(self) -> List[str]:
        """캐시된 회사 목록 반환"""
        return list(self._analysis_cache.keys())

    def get_cached_data(self) -> Dict[str, Any]:
        """전체 캐시 데이터 반환"""
        return self._analysis_cache

    def delete_company_cache(self, company_name: str) -> bool:
        """특정 회사 캐시 삭제"""
        if company_name in self._analysis_cache:
            del self._analysis_cache[company_name]
            self._save_analysis_cache()
            return True
        return False

    def get_benchmark_summary(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """벤치마킹 결과 요약 통계"""
        yes_count = sum(1 for r in results.values() if r.get("coverage") == "Yes")
        partially_count = sum(1 for r in results.values() if r.get("coverage") == "Partially")
        no_count = sum(1 for r in results.values() if r.get("coverage") == "No")
        total = len(results)

        return {
            "total_companies": total,
            "full_coverage": yes_count,
            "partial_coverage": partially_count,
            "no_coverage": no_count,
            "coverage_rate": round((yes_count + partially_count * 0.5) / total * 100, 1) if total else 0,
        }

    def clear_cache(self):
        """캐시 초기화"""
        self._cache.clear()
        logger.info("Keyword cache cleared")


# Singleton
_benchmark_service: Optional[BenchmarkService] = None


def get_benchmark_service() -> BenchmarkService:
    """Get or create BenchmarkService singleton."""
    global _benchmark_service
    if _benchmark_service is None:
        _benchmark_service = BenchmarkService()
    return _benchmark_service


def reload_benchmark_service() -> BenchmarkService:
    """Reload BenchmarkService singleton (for cache refresh)."""
    global _benchmark_service
    _benchmark_service = BenchmarkService()
    return _benchmark_service
