"""Sentiment analysis service."""
from typing import List, Dict

from ai.models.sentiment import SentimentModel
from app.core.logging import get_logger

logger = get_logger(__name__)


class SentimentService:
    """Service for sentiment analysis operations."""

    def __init__(self) -> None:
        self._model = SentimentModel()

    def analyze_text(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of a single text."""
        label, score = self._model.analyze(text)
        return {"label": label, "score": score}

    def analyze_texts(self, texts: List[str]) -> List[Dict[str, float]]:
        """Analyze sentiment of multiple texts."""
        logger.info(f"Analyzing sentiment for {len(texts)} texts")
        results = self._model.analyze_batch(texts)
        return [{"label": label, "score": score} for label, score in results]
