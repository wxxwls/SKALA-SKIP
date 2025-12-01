"""OpenAI API client."""
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import LLMException

logger = get_logger(__name__)

# Prompt templates directory
PROMPTS_DIR = Path(__file__).parent.parent / "prompts" / "report"


class OpenAIClient:
    """Client for OpenAI API calls."""

    def __init__(self) -> None:
        self._client: Optional[AsyncOpenAI] = None

    def _get_client(self) -> AsyncOpenAI:
        """Get or create OpenAI client."""
        if self._client is None:
            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    async def chat_completion(
        self,
        messages: List[dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Generate chat completion."""
        try:
            client = self._get_client()
            response = await client.chat.completions.create(
                model=model or settings.OPENAI_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI chat completion failed: {e}")
            raise LLMException(
                message="Failed to generate chat completion",
                details={"error": str(e)},
            )

    async def generate_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-3-small",
    ) -> List[List[float]]:
        """Generate embeddings for texts."""
        try:
            client = self._get_client()
            response = await client.embeddings.create(
                model=model,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"OpenAI embedding generation failed: {e}")
            raise LLMException(
                message="Failed to generate embeddings",
                details={"error": str(e)},
            )

    def _format_kpi_data(self, kpi_data: List[Dict[str, Any]]) -> str:
        """Format KPI data for prompt."""
        if not kpi_data:
            return "제공된 KPI 데이터 없음"

        lines = []
        for kpi in kpi_data:
            name = kpi.get("kpi_name") or kpi.get("name", "")
            value = kpi.get("kpi_value") or kpi.get("value", "")
            unit = kpi.get("unit", "")
            is_null = kpi.get("is_null", False)

            if is_null or not value:
                lines.append(f"- {name}: ※ 내부 데이터 미등록 ({unit})")
            else:
                lines.append(f"- {name}: {value} {unit}")

        return "\n".join(lines) if lines else "제공된 KPI 데이터 없음"

    def _extract_html(self, text: str) -> str:
        """Extract HTML content from response."""
        # Try to extract HTML from code blocks
        html_match = re.search(r"```html\s*([\s\S]*?)\s*```", text)
        if html_match:
            html_content = html_match.group(1).strip()
        elif "<section" in text or "<div" in text:
            html_content = text.strip()
        else:
            html_content = text.strip()

        # Remove duplicate h3 title from OpenAI response (we add our own title in wrapper)
        # Pattern: <h3 class="issue-title">...</h3>
        html_content = re.sub(r'<h3[^>]*class="issue-title"[^>]*>[\s\S]*?</h3>\s*', '', html_content)

        # Also remove any standalone h3 at the beginning
        html_content = re.sub(r'^[\s\n]*<h3[^>]*>[\s\S]*?</h3>\s*', '', html_content)

        return html_content.strip()

    async def generate_impact_section(
        self,
        company_name: str,
        industry: str,
        year: int,
        issue_id: str,
        issue_name: str,
        category: str,
        impact_score: float,
        kpi_data: List[Dict[str, Any]],
        priority_rank: int,
    ) -> str:
        """Generate impact materiality section HTML."""
        try:
            # Load prompt template
            prompt_path = PROMPTS_DIR / "impact_section.txt"
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()

            # Format KPI data
            kpi_text = self._format_kpi_data(kpi_data)

            # Fill template
            prompt = prompt_template.format(
                company_name=company_name,
                industry=industry,
                year=year,
                issue_id=issue_id,
                issue_name=issue_name,
                category=category,
                impact_score=impact_score,
                priority_rank=priority_rank,
                kpi_data=kpi_text,
            )

            # Parse system and user messages
            messages = [
                {"role": "user", "content": prompt}
            ]

            logger.info(f"Generating impact section for: {issue_name}")

            response = await self.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=2048,
            )

            return self._extract_html(response)

        except Exception as e:
            logger.error(f"Failed to generate impact section: {e}")
            raise LLMException(
                message="영향 중대성 섹션 생성 실패",
                details={"error": str(e)},
            )

    async def generate_financial_section(
        self,
        company_name: str,
        industry: str,
        year: int,
        issue_id: str,
        issue_name: str,
        category: str,
        financial_score: float,
        kpi_data: List[Dict[str, Any]],
        priority_rank: int,
    ) -> str:
        """Generate financial materiality section HTML."""
        try:
            # Load prompt template
            prompt_path = PROMPTS_DIR / "financial_section.txt"
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()

            # Format KPI data
            kpi_text = self._format_kpi_data(kpi_data)

            # Fill template
            prompt = prompt_template.format(
                company_name=company_name,
                industry=industry,
                year=year,
                issue_id=issue_id,
                issue_name=issue_name,
                category=category,
                financial_score=financial_score,
                priority_rank=priority_rank,
                kpi_data=kpi_text,
            )

            messages = [
                {"role": "user", "content": prompt}
            ]

            logger.info(f"Generating financial section for: {issue_name}")

            response = await self.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=2048,
            )

            return self._extract_html(response)

        except Exception as e:
            logger.error(f"Failed to generate financial section: {e}")
            raise LLMException(
                message="재무 중대성 섹션 생성 실패",
                details={"error": str(e)},
            )

    async def modify_report(
        self,
        current_report: str,
        instruction: str,
    ) -> str:
        """Modify report based on user instruction."""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """당신은 ESG 보고서 수정 전문가입니다.
사용자의 지시에 따라 보고서를 수정하세요.
- 지시된 부분만 수정
- 기존 형식 유지
- 한국어로 작성
- 마크다운 형식 유지"""
                },
                {
                    "role": "user",
                    "content": f"""현재 보고서:
{current_report}

수정 지시:
{instruction}

위 지시에 따라 보고서를 수정해주세요."""
                }
            ]

            logger.info(f"Modifying report with instruction: {instruction[:50]}...")

            response = await self.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=4096,
            )

            return response

        except Exception as e:
            logger.error(f"Failed to modify report: {e}")
            raise LLMException(
                message="보고서 수정 실패",
                details={"error": str(e)},
            )


# Singleton instance
_openai_client: Optional[OpenAIClient] = None


def get_openai_client() -> OpenAIClient:
    """Get or create OpenAIClient singleton."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client
