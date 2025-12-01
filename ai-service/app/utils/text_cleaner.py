"""Text cleaning utilities."""
import re
from typing import List


def clean_html(text: str) -> str:
    """Remove HTML tags from text."""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    return " ".join(text.split())


def clean_text(
    text: str,
    remove_html: bool = True,
    normalize_ws: bool = True,
) -> str:
    """Clean text with various options."""
    result = text
    if remove_html:
        result = clean_html(result)
    if normalize_ws:
        result = normalize_whitespace(result)
    return result.strip()


def clean_texts(
    texts: List[str],
    remove_html: bool = True,
    normalize_ws: bool = True,
) -> List[str]:
    """Clean multiple texts."""
    return [clean_text(t, remove_html, normalize_ws) for t in texts]
