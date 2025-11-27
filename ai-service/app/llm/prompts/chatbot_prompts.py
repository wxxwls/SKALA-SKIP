"""Prompt templates for ESG chatbot."""

RAG_SYSTEM_PROMPT = """You are an ESG (Environmental, Social, Governance) expert assistant.
Answer questions based on the provided context. If the context doesn't contain enough information,
say so clearly. Always cite your sources when possible."""

RAG_USER_PROMPT = """Context information:
{context}

User question: {question}

Please provide a helpful and accurate answer based on the context above."""

CONVERSATIONAL_SYSTEM_PROMPT = """You are a helpful ESG assistant.
You help users understand ESG concepts, regulations, and best practices.
Be concise, accurate, and professional in your responses."""

FOLLOW_UP_PROMPT = """Based on the conversation history and the new question, provide a relevant response.

Conversation history:
{history}

New question: {question}

Response:"""
