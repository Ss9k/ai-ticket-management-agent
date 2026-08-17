"""
Embedding generator using SentenceTransformers.
Same model used for both document ingestion and query embedding.
"""
import logging
import numpy as np
from typing import Union

from backend.core.config import get_settings

logger = logging.getLogger(__name__)

_model_instance = None


def _get_model():
    global _model_instance
    if _model_instance is None:
        from sentence_transformers import SentenceTransformer
        settings = get_settings()
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _model_instance = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding model loaded")
    return _model_instance


class EmbeddingGenerator:
    """Generates vector embeddings for text using SentenceTransformers."""

    def __init__(self):
        self._model = _get_model()

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        """
        Embed a list of documents.
        Returns shape: (n_documents, embedding_dim)
        """
        if not texts:
            return np.array([])
        logger.info(f"Embedding {len(texts)} documents")
        embeddings = self._model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        return np.array(embeddings, dtype="float32")

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query string.
        Returns shape: (1, embedding_dim)
        """
        embedding = self._model.encode([query], show_progress_bar=False, normalize_embeddings=True)
        return np.array(embedding, dtype="float32")
