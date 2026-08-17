"""
Tests: RAG retrieval and classification (mocked LLM)
"""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock


class TestVectorStore:
    def test_build_and_search(self):
        pytest.importorskip("faiss")
        from backend.rag.vector_store import VectorStore
        store = VectorStore()

        embeddings = np.random.rand(5, 384).astype("float32")
        metadata = [{"source": f"doc{i}.md", "text": f"Text chunk {i}"} for i in range(5)]
        store.build(embeddings, metadata)
        assert store.is_loaded

        query = np.random.rand(1, 384).astype("float32")
        results = store.search(query, top_k=3)
        assert len(results) == 3
        assert "source" in results[0]
        assert "text" in results[0]
        assert "distance" in results[0]

    def test_empty_search_returns_empty(self):
        pytest.importorskip("faiss")
        from backend.rag.vector_store import VectorStore
        store = VectorStore()
        query = np.random.rand(1, 384).astype("float32")
        results = store.search(query)
        assert results == []


class TestKnowledgeLoader:
    def test_load_markdown(self, tmp_path):
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\n" + "A" * 700)  # Long enough to chunk
        from backend.rag.knowledge_loader import KnowledgeLoader
        loader = KnowledgeLoader(str(tmp_path))
        docs = loader.load()
        assert len(docs) >= 1
        assert docs[0]["source"] == "test.md"

    def test_missing_docs_path(self, tmp_path):
        from backend.rag.knowledge_loader import KnowledgeLoader
        loader = KnowledgeLoader(str(tmp_path / "nonexistent"))
        docs = loader.load()
        assert docs == []


class TestRAGClassification:
    def test_classification_fallback_on_llm_error(self):
        with patch("backend.rag.rag_pipeline.get_llm_manager") as mock_mgr:
            mock_mgr.return_value.generate.side_effect = RuntimeError("All providers failed")
            # Re-create pipeline instance with mocked manager
            from backend.rag import rag_pipeline
            rag_pipeline._pipeline = None  # reset singleton

            with patch("backend.rag.rag_pipeline._get_store") as mock_store:
                mock_store.return_value.search.return_value = []
                mock_store.return_value.is_loaded = False
                pipeline = rag_pipeline.RAGPipeline()

                result = pipeline.classify_ticket("VPN broken", "Cannot connect")
                # Should return defaults, not raise
                assert result["category"] == "Other"
                assert result["severity"] == "Medium"
                assert result["priority"] == "P3"
