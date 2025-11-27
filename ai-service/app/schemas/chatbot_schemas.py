"""Chatbot related Pydantic schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Single chat message."""

    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RetrievedDocument(BaseModel):
    """Retrieved document from RAG."""

    content: str = Field(..., description="Document content")
    source: str = Field(..., description="Document source")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    metadata: dict = Field(default_factory=dict)


class ChatRequest(BaseModel):
    """Request schema for chat."""

    session_id: str = Field(..., description="Chat session ID")
    message: str = Field(..., description="User message")
    history: List[ChatMessage] = Field(default_factory=list, description="Chat history")
    use_rag: bool = Field(default=True, description="Whether to use RAG")
    max_tokens: int = Field(default=1024, description="Maximum response tokens")


class ChatResponse(BaseModel):
    """Response schema for chat."""

    session_id: str = Field(..., description="Chat session ID")
    response: str = Field(..., description="Assistant response")
    retrieved_documents: List[RetrievedDocument] = Field(
        default_factory=list, description="Retrieved documents used for response"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatHistoryRequest(BaseModel):
    """Request schema for chat history."""

    session_id: str = Field(..., description="Chat session ID")
    limit: int = Field(default=50, ge=1, le=200, description="Maximum messages to retrieve")


class ChatHistoryResponse(BaseModel):
    """Response schema for chat history."""

    session_id: str = Field(..., description="Chat session ID")
    messages: List[ChatMessage] = Field(default_factory=list, description="Chat messages")
    total_count: int = Field(..., description="Total message count")
