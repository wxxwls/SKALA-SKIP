"""Report generation chain using LangChain."""
from typing import Dict, Optional

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.config import settings
from app.core.logging import get_logger
from app.llm.prompts.report_prompts import (
    REPORT_SECTION_SYSTEM_PROMPT,
    REPORT_SECTION_USER_PROMPT,
)

logger = get_logger(__name__)


class ReportChain:
    """Chain for ESG report section generation."""

    def __init__(self) -> None:
        self._llm: Optional[ChatOpenAI] = None

    def _get_llm(self) -> ChatOpenAI:
        """Get or create LLM instance."""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.5,
            )
        return self._llm

    async def generate_section(
        self,
        section_type: str,
        context: str,
        max_length: int = 1000,
    ) -> str:
        """Generate a report section."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", REPORT_SECTION_SYSTEM_PROMPT),
            ("user", REPORT_SECTION_USER_PROMPT),
        ])

        chain = prompt | self._get_llm() | StrOutputParser()

        result = await chain.ainvoke({
            "section_type": section_type,
            "context": context,
            "max_length": max_length,
        })

        return result

    async def generate_multiple_sections(
        self,
        sections: Dict[str, str],
        max_length: int = 1000,
    ) -> Dict[str, str]:
        """Generate multiple report sections."""
        results = {}
        for section_type, context in sections.items():
            results[section_type] = await self.generate_section(
                section_type=section_type,
                context=context,
                max_length=max_length,
            )
        return results
