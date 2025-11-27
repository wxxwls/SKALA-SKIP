"""RAG chain implementation using LangChain."""
from typing import List, Optional

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.core.config import settings
from app.core.logging import get_logger
from app.llm.prompts.chatbot_prompts import RAG_SYSTEM_PROMPT, RAG_USER_PROMPT

logger = get_logger(__name__)


class RAGChain:
    """RAG chain for question answering with retrieval."""

    def __init__(self) -> None:
        self._llm: Optional[ChatOpenAI] = None
        self._embeddings: Optional[OpenAIEmbeddings] = None

    def _get_llm(self) -> ChatOpenAI:
        """Get or create LLM instance."""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.7,
            )
        return self._llm

    def _get_embeddings(self) -> OpenAIEmbeddings:
        """Get or create embeddings instance."""
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(
                api_key=settings.OPENAI_API_KEY,
            )
        return self._embeddings

    async def run(
        self,
        question: str,
        context_documents: List[str],
    ) -> str:
        """Run RAG chain with provided context."""
        context = "\n\n".join(context_documents)

        prompt = ChatPromptTemplate.from_messages([
            ("system", RAG_SYSTEM_PROMPT),
            ("user", RAG_USER_PROMPT),
        ])

        chain = (
            {"context": lambda _: context, "question": RunnablePassthrough()}
            | prompt
            | self._get_llm()
            | StrOutputParser()
        )

        result = await chain.ainvoke(question)
        return result

    async def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a query."""
        embeddings = self._get_embeddings()
        return await embeddings.aembed_query(query)

    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Generate embeddings for documents."""
        embeddings = self._get_embeddings()
        return await embeddings.aembed_documents(documents)
