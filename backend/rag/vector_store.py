"""
FAISS-based vector store for the SupportPilot knowledge base.
"""
import os
import pickle
import logging
import numpy as np
from typing import Optional

from backend.core.config import get_settings

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Wraps FAISS IndexFlatL2 for document storage and similarity search.
    """

    def __init__(self):
        self._index = None
        self._metadata: list[dict] = []  # [{source: str, text: str}]
        settings = get_settings()
        self._index_path = settings.faiss_index_path
        self._metadata_path = settings.faiss_metadata_path

    def build(self, embeddings: np.ndarray, metadata: list[dict]) -> None:
        """Build FAISS index from embeddings and associated metadata."""
        try:
            import faiss
        except ImportError:
            raise RuntimeError("faiss-cpu package not installed")

        if embeddings.shape[0] == 0:
            logger.warning("No embeddings provided to build index")
            return

        dim = embeddings.shape[1]
        self._index = faiss.IndexFlatL2(dim)
        self._index.add(embeddings)
        self._metadata = metadata
        logger.info(f"Built FAISS index with {len(metadata)} documents (dim={dim})")

    def save(self) -> None:
        """Persist index and metadata to disk."""
        try:
            import faiss
        except ImportError:
            raise RuntimeError("faiss-cpu package not installed")

        if self._index is None:
            logger.warning("No index to save")
            return

        # Ensure directories exist
        os.makedirs(os.path.dirname(self._index_path) or ".", exist_ok=True)
        os.makedirs(os.path.dirname(self._metadata_path) or ".", exist_ok=True)

        faiss.write_index(self._index, self._index_path)
        with open(self._metadata_path, "wb") as f:
            pickle.dump(self._metadata, f)
        logger.info(f"Saved FAISS index to {self._index_path}")

    def load(self) -> bool:
        """Load persisted index from disk. Returns True if successful."""
        try:
            import faiss
        except ImportError:
            raise RuntimeError("faiss-cpu package not installed")

        if not os.path.exists(self._index_path) or not os.path.exists(self._metadata_path):
            logger.warning("FAISS index files not found — knowledge base not ingested yet")
            return False

        self._index = faiss.read_index(self._index_path)
        with open(self._metadata_path, "rb") as f:
            self._metadata = pickle.load(f)
        logger.info(f"Loaded FAISS index with {len(self._metadata)} documents")
        return True

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[dict]:
        """
        Search for top-k similar documents.
        Returns list of {source, text, distance}.
        """
        if self._index is None or self._index.ntotal == 0:
            logger.warning("VectorStore search called but index is empty or not loaded")
            return []

        actual_k = min(top_k, self._index.ntotal)
        distances, indices = self._index.search(query_embedding, actual_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            meta = self._metadata[idx]
            results.append({
                "source": meta.get("source", "Unknown"),
                "text": meta.get("text", ""),
                "distance": float(dist),
            })
        return results

    @property
    def is_loaded(self) -> bool:
        return self._index is not None and self._index.ntotal > 0
