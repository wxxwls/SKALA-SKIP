"""
ESG Media Analysis Service

뉴스 기사를 수집하고, ESG 이슈로 분류하고, 감정 분석을 수행
"""

import re
import urllib.request
import urllib.parse
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter

from app.config.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# ESG Issue Keywords Mapping
ESG_ISSUE_KEYWORDS = {
    "기후변화 대응": [
        "기후변화", "탄소중립", "탄소배출", "온실가스", "RE100", "넷제로",
        "탄소감축", "기후위기", "탄소", "배출권", "GHG", "온실", "기후"
    ],
    "신재생에너지 확대 및 전력 효율화": [
        "신재생에너지", "태양광", "풍력", "수소", "재생에너지", "전력효율",
        "에너지효율", "그린에너지", "에너지", "전력", "발전", "ESS", "배터리"
    ],
    "환경영향 관리": [
        "환경영향", "환경평가", "오염", "배출관리", "폐기물", "수질", "대기질",
        "환경보호", "환경", "재활용", "순환경제", "미세먼지", "플라스틱"
    ],
    "생물다양성 보호": [
        "생물다양성", "생태계", "자연자본", "서식지", "멸종위기",
        "생태보전", "생태", "자연"
    ],
    "친환경 사업/기술 투자": [
        "친환경", "녹색기술", "그린테크", "친환경투자", "지속가능", "환경기술",
        "ESG투자", "ESG", "지속가능성", "그린뉴딜", "저탄소", "녹색",
        "신사업", "미래사업", "신성장", "신규사업", "사업다각화",
        "기술개발", "기술혁신", "R&D", "연구개발", "첨단기술", "혁신",
        "디지털전환", "DX", "디지털혁신",
        "생성AI", "GenAI", "GPT", "LLM", "클라우드", "빅데이터",
        "전기차", "EV", "자율주행", "스마트시티", "스마트팩토리"
    ],
    "인재양성 및 다양성": [
        "인재양성", "인재", "다양성", "포용", "교육", "역량개발", "인력개발",
        "여성인력", "DEI", "채용", "직원", "임직원", "여성", "양성평등", "육성", "인력"
    ],
    "인권경영 고도화": [
        "인권", "인권경영", "강제노동", "아동노동", "차별금지",
        "인권실사", "노동권", "노동", "차별"
    ],
    "안전보건 관리": [
        "안전", "보건", "산업재해", "안전사고", "작업환경", "산업안전",
        "안전보건", "재해예방", "사고", "재해", "건강"
    ],
    "공급망 ESG 관리": [
        "공급망", "협력사", "협력업체", "납품업체", "공급업체", "벤더",
        "하도급", "밸류체인", "가치사슬", "협력", "파트너"
    ],
    "책임있는 제품/서비스 관리": [
        "품질", "제품안전", "소비자보호", "리콜", "고객만족", "서비스품질",
        "제품책임", "제품", "서비스", "고객", "소비자"
    ],
    "정보보안 및 프라이버시": [
        "정보보안", "개인정보", "프라이버시", "사이버보안", "데이터보호",
        "보안사고", "해킹", "정보유출", "보안", "데이터", "AI", "인공지능", "디지털"
    ],
    "지역사회 공헌": [
        "사회공헌", "기부", "봉사", "지역사회", "상생", "나눔", "후원",
        "지역발전", "사회적가치", "공헌", "사회", "복지"
    ],
    "포트폴리오 ESG 관리": [
        "포트폴리오", "ESG평가", "투자심사", "자산운용", "투자", "펀드", "자산"
    ],
    "투명한 이사회 경영": [
        "이사회", "사외이사", "지배구조", "경영투명성", "이사회구성",
        "독립성", "거버넌스", "경영진", "의사결정"
    ],
    "윤리 및 컴플라이언스": [
        "윤리", "컴플라이언스", "준법", "반부패", "청렴", "내부통제",
        "행동강령", "부패방지", "부패", "규제", "법규"
    ],
    "주주가치 제고": [
        "주주", "배당", "주가", "자사주", "주주환원", "주주총회",
        "의결권", "주식", "주주권", "환원", "총회"
    ],
    "리스크 관리": [
        "리스크", "위험관리", "위기관리", "재무리스크", "운영리스크",
        "통합리스크", "위험", "위기", "대응"
    ],
    "ESG 공시 의무화 대응": [
        "ESG공시", "지속가능보고서", "통합보고서", "ESG보고", "공시의무",
        "TCFD", "ISSB", "공시", "보고서", "공개"
    ]
}

# ESG Category Mapping
ESG_CATEGORY_MAP = {
    "기후변화 대응": "E",
    "신재생에너지 확대 및 전력 효율화": "E",
    "환경영향 관리": "E",
    "생물다양성 보호": "E",
    "친환경 사업/기술 투자": "E",
    "인재양성 및 다양성": "S",
    "인권경영 고도화": "S",
    "안전보건 관리": "S",
    "공급망 ESG 관리": "S",
    "책임있는 제품/서비스 관리": "S",
    "정보보안 및 프라이버시": "S",
    "지역사회 공헌": "S",
    "포트폴리오 ESG 관리": "S",
    "투명한 이사회 경영": "G",
    "윤리 및 컴플라이언스": "G",
    "주주가치 제고": "G",
    "리스크 관리": "G",
    "ESG 공시 의무화 대응": "G"
}

# Sentiment Keywords
POSITIVE_KEYWORDS = {
    # 성과/성장
    "성공", "성장", "증가", "향상", "개선", "발전", "확대", "강화", "상승",
    "호조", "호황", "활성화", "활발", "도약", "혁신", "선도", "우수",
    # 긍정 평가
    "우수", "탁월", "뛰어난", "훌륭", "좋은", "긍정적", "효과적",
    "성과", "달성", "수상", "인정", "평가", "선정",
    # ESG 긍정
    "친환경", "지속가능", "탄소중립", "녹색", "청정", "재생에너지",
    "투명", "윤리", "공헌", "상생", "다양성", "포용",
    # 기회/전망
    "기회", "전망", "기대", "희망", "가능성", "잠재력",
    # 투자/수익
    "투자", "수익", "이익", "배당", "가치", "성장성"
}

NEGATIVE_KEYWORDS = {
    # 문제/위기
    "문제", "위기", "위험", "우려", "논란", "비판", "반발", "갈등",
    "사고", "재해", "피해", "손실", "손해", "적자", "부진", "악화",
    # 부정 행위
    "부패", "비리", "횡령", "배임", "뇌물", "사기", "위반", "불법",
    "위법", "탈세", "회계부정", "분식",
    # ESG 리스크
    "오염", "배출", "누출", "파괴", "훼손", "차별", "인권침해",
    "강제노동", "아동노동", "안전사고", "중대재해",
    # 감소/하락
    "감소", "하락", "감축", "축소", "폐쇄", "중단", "철수", "포기",
    "취소", "연기", "지연",
    # 부정 평가
    "부정적", "실패", "좌절", "미흡", "부족", "불충분", "불만",
    "경고", "제재", "처벌", "과징금", "벌금"
}


class NaverNewsCollector:
    """Naver News Search API Collector."""

    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize collector.

        Args:
            client_id: Naver API Client ID
            client_secret: Naver API Client Secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://openapi.naver.com/v1/search/news.json"

    def search_news(
        self,
        keyword: str,
        display: int = 100,
        start: int = 1,
        sort: str = "date"
    ) -> Dict[str, Any]:
        """
        Search news via Naver API.

        Args:
            keyword: Search keyword
            display: Number of results per page (max 100)
            start: Start index
            sort: Sort method ('sim' for similarity, 'date' for date)

        Returns:
            API response as dictionary
        """
        enc_keyword = urllib.parse.quote(keyword)
        url = f"{self.base_url}?query={enc_keyword}&start={start}&display={display}&sort={sort}"

        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.client_id)
        request.add_header("X-Naver-Client-Secret", self.client_secret)

        try:
            response = urllib.request.urlopen(request)
            if response.getcode() == 200:
                response_body = response.read()
                return json.loads(response_body.decode("utf-8"))
            else:
                logger.error(f"Naver API Error Code: {response.getcode()}")
                return {"items": []}
        except Exception as e:
            logger.error(f"Naver API call error: {e}")
            return {"items": []}

    def collect_news(
        self,
        keywords: List[str],
        max_pages: int = 10,
        sort_types: List[str] = None,
        delay: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Collect news for multiple keywords.

        Args:
            keywords: List of search keywords
            max_pages: Max pages per keyword (max 10)
            sort_types: Sort methods to use
            delay: Delay between API calls (seconds)

        Returns:
            List of news items
        """
        if sort_types is None:
            sort_types = ["sim", "date"]

        all_items = []
        display_count = 100

        logger.info(f"Collecting news for {len(keywords)} keywords")

        for keyword in keywords:
            for sort_type in sort_types:
                for page in range(1, max_pages + 1):
                    start_index = (page - 1) * display_count + 1
                    result = self.search_news(
                        keyword=keyword,
                        display=display_count,
                        start=start_index,
                        sort=sort_type
                    )

                    if not result.get("items"):
                        break

                    all_items.extend(result["items"])
                    time.sleep(delay)

        logger.info(f"Collected {len(all_items)} news items")
        return all_items


class ESGIssueClassifier:
    """ESG Issue Classifier for news articles."""

    def __init__(self):
        """Initialize classifier with ESG issue mappings."""
        self.esg_issues = ESG_ISSUE_KEYWORDS
        self.category_map = ESG_CATEGORY_MAP

    def classify_article(self, text: str, title: str = "") -> List[str]:
        """
        Classify article into ESG issues.

        Args:
            text: Article body
            title: Article title

        Returns:
            List of matched ESG issues
        """
        if not text:
            text = ""
        if not title:
            title = ""

        # Remove HTML tags
        text = re.sub("<[^<]+?>", "", str(text))
        title = re.sub("<[^<]+?>", "", str(title))

        full_text = (title + " " + text).lower()

        matched_issues = []
        for issue, keywords in self.esg_issues.items():
            for keyword in keywords:
                if keyword.lower() in full_text:
                    matched_issues.append(issue)
                    break

        return matched_issues if matched_issues else ["기타"]

    def get_esg_category(self, issue: str) -> str:
        """Get ESG category (E/S/G) for an issue."""
        return self.category_map.get(issue, "ETC")


class SentimentAnalyzer:
    """Sentiment Analyzer for Korean news articles."""

    def __init__(self):
        """Initialize with sentiment keywords."""
        self.positive_keywords = POSITIVE_KEYWORDS
        self.negative_keywords = NEGATIVE_KEYWORDS

    def analyze_sentiment(self, text: str) -> Tuple[str, float, Dict[str, int]]:
        """
        Analyze text sentiment.

        Args:
            text: Text to analyze

        Returns:
            Tuple of (sentiment_label, sentiment_score, details)
        """
        if not text:
            return "중립", 0.0, {"positive_count": 0, "negative_count": 0}

        # Remove HTML tags
        text = re.sub("<[^<]+?>", "", str(text))
        text = text.lower()

        # Count keywords
        positive_count = sum(1 for keyword in self.positive_keywords if keyword in text)
        negative_count = sum(1 for keyword in self.negative_keywords if keyword in text)

        # Calculate sentiment score (-1.0 to 1.0)
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            sentiment_score = 0.0
            sentiment_label = "중립"
        else:
            sentiment_score = (positive_count - negative_count) / total_sentiment_words

            if sentiment_score > 0.2:
                sentiment_label = "긍정"
            elif sentiment_score < -0.2:
                sentiment_label = "부정"
            else:
                sentiment_label = "중립"

        return sentiment_label, round(sentiment_score, 3), {
            "positive_count": positive_count,
            "negative_count": negative_count
        }


class MediaAnalysisService:
    """ESG Media Analysis Service."""

    def __init__(
        self,
        naver_client_id: Optional[str] = None,
        naver_client_secret: Optional[str] = None
    ):
        """
        Initialize Media Analysis Service.

        Args:
            naver_client_id: Naver API Client ID
            naver_client_secret: Naver API Client Secret
        """
        self.client_id = naver_client_id or getattr(settings, "NAVER_CLIENT_ID", "")
        self.client_secret = naver_client_secret or getattr(settings, "NAVER_CLIENT_SECRET", "")

        self.classifier = ESGIssueClassifier()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.news_collector = None

        if self.client_id and self.client_secret:
            self.news_collector = NaverNewsCollector(self.client_id, self.client_secret)

        logger.info("MediaAnalysisService initialized")

    def process_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single news article.

        Args:
            article: Raw article data

        Returns:
            Processed article with ESG classification and sentiment
        """
        # Clean title and description
        clean_title = re.sub("<[^<]+?>", "", str(article.get("title", "")))
        clean_description = re.sub("<[^<]+?>", "", str(article.get("description", "")))

        # Full text for analysis
        full_content = clean_title + " " + clean_description

        # ESG classification
        esg_issues = self.classifier.classify_article(full_content, clean_title)
        esg_categories = list(set(
            self.classifier.get_esg_category(issue)
            for issue in esg_issues
            if issue != "기타"
        ))

        # Sentiment analysis
        sentiment_label, sentiment_score, sentiment_details = (
            self.sentiment_analyzer.analyze_sentiment(full_content)
        )

        return {
            "title": article.get("title", ""),
            "clean_title": clean_title,
            "description": article.get("description", ""),
            "clean_description": clean_description,
            "link": article.get("link", ""),
            "originallink": article.get("originallink", ""),
            "pubDate": article.get("pubDate", ""),
            "esg_issues": esg_issues,
            "esg_categories": esg_categories,
            "sentiment": sentiment_label,
            "sentiment_score": sentiment_score,
            "positive_count": sentiment_details["positive_count"],
            "negative_count": sentiment_details["negative_count"],
        }

    async def collect_and_analyze_news(
        self,
        keywords: List[str],
        max_pages: int = 5
    ) -> Dict[str, Any]:
        """
        Collect and analyze news for given keywords.

        Args:
            keywords: Search keywords
            max_pages: Max pages per keyword

        Returns:
            Analysis results
        """
        if not self.news_collector:
            logger.error("News collector not initialized - missing API credentials")
            return {"error": "Naver API credentials not configured"}

        # Collect news
        raw_articles = self.news_collector.collect_news(
            keywords=keywords,
            max_pages=max_pages
        )

        # Process articles
        processed_articles = []
        for article in raw_articles:
            try:
                processed = self.process_article(article)
                processed_articles.append(processed)
            except Exception as e:
                logger.error(f"Error processing article: {e}")
                continue

        # Remove duplicates by link
        seen_links = set()
        unique_articles = []
        for article in processed_articles:
            link = article.get("link", "")
            if link not in seen_links:
                seen_links.add(link)
                unique_articles.append(article)

        return {
            "total_collected": len(raw_articles),
            "unique_articles": len(unique_articles),
            "articles": unique_articles,
            "statistics": self.generate_statistics(unique_articles)
        }

    def analyze_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze pre-collected articles.

        Args:
            articles: List of raw article data

        Returns:
            Analysis results
        """
        processed_articles = []
        for article in articles:
            try:
                processed = self.process_article(article)
                processed_articles.append(processed)
            except Exception as e:
                logger.error(f"Error processing article: {e}")
                continue

        return {
            "total_articles": len(processed_articles),
            "articles": processed_articles,
            "statistics": self.generate_statistics(processed_articles)
        }

    def generate_statistics(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate statistics from analyzed articles.

        Args:
            articles: List of processed articles

        Returns:
            Statistics dictionary
        """
        if not articles:
            return {}

        # ESG Issue statistics
        issue_counts: Dict[str, int] = {}
        for article in articles:
            for issue in article.get("esg_issues", []):
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

        issue_stats = []
        for issue in list(ESG_ISSUE_KEYWORDS.keys()) + ["기타"]:
            count = issue_counts.get(issue, 0)
            issue_stats.append({
                "issue": issue,
                "count": count,
                "percentage": round(count / len(articles) * 100, 2) if articles else 0,
                "esg_category": ESG_CATEGORY_MAP.get(issue, "ETC")
            })

        # Sort by count
        issue_stats.sort(key=lambda x: x["count"], reverse=True)

        # Sentiment statistics
        sentiment_counts = Counter(
            article.get("sentiment", "중립") for article in articles
        )

        # ESG Category statistics
        category_counts: Dict[str, int] = {"E": 0, "S": 0, "G": 0, "ETC": 0}
        for article in articles:
            for cat in article.get("esg_categories", []):
                if cat in category_counts:
                    category_counts[cat] += 1

        return {
            "issue_statistics": issue_stats,
            "sentiment_statistics": {
                "긍정": sentiment_counts.get("긍정", 0),
                "부정": sentiment_counts.get("부정", 0),
                "중립": sentiment_counts.get("중립", 0),
                "avg_score": round(
                    sum(a.get("sentiment_score", 0) for a in articles) / len(articles), 3
                ) if articles else 0
            },
            "category_statistics": category_counts
        }

    def search_by_keyword(
        self,
        articles: List[Dict[str, Any]],
        keyword: str
    ) -> List[Dict[str, Any]]:
        """
        Search articles by keyword.

        Args:
            articles: List of processed articles
            keyword: Search keyword

        Returns:
            Filtered articles
        """
        keyword_lower = keyword.lower()
        results = []

        for article in articles:
            title = article.get("clean_title", "").lower()
            description = article.get("clean_description", "").lower()

            if keyword_lower in title or keyword_lower in description:
                results.append(article)

        return results

    def get_articles_by_issue(
        self,
        articles: List[Dict[str, Any]],
        issue: str
    ) -> List[Dict[str, Any]]:
        """
        Get articles for a specific ESG issue.

        Args:
            articles: List of processed articles
            issue: ESG issue name

        Returns:
            Filtered articles
        """
        return [
            article for article in articles
            if issue in article.get("esg_issues", [])
        ]

    async def get_stored_media_data(self) -> Dict[str, Any]:
        """
        Get stored/cached media data.

        For now, this fetches news with default keywords.
        In the future, this could return data from a database.

        Returns:
            Analysis results with articles and statistics
        """
        # Default keywords for automatic news collection
        default_keywords = ["SK ESG", "SK 지속가능"]

        logger.info(f"Fetching media data with default keywords: {default_keywords}")

        # Use existing collect_and_analyze_news method
        return await self.collect_and_analyze_news(
            keywords=default_keywords,
            max_pages=3
        )


# Singleton instance
_media_analysis_service: Optional[MediaAnalysisService] = None


def get_media_analysis_service() -> MediaAnalysisService:
    """Get or create MediaAnalysisService singleton."""
    global _media_analysis_service
    if _media_analysis_service is None:
        _media_analysis_service = MediaAnalysisService()
    return _media_analysis_service
