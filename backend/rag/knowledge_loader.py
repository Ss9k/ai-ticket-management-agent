"""
Knowledge base loader — reads .md and .pdf files from docs/ directory.
Splits large documents into chunks for better retrieval.
"""
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CHUNK_SIZE = 600       # characters per chunk
CHUNK_OVERLAP = 100    # overlap between consecutive chunks


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return [c for c in chunks if len(c) > 50]  # discard tiny remnants


class KnowledgeLoader:
    """Loads and chunks documents from the docs/ directory."""

    def __init__(self, docs_path: str):
        self._docs_path = docs_path

    def load(self) -> list[dict]:
        """
        Load all supported documents.
        Returns list of {source: str, text: str} dicts.
        """
        documents = []
        path = Path(self._docs_path)

        if not path.exists():
            logger.warning(f"Docs directory not found: {self._docs_path}")
            return documents

        files = list(path.rglob("*.md")) + list(path.rglob("*.pdf"))
        logger.info(f"Found {len(files)} files in {self._docs_path}")

        for file_path in files:
            try:
                if file_path.suffix.lower() == ".md":
                    docs = self._load_markdown(file_path)
                elif file_path.suffix.lower() == ".pdf":
                    docs = self._load_pdf(file_path)
                else:
                    continue
                documents.extend(docs)
                logger.info(f"Loaded {len(docs)} chunks from {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")

        logger.info(f"Total documents loaded: {len(documents)}")
        return documents

    def _load_markdown(self, file_path: Path) -> list[dict]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        chunks = _chunk_text(text)
        return [{"source": file_path.name, "text": chunk} for chunk in chunks]

    def _load_pdf(self, file_path: Path) -> list[dict]:
        try:
            import PyPDF2
            text_parts = []
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            full_text = "\n".join(text_parts)
            chunks = _chunk_text(full_text)
            return [{"source": file_path.name, "text": chunk} for chunk in chunks]
        except ImportError:
            logger.warning("PyPDF2 not installed — skipping PDF files")
            return []
