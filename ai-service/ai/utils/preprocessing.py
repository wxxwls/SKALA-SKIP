"""Text preprocessing utilities."""
import re
from typing import List


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text: str) -> List[str]:
    """Simple whitespace tokenization."""
    return text.split()


def remove_stopwords(tokens: List[str], stopwords: set) -> List[str]:
    """Remove stopwords from tokens."""
    return [t for t in tokens if t.lower() not in stopwords]


def truncate_text(text: str, max_length: int = 512) -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."
