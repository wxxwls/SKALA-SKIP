"""Chatbot API endpoints."""
from fastapi import APIRouter, Depends

from app.schemas.chatbot_schemas import (
    ChatRequest,
    ChatResponse,
    ChatHistoryRequest,
    ChatHistoryResponse,
)
from app.services.chatbot_service import ChatbotService

router = APIRouter()


def get_chatbot_service() -> ChatbotService:
    """Dependency injection for ChatbotService."""
    return ChatbotService()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: ChatbotService = Depends(get_chatbot_service),
) -> ChatResponse:
    """Process a chat message using RAG."""
    return await service.process_chat(request)


@router.post("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    request: ChatHistoryRequest,
    service: ChatbotService = Depends(get_chatbot_service),
) -> ChatHistoryResponse:
    """Retrieve chat history for a session."""
    return await service.get_history(request)
