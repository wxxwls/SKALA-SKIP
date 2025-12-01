"""
ESG Standards Service - GRI/SASB 표준 추출 및 한국어 중대성 매핑

이 서비스는 다음을 처리합니다:
1. GRI/SASB PDF에서 공시 요구사항 추출
2. 한국어 중대성 항목으로 매핑 (임베딩 + LLM 2단계)
3. 벡터 DB에 저장 및 검색
"""

import json
import os
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from pypdf import PdfReader
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.config.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# 18개 한국어 중대성 항목 (실제 데이터)
KOREAN_MATERIALITY_ITEMS = [
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


class StandardsExtractor:
    """GRI/SASB 표준에서 공시 요구사항 추출"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"
        logger.info("StandardsExtractor initialized")

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """PDF 파일에서 텍스트 추출"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error reading {pdf_path}: {e}")
            return ""

    def chunk_text(self, text: str, max_chars: int = 12000) -> list[str]:
        """텍스트를 처리 가능한 청크로 분할"""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) < max_chars:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def extract_disclosures_with_ai(
        self, text: str, standard_name: str
    ) -> list[dict[str, Any]]:
        """GPT를 사용하여 공시 요구사항 추출"""

        system_prompt = """You are an expert in sustainability reporting standards.
Your task is to extract ALL disclosure requirements from the provided text.

For each disclosure requirement, extract:
1. disclosure_id: The official identifier (e.g., "GRI 201-1", "TC-SI-130a.1")
2. disclosure_title: The short title of the disclosure
3. description: What needs to be disclosed/reported
4. requirements: Specific requirements or metrics to report
5. category: The main category/topic (e.g., "Economic", "Environmental", "Social")

Return ONLY a valid JSON array of disclosure objects. Do not include any markdown formatting or explanations.
Format: [{"disclosure_id": "...", "disclosure_title": "...", "description": "...", "requirements": "...", "category": "..."}]

If no disclosure requirements are found in the text, return an empty array: []"""

        user_prompt = f"""Extract ALL disclosure requirements from this {standard_name} standard text:

{text}

Return a JSON array of disclosure requirements."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )

            content = response.choices[0].message.content.strip()

            # 마크다운 코드 블록 제거
            content = re.sub(r'^```json\s*', '', content)
            content = re.sub(r'^```\s*', '', content)
            content = re.sub(r'\s*```$', '', content)
            content = content.strip()

            disclosures = json.loads(content)

            for disc in disclosures:
                disc['standard'] = standard_name

            return disclosures

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {standard_name}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error extracting from {standard_name}: {e}")
            return []

    def process_gri_standards(self, gri_folder: str) -> list[dict[str, Any]]:
        """GRI 표준 PDF 처리"""
        all_disclosures = []
        gri_path = Path(gri_folder)
        pdf_files = list(gri_path.glob("*.pdf"))

        logger.info(f"Processing {len(pdf_files)} GRI standards...")

        for pdf_file in pdf_files:
            standard_name = f"GRI - {pdf_file.stem}"
            text = self.extract_text_from_pdf(str(pdf_file))

            if not text:
                continue

            chunks = self.chunk_text(text)

            for chunk in chunks:
                disclosures = self.extract_disclosures_with_ai(chunk, standard_name)
                all_disclosures.extend(disclosures)

        return all_disclosures

    def process_sasb_standards(self, sasb_file: str) -> list[dict[str, Any]]:
        """SASB 표준 PDF 처리"""
        all_disclosures = []
        standard_name = f"SASB - {Path(sasb_file).stem}"

        logger.info(f"Processing SASB standard: {standard_name}...")

        text = self.extract_text_from_pdf(sasb_file)

        if not text:
            return []

        chunks = self.chunk_text(text)

        for chunk in chunks:
            disclosures = self.extract_disclosures_with_ai(chunk, standard_name)
            all_disclosures.extend(disclosures)

        return all_disclosures

    def deduplicate_disclosures(
        self, disclosures: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """중복 공시 요구사항 제거"""
        seen_ids = set()
        unique_disclosures = []

        for disc in disclosures:
            disc_id = disc.get('disclosure_id', '')
            if disc_id and disc_id not in seen_ids:
                seen_ids.add(disc_id)
                unique_disclosures.append(disc)
            elif not disc_id:
                unique_disclosures.append(disc)

        return unique_disclosures


class KoreanMaterialityMapper:
    """공시 요구사항을 한국어 중대성 항목으로 매핑 (2단계 접근법)"""

    def __init__(self, shortlist_k: int = 3):
        logger.info("Initializing Korean Materiality Mapper...")
        self.shortlist_k = shortlist_k
        self.korean_items = KOREAN_MATERIALITY_ITEMS

        # 임베딩 생성
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL if hasattr(settings, 'OPENAI_EMBEDDING_MODEL')
            else "text-embedding-3-large"
        )
        self.llm = ChatOpenAI(model=settings.OPENAI_MODEL)

        # 한국어 항목 임베딩 생성
        logger.info("Generating embeddings for Korean materiality items...")
        self.korean_embeddings = self._generate_korean_embeddings()

        # LLM 분류 체인 설정
        self.classification_chain = self._setup_classification_chain()
        logger.info("Korean Materiality Mapper initialized")

    def _generate_korean_embeddings(self) -> np.ndarray:
        """한국어 중대성 항목에 대한 임베딩 생성"""
        vectors = []
        for item in self.korean_items:
            vector = self.embeddings.embed_query(item)
            vectors.append(np.asarray(vector, dtype="float32"))

        vectors = np.vstack(vectors)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-8
        return vectors / norms

    def _setup_classification_chain(self):
        """LLM 분류 체인 설정"""
        classification_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an ESG classification assistant. "
                    "Select the single best Korean materiality item from the provided candidate list. "
                    "Respond ONLY with valid JSON containing keys "
                    "'korean_item', 'confidence' (0-1 float), and 'reason'. "
                    "Do not reference any items outside the candidate list.",
                ),
                (
                    "human",
                    "Disclosure text:\n{disclosure_text}\n\n"
                    "Korean materiality candidates:\n{candidate_text}\n\n"
                    "Remember: choose ONLY from the candidate list.",
                ),
            ]
        )
        return classification_prompt | self.llm | StrOutputParser()

    def find_top_k_candidates(self, disclosure_text: str) -> list[tuple[str, float]]:
        """임베딩 유사도를 사용하여 Top-K 한국어 중대성 후보 찾기"""
        query = np.asarray(
            self.embeddings.embed_query(disclosure_text), dtype="float32"
        )
        norm_query = query / (np.linalg.norm(query) + 1e-8)

        similarities = self.korean_embeddings @ norm_query

        top_k_indices = np.argsort(-similarities)[: self.shortlist_k]
        candidates = [
            (self.korean_items[idx], float(similarities[idx])) for idx in top_k_indices
        ]

        return candidates

    def llm_pick_best_match(
        self, disclosure_text: str, candidates: list[tuple[str, float]]
    ) -> dict[str, Any]:
        """LLM을 사용하여 후보 중 최적의 한국어 중대성 항목 선택"""
        candidate_lines = []
        for rank, (item, sim) in enumerate(candidates, start=1):
            candidate_lines.append(f"{rank}. {item} | similarity={sim:.3f}")

        response = self.classification_chain.invoke(
            {
                "disclosure_text": disclosure_text,
                "candidate_text": "\n".join(candidate_lines),
            }
        )

        try:
            data = json.loads(response)
            korean_item = data.get("korean_item", candidates[0][0])
            confidence = float(data.get("confidence", candidates[0][1]))
            reason = data.get("reason", "")
        except json.JSONDecodeError:
            korean_item = candidates[0][0]
            confidence = candidates[0][1]
            reason = f"Fallback due to parse error: {response}"

        return {
            "korean_item": korean_item,
            "confidence": confidence,
            "reason": reason,
            "candidates": ", ".join(item for item, _ in candidates),
            "similarities": ", ".join(f"{sim:.3f}" for _, sim in candidates),
        }

    def map_disclosure(self, disclosure: dict[str, Any]) -> dict[str, Any]:
        """단일 공시 요구사항을 한국어 중대성 항목으로 매핑"""
        match_text = (
            f"{disclosure['disclosure_title']}. "
            f"{disclosure.get('description', '')}. "
            f"Category: {disclosure.get('category', '')}"
        )

        # 1단계: 임베딩 기반 Top-K 후보 선택
        candidates = self.find_top_k_candidates(match_text)

        # 2단계: LLM 기반 최종 선택
        llm_result = self.llm_pick_best_match(match_text, candidates)

        return {
            "disclosure_id": disclosure["disclosure_id"],
            "disclosure_title": disclosure["disclosure_title"],
            "standard": disclosure["standard"],
            "category": disclosure.get("category", ""),
            "description": disclosure.get("description", ""),
            "requirements": disclosure.get("requirements", ""),
            "korean_materiality": llm_result["korean_item"],
            "confidence_score": llm_result["confidence"],
            "llm_reason": llm_result["reason"],
            "candidate_items": llm_result["candidates"],
            "candidate_similarities": llm_result["similarities"],
        }

    def map_disclosures(self, disclosures: list[dict[str, Any]]) -> pd.DataFrame:
        """모든 공시 요구사항을 한국어 중대성 항목으로 매핑"""
        logger.info(f"Mapping {len(disclosures)} disclosures to Korean categories...")

        results = []
        for disclosure in disclosures:
            result = self.map_disclosure(disclosure)
            results.append(result)

        return pd.DataFrame(results)

    def export_grouped_json(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        """한국어 중대성별로 그룹화된 JSON 내보내기"""
        grouped_data = []

        for korean_item in self.korean_items:
            mapped_disclosures = df[df["korean_materiality"] == korean_item]

            disclosure_list = []
            for _, row in mapped_disclosures.iterrows():
                disclosure_list.append({
                    "disclosure_id": row["disclosure_id"],
                    "disclosure_title": row["disclosure_title"]
                })

            grouped_data.append({
                "issue_title": korean_item,
                "disclosures": disclosure_list
            })

        return grouped_data


class StandardsVectorDB:
    """BGE-M3 임베딩을 사용한 표준 벡터 DB 관리"""

    def __init__(self, persist_directory: str = "chroma_db"):
        """ChromaDB 클라이언트 초기화"""
        import chromadb
        from chromadb.config import Settings

        self.persist_directory = persist_directory

        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # BGE-M3 임베딩 모델 로드
        logger.info("Loading BGE-M3 embedding model...")
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("BGE-M3 model loaded")

        self.collection = self.client.get_or_create_collection(
            name="sustainability_disclosures",
            metadata={"description": "GRI and SASB disclosure requirements"}
        )

    def _create_embedding_text(self, disclosure: dict[str, Any]) -> str:
        """임베딩용 텍스트 표현 생성"""
        parts = []

        if disclosure.get('disclosure_id'):
            parts.append(f"ID: {disclosure['disclosure_id']}")

        if disclosure.get('disclosure_title'):
            parts.append(f"Title: {disclosure['disclosure_title']}")

        if disclosure.get('category'):
            parts.append(f"Category: {disclosure['category']}")

        if disclosure.get('description'):
            parts.append(f"Description: {disclosure['description']}")

        if disclosure.get('requirements'):
            parts.append(f"Requirements: {disclosure['requirements']}")

        return " | ".join(parts)

    def add_disclosures(self, disclosures: list[dict[str, Any]]) -> None:
        """공시 요구사항을 ChromaDB에 추가"""
        if not disclosures:
            logger.info("No disclosures to add")
            return

        logger.info(f"Adding {len(disclosures)} disclosures to ChromaDB...")

        ids = []
        documents = []
        metadatas = []
        embeddings_list = []

        for idx, disclosure in enumerate(disclosures):
            doc_id = f"{disclosure.get('standard', 'unknown')}_{disclosure.get('disclosure_id', idx)}"
            doc_id = doc_id.replace(' ', '_').replace('/', '_')

            doc_text = self._create_embedding_text(disclosure)

            embedding = self.embedding_model.encode(doc_text, normalize_embeddings=True)

            metadata = {
                'standard': disclosure.get('standard', ''),
                'disclosure_id': disclosure.get('disclosure_id', ''),
                'disclosure_title': disclosure.get('disclosure_title', ''),
                'category': disclosure.get('category', ''),
            }

            ids.append(doc_id)
            documents.append(doc_text)
            embeddings_list.append(embedding.tolist())
            metadatas.append(metadata)

        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings_list,
                metadatas=metadatas
            )
            logger.info(f"Successfully added {len(ids)} disclosures to ChromaDB")
        except Exception as e:
            logger.error(f"Error adding to ChromaDB: {e}")

    def search_disclosures(
        self,
        query: str,
        n_results: int = 10,
        filter_standard: str | None = None
    ) -> list[dict[str, Any]]:
        """시맨틱 검색으로 관련 공시 요구사항 검색"""
        query_embedding = self.embedding_model.encode(query, normalize_embeddings=True)

        where_clause = None
        if filter_standard:
            where_clause = {"standard": {"$contains": filter_standard}}

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=where_clause,
            include=["documents", "metadatas", "distances"]
        )

        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'similarity_score': 1 - results['distances'][0][i]
                })

        return formatted_results

    def get_statistics(self) -> dict[str, Any]:
        """저장된 공시 요구사항 통계 조회"""
        all_docs = self.collection.get(include=["metadatas"])

        standard_counts: dict[str, int] = {}
        category_counts: dict[str, int] = {}

        if all_docs['ids']:
            for metadata in all_docs['metadatas']:
                standard = metadata.get('standard', 'Unknown')
                category = metadata.get('category', 'Unknown')

                standard_counts[standard] = standard_counts.get(standard, 0) + 1
                category_counts[category] = category_counts.get(category, 0) + 1

        return {
            'total_disclosures': len(all_docs['ids']),
            'by_standard': standard_counts,
            'by_category': category_counts
        }

    def reset_database(self) -> None:
        """데이터베이스 초기화"""
        self.client.delete_collection(name="sustainability_disclosures")
        self.collection = self.client.get_or_create_collection(
            name="sustainability_disclosures",
            metadata={"description": "GRI and SASB disclosure requirements"}
        )
        logger.info("Database reset complete")
