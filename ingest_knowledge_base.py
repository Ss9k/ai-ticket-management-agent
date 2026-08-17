"""
SupportPilot Knowledge Base Ingestion Script

Run this once (and whenever docs/ changes) to build the FAISS vector index.

Usage:
    python ingest_knowledge_base.py

The script reads all .md and .pdf files from docs/, generates embeddings,
and saves the FAISS index to backend/rag/.
"""
import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.core.config import get_settings
from backend.core.logging_config import setup_logging
from backend.rag.knowledge_loader import KnowledgeLoader
from backend.rag.embedding_generator import EmbeddingGenerator
from backend.rag.vector_store import VectorStore

setup_logging("INFO")
logger = logging.getLogger(__name__)


def main():
    settings = get_settings()
    logger.info("=" * 60)
    logger.info("SupportPilot Knowledge Base Ingestion")
    logger.info("=" * 60)

    # Step 1: Load documents
    logger.info(f"Loading documents from: {settings.docs_path}")
    loader = KnowledgeLoader(settings.docs_path)
    documents = loader.load()

    if not documents:
        logger.error("No documents found. Add .md or .pdf files to the docs/ directory.")
        sys.exit(1)

    logger.info(f"Loaded {len(documents)} document chunks")

    # Step 2: Generate embeddings
    logger.info(f"Generating embeddings with model: {settings.embedding_model}")
    embedder = EmbeddingGenerator()
    texts = [doc["text"] for doc in documents]
    embeddings = embedder.embed_documents(texts)
    logger.info(f"Generated embeddings shape: {embeddings.shape}")

    # Step 3: Build and save FAISS index
    logger.info("Building FAISS index...")
    store = VectorStore()
    store.build(embeddings, documents)
    store.save()

    logger.info("=" * 60)
    logger.info(f"Knowledge base ingestion complete!")
    logger.info(f"Index saved to: {settings.faiss_index_path}")
    logger.info(f"Metadata saved to: {settings.faiss_metadata_path}")
    logger.info(f"Total chunks indexed: {len(documents)}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
