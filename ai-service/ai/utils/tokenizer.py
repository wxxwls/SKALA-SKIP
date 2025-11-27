"""Tokenization utilities."""
from typing import List, Optional

import tiktoken


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens in text for a given model."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def truncate_to_tokens(
    text: str,
    max_tokens: int,
    model: str = "gpt-4",
) -> str:
    """Truncate text to fit within token limit."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    tokens = encoding.encode(text)
    if len(tokens) <= max_tokens:
        return text
    return encoding.decode(tokens[:max_tokens])


def split_into_chunks(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
    model: str = "gpt-4",
) -> List[str]:
    """Split text into token-based chunks with overlap."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    tokens = encoding.encode(text)
    chunks = []
    start = 0

    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(encoding.decode(chunk_tokens))
        start = end - overlap if end < len(tokens) else end

    return chunks
