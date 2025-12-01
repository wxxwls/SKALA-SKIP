"""
ESG Standards Service

Service for extracting disclosure requirements from GRI/SASB standards
and mapping them to Korean materiality items (18 ESG issues).

Uses ChromaDB + BGE-M3 embeddings for semantic search and mapping.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from openai import AsyncOpenAI
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from tqdm import tqdm

from app.config.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Path to data files
SEED_DATA_PATH = Path(__file__).parent.parent / "data" / "esg_disclosures_seed.json"
ALL_DISCLOSURES_PATH = Path(__file__).parent.parent / "data" / "all_disclosures.json"
CHROMA_DB_PATH = Path(__file__).parent.parent / "data" / "chroma_db"

# 18 Korean materiality items (SK standard)
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

# ESG Category mapping
ESG_CATEGORY_MAP = {
    "기후변화 대응": "E",
    "신재생에너지 확대 및 전력 효율화": "E",
    "환경영향 관리": "E",
    "생물다양성 보호": "E",
    "친환경 사업/기술 투자": "E",
    "인재양성 및 다양성": "S",
    "인권경영 고도화": "S",
    "안전보건 관리": "S",
    "공급망 ESG 관리": "G",
    "책임있는 제품/서비스 관리": "S",
    "정보보안 및 프라이버시": "G",
    "지역사회 공헌": "S",
    "포트폴리오 ESG 관리": "G",
    "투명한 이사회 경영": "G",
    "윤리 및 컴플라이언스": "G",
    "주주가치 제고": "G",
    "리스크 관리": "G",
    "ESG 공시 의무화 대응": "G",
}


class ESGStandardsService:
    """Service for ESG standards analysis using ChromaDB and BGE-M3 embeddings."""

    def __init__(self, persist_directory: str = None):
        """Initialize the service with ChromaDB and BGE-M3 model."""
        # Use pre-existing ChromaDB if available, otherwise use default path
        if persist_directory is None:
            if CHROMA_DB_PATH.exists():
                persist_directory = str(CHROMA_DB_PATH)
                logger.info(f"Using existing ChromaDB at: {persist_directory}")
            else:
                persist_directory = "data/chroma_esg_standards"
                Path(persist_directory).mkdir(parents=True, exist_ok=True)

        self.persist_directory = persist_directory
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.openai_model = settings.OPENAI_MODEL

        # Initialize ChromaDB client with fallback for corrupted DB
        try:
            self.chroma_client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
        except Exception as e:
            logger.warning(f"Failed to load ChromaDB from {persist_directory}: {e}")
            logger.info("Creating new ChromaDB in fallback directory...")
            fallback_dir = "data/chroma_esg_standards_new"
            Path(fallback_dir).mkdir(parents=True, exist_ok=True)
            self.persist_directory = fallback_dir
            self.chroma_client = chromadb.PersistentClient(
                path=fallback_dir,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

        # Load BGE-M3 embedding model
        logger.info("Loading BGE-M3 embedding model...")
        self.embedding_model = SentenceTransformer('BAAI/bge-m3')
        logger.info("BGE-M3 model loaded successfully")

        # Get or create collection for disclosures
        # Try to use existing collection name from pre-existing DB
        try:
            existing_collections = self.chroma_client.list_collections()
            if existing_collections:
                collection_name = existing_collections[0].name
                logger.info(f"Found existing collection: {collection_name}")
            else:
                collection_name = "esg_disclosures"
        except Exception:
            collection_name = "esg_disclosures"

        self.disclosure_collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "GRI and SASB disclosure requirements"}
        )

        # Generate and cache Korean materiality embeddings
        self._korean_embeddings = None
        self._init_korean_embeddings()

        # Load seed data with Korean mappings
        self._disclosure_korean_map: Dict[str, List[str]] = {}
        self._load_seed_data_if_empty()

        # Load all disclosures from JSON for direct reference
        self._all_disclosures: List[Dict[str, Any]] = []
        self._disclosure_embeddings: Optional[np.ndarray] = None
        self._load_all_disclosures()

    def _load_all_disclosures(self):
        """Load all disclosures from JSON file and generate embeddings."""
        if not ALL_DISCLOSURES_PATH.exists():
            logger.warning(f"All disclosures file not found: {ALL_DISCLOSURES_PATH}")
            return

        try:
            with open(ALL_DISCLOSURES_PATH, 'r', encoding='utf-8') as f:
                self._all_disclosures = json.load(f)

            logger.info(f"Loaded {len(self._all_disclosures)} disclosures from JSON")

            # Generate embeddings for all disclosures
            logger.info("Generating embeddings for all disclosures...")
            embeddings_list = []
            for disc in self._all_disclosures:
                # Create text for embedding
                text_parts = []
                if disc.get('disclosure_id'):
                    text_parts.append(disc['disclosure_id'])
                if disc.get('disclosure_title'):
                    text_parts.append(disc['disclosure_title'])
                if disc.get('description'):
                    desc = disc['description']
                    if isinstance(desc, str):
                        text_parts.append(desc[:500])
                if disc.get('category'):
                    text_parts.append(disc['category'])

                embed_text = " | ".join(text_parts)
                embedding = self.embedding_model.encode(embed_text, normalize_embeddings=True)
                embeddings_list.append(embedding)

            self._disclosure_embeddings = np.vstack(embeddings_list)
            logger.info(f"Generated embeddings for {len(self._all_disclosures)} disclosures")

        except Exception as e:
            logger.error(f"Error loading all disclosures: {e}")
            self._all_disclosures = []
            self._disclosure_embeddings = None

    def _load_seed_data_if_empty(self):
        """Load seed data from JSON file if ChromaDB is empty."""
        current_count = self.disclosure_collection.count()
        if current_count > 0:
            logger.info(f"ChromaDB already has {current_count} disclosures - using existing data")
            # Load disclosure-korean mappings from existing data if seed file exists
            self._load_disclosure_korean_map_from_seed()
            return

        if not SEED_DATA_PATH.exists():
            logger.warning(f"Seed data file not found: {SEED_DATA_PATH}")
            return

        try:
            with open(SEED_DATA_PATH, 'r', encoding='utf-8') as f:
                seed_data = json.load(f)

            disclosures = seed_data.get('disclosures', [])
            logger.info(f"Loading {len(disclosures)} disclosures from seed data...")

            # Store disclosures in ChromaDB
            ids = []
            documents = []
            metadatas = []
            embeddings_list = []

            for idx, disc in enumerate(disclosures):
                doc_id = f"{disc.get('standard', 'unknown')}_{disc.get('disclosure_id', idx)}"
                doc_id = doc_id.replace(' ', '_').replace('/', '_')

                doc_text = self._create_embedding_text(disc)
                embedding = self.embedding_model.encode(doc_text, normalize_embeddings=True)

                # Store Korean issues mapping
                korean_issues = disc.get('korean_issues', [])
                self._disclosure_korean_map[disc.get('disclosure_id', '')] = korean_issues

                metadata = {
                    'standard': disc.get('standard', ''),
                    'disclosure_id': disc.get('disclosure_id', ''),
                    'disclosure_title': disc.get('disclosure_title', ''),
                    'category': disc.get('category', ''),
                    'description': disc.get('description', '')[:500] if disc.get('description') else '',
                    'korean_issues': json.dumps(korean_issues, ensure_ascii=False),
                }

                ids.append(doc_id)
                documents.append(doc_text)
                embeddings_list.append(embedding.tolist())
                metadatas.append(metadata)

            self.disclosure_collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings_list,
                metadatas=metadatas
            )
            logger.info(f"Successfully loaded {len(ids)} disclosures from seed data")

        except Exception as e:
            logger.error(f"Error loading seed data: {e}")

    def _load_disclosure_korean_map_from_seed(self):
        """Load disclosure-korean mappings from seed file."""
        if not SEED_DATA_PATH.exists():
            return

        try:
            with open(SEED_DATA_PATH, 'r', encoding='utf-8') as f:
                seed_data = json.load(f)

            for disc in seed_data.get('disclosures', []):
                disc_id = disc.get('disclosure_id', '')
                korean_issues = disc.get('korean_issues', [])
                if disc_id:
                    self._disclosure_korean_map[disc_id] = korean_issues

            logger.info(f"Loaded Korean mappings for {len(self._disclosure_korean_map)} disclosures")
        except Exception as e:
            logger.error(f"Error loading disclosure-korean mappings: {e}")

    def _init_korean_embeddings(self):
        """Generate embeddings for Korean materiality items."""
        logger.info("Generating embeddings for Korean materiality items...")
        embeddings = []
        for item in KOREAN_MATERIALITY_ITEMS:
            emb = self.embedding_model.encode(item, normalize_embeddings=True)
            embeddings.append(emb)
        self._korean_embeddings = np.vstack(embeddings)
        logger.info(f"Generated embeddings for {len(KOREAN_MATERIALITY_ITEMS)} Korean items")

    def _create_embedding_text(self, disclosure: Dict[str, Any]) -> str:
        """Create text representation for embedding."""
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

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file."""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error reading {pdf_path}: {e}")
            return ""

    def chunk_text(self, text: str, max_chars: int = 12000) -> List[str]:
        """Split text into chunks for processing."""
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

    async def extract_disclosures_with_ai(self, text: str, standard_name: str) -> List[Dict[str, Any]]:
        """Use GPT to extract disclosure requirements from text."""
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
            response = await self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )

            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            content = re.sub(r'^```json\s*', '', content)
            content = re.sub(r'^```\s*', '', content)
            content = re.sub(r'\s*```$', '', content)
            content = content.strip()

            # Parse JSON
            disclosures = json.loads(content)

            # Add standard source
            for disc in disclosures:
                disc['standard'] = standard_name

            return disclosures

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {standard_name}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error extracting from {standard_name}: {e}")
            return []

    async def process_standards_folder(self, gri_folder: str, sasb_file: str) -> int:
        """Process GRI and SASB standards and store in ChromaDB."""
        all_disclosures = []

        # Process GRI standards
        gri_path = Path(gri_folder)
        if gri_path.exists():
            pdf_files = list(gri_path.glob("*.pdf"))
            logger.info(f"Processing {len(pdf_files)} GRI standards...")

            for pdf_file in tqdm(pdf_files, desc="GRI Standards"):
                standard_name = f"GRI - {pdf_file.stem}"
                text = self.extract_text_from_pdf(str(pdf_file))

                if not text:
                    continue

                chunks = self.chunk_text(text)
                for chunk in chunks:
                    disclosures = await self.extract_disclosures_with_ai(chunk, standard_name)
                    all_disclosures.extend(disclosures)

        # Process SASB standard
        sasb_path = Path(sasb_file)
        if sasb_path.exists():
            standard_name = f"SASB - {sasb_path.stem}"
            logger.info(f"Processing SASB standard: {standard_name}...")

            text = self.extract_text_from_pdf(sasb_file)
            if text:
                chunks = self.chunk_text(text)
                for chunk in tqdm(chunks, desc="SASB Chunks"):
                    disclosures = await self.extract_disclosures_with_ai(chunk, standard_name)
                    all_disclosures.extend(disclosures)

        # Deduplicate
        all_disclosures = self._deduplicate_disclosures(all_disclosures)

        # Store in ChromaDB
        await self._store_disclosures_in_chromadb(all_disclosures)

        return len(all_disclosures)

    def _deduplicate_disclosures(self, disclosures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate disclosure requirements based on disclosure_id."""
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

    async def _store_disclosures_in_chromadb(self, disclosures: List[Dict[str, Any]]):
        """Store disclosures in ChromaDB with embeddings."""
        if not disclosures:
            logger.warning("No disclosures to store")
            return

        logger.info(f"Storing {len(disclosures)} disclosures in ChromaDB...")

        ids = []
        documents = []
        metadatas = []
        embeddings_list = []

        for idx, disclosure in enumerate(tqdm(disclosures, desc="Embedding disclosures")):
            # Create unique ID
            doc_id = f"{disclosure.get('standard', 'unknown')}_{disclosure.get('disclosure_id', idx)}"
            doc_id = doc_id.replace(' ', '_').replace('/', '_')

            # Create document text for embedding
            doc_text = self._create_embedding_text(disclosure)

            # Generate embedding
            embedding = self.embedding_model.encode(doc_text, normalize_embeddings=True)

            # Prepare metadata
            metadata = {
                'standard': disclosure.get('standard', ''),
                'disclosure_id': disclosure.get('disclosure_id', ''),
                'disclosure_title': disclosure.get('disclosure_title', ''),
                'category': disclosure.get('category', ''),
                'description': disclosure.get('description', '')[:500] if disclosure.get('description') else '',
            }

            ids.append(doc_id)
            documents.append(doc_text)
            embeddings_list.append(embedding.tolist())
            metadatas.append(metadata)

        # Batch insert to ChromaDB
        try:
            self.disclosure_collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings_list,
                metadatas=metadatas
            )
            logger.info(f"Successfully added {len(ids)} disclosures to ChromaDB")
        except Exception as e:
            logger.error(f"Error adding to ChromaDB: {e}")

    def find_top_k_korean_candidates(self, disclosure_text: str, k: int = 3) -> List[tuple]:
        """
        Find top-K Korean materiality candidates using embedding similarity.
        Returns: [(korean_item, similarity_score), ...]
        """
        # Generate normalized embedding for disclosure
        query_emb = self.embedding_model.encode(disclosure_text, normalize_embeddings=True)

        # Calculate cosine similarity with all Korean items
        similarities = self._korean_embeddings @ query_emb

        # Find top-K matches
        top_k_indices = np.argsort(-similarities)[:k]
        candidates = [
            (KOREAN_MATERIALITY_ITEMS[idx], float(similarities[idx]))
            for idx in top_k_indices
        ]

        return candidates

    async def map_disclosure_to_korean(self, disclosure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Two-stage mapping: embedding-based shortlist + LLM selection.
        """
        # Create text for matching
        match_text = f"{disclosure.get('disclosure_title', '')}. {disclosure.get('description', '')}. Category: {disclosure.get('category', '')}"

        # Stage 1: Find top-K candidates using embeddings
        candidates = self.find_top_k_korean_candidates(match_text, k=3)

        # Stage 2: LLM picks the best match from candidates
        candidate_text = "\n".join([
            f"{rank}. {item} | similarity={sim:.3f}"
            for rank, (item, sim) in enumerate(candidates, start=1)
        ])

        prompt = f"""You are an ESG classification assistant.
Select the single best Korean materiality item from the provided candidate list.
Respond ONLY with valid JSON containing keys 'korean_item', 'confidence' (0-1 float), and 'reason'.
Do not reference any items outside the candidate list.

Disclosure text:
{match_text}

Korean materiality candidates:
{candidate_text}

Remember: choose ONLY from the candidate list."""

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an ESG classification assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )

            content = response.choices[0].message.content.strip()
            content = re.sub(r'^```json\s*', '', content)
            content = re.sub(r'\s*```$', '', content)

            data = json.loads(content)
            return {
                "korean_item": data.get("korean_item", candidates[0][0]),
                "confidence": float(data.get("confidence", candidates[0][1])),
                "reason": data.get("reason", ""),
                "candidates": [item for item, _ in candidates],
            }
        except Exception as e:
            logger.error(f"LLM mapping error: {e}")
            return {
                "korean_item": candidates[0][0],
                "confidence": candidates[0][1],
                "reason": "Fallback to top embedding match",
                "candidates": [item for item, _ in candidates],
            }

    def search_disclosures(
        self,
        query: str,
        n_results: int = 10,
        filter_standard: str = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant disclosures using semantic search."""
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query, normalize_embeddings=True)

        # Build where clause for filtering
        where_clause = None
        if filter_standard:
            where_clause = {"standard": {"$contains": filter_standard}}

        # Search in ChromaDB
        results = self.disclosure_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=where_clause,
            include=["documents", "metadatas", "distances"]
        )

        # Format results
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                metadata = results['metadatas'][0][i]
                # Find Korean mapping for this disclosure
                candidates = self.find_top_k_korean_candidates(
                    results['documents'][0][i], k=1
                )
                korean_item = candidates[0][0] if candidates else "Unknown"

                formatted_results.append({
                    'id': results['ids'][0][i],
                    'disclosure_id': metadata.get('disclosure_id', ''),
                    'disclosure_title': metadata.get('disclosure_title', ''),
                    'standard': metadata.get('standard', ''),
                    'category': metadata.get('category', ''),
                    'korean_issue': korean_item,
                    'similarity_score': 1 - results['distances'][0][i]
                })

        return formatted_results

    def _extract_description_from_document(self, doc_text: str) -> str:
        """Extract description from ChromaDB document text."""
        if not doc_text:
            return ""
        # Document format: "ID: xxx | Title: xxx | Category: xxx | Description: xxx | Requirements: xxx"
        desc_match = re.search(r'Description:\s*([^|]+)', doc_text)
        if desc_match:
            return desc_match.group(1).strip()
        return ""

    async def get_disclosures_for_issue(
        self,
        issue_name: str,
        standard_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get disclosure requirements mapped to a Korean materiality issue.
        Uses semantic search against all_disclosures.json embeddings.
        """
        disclosures = []

        # Use JSON-based semantic search if available
        if self._all_disclosures and self._disclosure_embeddings is not None:
            # Generate embedding for the issue
            query_embedding = self.embedding_model.encode(issue_name, normalize_embeddings=True)

            # Calculate cosine similarities with all disclosures
            similarities = self._disclosure_embeddings @ query_embedding

            # Get top matches (indices sorted by similarity descending)
            top_indices = np.argsort(-similarities)

            seen_ids = set()
            for idx in top_indices:
                if len(disclosures) >= 30:  # Limit results
                    break

                similarity = float(similarities[idx])
                if similarity < 0.35:  # Similarity threshold
                    continue

                disc = self._all_disclosures[idx]
                disc_id = disc.get('disclosure_id', '')
                standard = disc.get('standard', '')

                # Apply standard filter if provided
                if standard_filter:
                    if standard_filter.upper() not in standard.upper():
                        continue

                # Skip duplicates
                if disc_id in seen_ids:
                    continue
                seen_ids.add(disc_id)

                # Determine standard type (GRI or SASB)
                if 'GRI' in standard:
                    standard_type = 'GRI'
                elif 'SASB' in standard:
                    standard_type = 'SASB'
                else:
                    standard_type = standard

                # Get description (handle dict type for requirements field)
                description = disc.get('description', '')
                if isinstance(description, dict):
                    description = json.dumps(description, ensure_ascii=False)[:500]
                elif isinstance(description, str):
                    description = description[:500]

                disclosures.append({
                    "id": disc_id,
                    "title": disc.get('disclosure_title', ''),
                    "standard": standard_type,
                    "standard_source": standard,  # Full standard name
                    "description": description,
                    "category": disc.get('category', ''),
                    "source": "semantic_search",
                    "similarity": round(similarity, 3)
                })

        # Sort by similarity (highest first)
        disclosures.sort(key=lambda x: -x.get('similarity', 0))

        return {
            "issue": issue_name,
            "category": ESG_CATEGORY_MAP.get(issue_name, "Unknown"),
            "disclosures": disclosures[:20],  # Limit to top 20
            "total_count": len(disclosures)
        }

    async def get_all_issues_with_disclosures(self) -> List[Dict[str, Any]]:
        """
        Get all Korean materiality issues with their mapped disclosures.
        """
        results = []

        for issue in KOREAN_MATERIALITY_ITEMS:
            issue_data = await self.get_disclosures_for_issue(issue)

            gri_count = len([d for d in issue_data['disclosures'] if d['standard'] == 'GRI'])
            sasb_count = len([d for d in issue_data['disclosures'] if d['standard'] == 'SASB'])

            results.append({
                "issue": issue,
                "category": ESG_CATEGORY_MAP.get(issue, "Unknown"),
                "disclosures": issue_data['disclosures'],
                "disclosure_count": len(issue_data['disclosures']),
                "gri_count": gri_count,
                "sasb_count": sasb_count,
            })

        return results

    async def analyze_issue_with_ai(self, issue_name: str) -> Dict[str, Any]:
        """
        Use AI to generate detailed analysis for an ESG issue.
        """
        issue_data = await self.get_disclosures_for_issue(issue_name)
        disclosures = issue_data['disclosures']

        if not disclosures:
            return {
                "issue": issue_name,
                "category": ESG_CATEGORY_MAP.get(issue_name, "Unknown"),
                "disclosures": [],
                "analysis": {
                    "summary": "해당 이슈에 대한 공시 요구사항이 없습니다.",
                    "key_disclosures": [],
                    "recommendations": []
                }
            }

        disclosure_text = "\n".join([
            f"- {d['id']}: {d['title']} ({d['standard']})"
            for d in disclosures[:10]  # Limit to top 10
        ])

        prompt = f"""다음 ESG 이슈에 대한 GRI/SASB 공시 요구사항을 분석하세요:

이슈: {issue_name}

관련 공시 요구사항:
{disclosure_text}

다음 형식으로 분석 결과를 제공하세요:
1. 이슈 요약 (2-3문장)
2. 핵심 공시 요구사항 (주요 3가지)
3. 기업 대응 권고사항 (3가지)

JSON 형식으로 응답하세요:
{{"summary": "...", "key_disclosures": ["...", "...", "..."], "recommendations": ["...", "...", "..."]}}
"""

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an ESG reporting expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            content = response.choices[0].message.content.strip()
            content = re.sub(r'^```json\s*', '', content)
            content = re.sub(r'^```\s*', '', content)
            content = re.sub(r'\s*```$', '', content)

            analysis = json.loads(content)

            return {
                "issue": issue_name,
                "category": ESG_CATEGORY_MAP.get(issue_name, "Unknown"),
                "disclosures": disclosures,
                "analysis": analysis
            }

        except Exception as e:
            logger.error(f"AI analysis error for {issue_name}: {e}")
            return {
                "issue": issue_name,
                "category": ESG_CATEGORY_MAP.get(issue_name, "Unknown"),
                "disclosures": disclosures,
                "analysis": {
                    "summary": f"{issue_name}에 대한 {len(disclosures)}개의 공시 요구사항이 있습니다.",
                    "key_disclosures": [d["title"] for d in disclosures[:3]],
                    "recommendations": ["관련 지표 측정 체계 구축", "정기적 모니터링 실시", "이해관계자 소통 강화"]
                }
            }

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored disclosures."""
        all_docs = self.disclosure_collection.get(include=["metadatas"])

        standard_counts = {}
        category_counts = {}

        if all_docs['ids']:
            for metadata in all_docs['metadatas']:
                standard = metadata.get('standard', 'Unknown')
                category = metadata.get('category', 'Unknown')

                # Simplify standard name
                if 'GRI' in standard:
                    standard = 'GRI'
                elif 'SASB' in standard:
                    standard = 'SASB'

                standard_counts[standard] = standard_counts.get(standard, 0) + 1
                category_counts[category] = category_counts.get(category, 0) + 1

        return {
            "total_issues": len(KOREAN_MATERIALITY_ITEMS),
            "total_disclosures": len(all_docs['ids']) if all_docs['ids'] else 0,
            "gri_disclosures": standard_counts.get('GRI', 0),
            "sasb_disclosures": standard_counts.get('SASB', 0),
            "by_category": category_counts
        }

    def reset_database(self):
        """Clear all data from the database."""
        self.chroma_client.delete_collection(name="esg_disclosures")
        self.disclosure_collection = self.chroma_client.get_or_create_collection(
            name="esg_disclosures",
            metadata={"description": "GRI and SASB disclosure requirements"}
        )
        logger.info("Database reset complete")

    def get_collection_count(self) -> int:
        """Get the number of documents in the collection."""
        return self.disclosure_collection.count()


# Singleton instance
_service_instance: Optional[ESGStandardsService] = None


def get_esg_standards_service() -> ESGStandardsService:
    """Get singleton instance of ESGStandardsService."""
    global _service_instance
    if _service_instance is None:
        _service_instance = ESGStandardsService()
    return _service_instance
