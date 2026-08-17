"""
RAG Pipeline — orchestrates retrieval-augmented generation.
Used by the AI service to answer user questions and classify tickets.
"""
import json
import logging
from typing import Optional

from backend.rag.embedding_generator import EmbeddingGenerator
from backend.rag.vector_store import VectorStore
from backend.llm.provider_manager import get_llm_manager
from backend.llm.prompts import ASK_AI_PROMPT, CLASSIFICATION_PROMPT
from backend.core.config import get_settings

logger = logging.getLogger(__name__)

# Module-level singletons — loaded once
_embedder: Optional[EmbeddingGenerator] = None
_store: Optional[VectorStore] = None


def _get_embedder() -> EmbeddingGenerator:
    global _embedder
    if _embedder is None:
        _embedder = EmbeddingGenerator()
    return _embedder


def _get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
        _store.load()
    return _store


class RAGPipeline:
    """
    Orchestrates: embed query -> FAISS search -> build context -> LLM generation.
    """

    def __init__(self):
        self._embedder = _get_embedder()
        self._store = _get_store()
        self._llm = get_llm_manager()
        settings = get_settings()
        self._top_k = settings.top_k_results

    def ask(self, title: str, description: str) -> dict:
        """
        Answer a user's IT question.
        Returns dict with keys: full_response, context_used, retrieval_summary
        """
        query = f"{title}\n{description}"
        logger.info(f"RAG ask: '{title[:60]}'")

        # 1. Embed query
        query_emb = self._embedder.embed_query(query)

        # 2. Retrieve from FAISS
        results = self._store.search(query_emb, top_k=self._top_k)
        context_used = len(results) > 0

        # 3. Build context string
        if results:
            context_parts = []
            for i, r in enumerate(results, 1):
                context_parts.append(f"[KB Article {i} — Source: {r['source']}]\n{r['text']}")
            context = "\n\n".join(context_parts)
            retrieval_summary = f"Retrieved {len(results)} relevant KB articles: " + \
                                 ", ".join(set(r['source'] for r in results))
        else:
            context = "No relevant Knowledge Base articles found."
            retrieval_summary = "No KB articles matched. Using general IT knowledge."

        logger.info(f"RAG retrieval: {retrieval_summary}")

        # 4. Build prompt
        prompt = ASK_AI_PROMPT.format(
            context=context,
            retrieval_summary=retrieval_summary,
            title=title,
            description=description,
        )

        # 5. Generate response
        full_response = self._llm.generate(prompt, max_tokens=900)

        return {
            "full_response": full_response,
            "context_used": context_used,
            "retrieval_summary": retrieval_summary,
        }

    def classify_ticket(self, title: str, description: str) -> dict:
        """
        Classify a ticket using LLM.
        Returns dict with category, severity, priority, ai_analysis, ai_recommendation.
        Falls back to defaults if classification fails.
        """
        logger.info(f"Classifying ticket: '{title[:60]}'")
        prompt = CLASSIFICATION_PROMPT.format(title=title, description=description)

        defaults = {
            "category": "Other",
            "severity": "Medium",
            "priority": "P3",
            "ai_analysis": "Automated classification unavailable.",
            "ai_recommendation": "Please review manually.",
        }

        try:
            raw = self._llm.generate(prompt, max_tokens=300, response_format="json")
            # Strip code fences if present
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            data = json.loads(raw)

            # Validate and sanitise
            valid_categories = [
                "Hardware", "Software", "Network", "VPN", "Password Reset",
                "Email", "Printer", "Security", "Cloud", "Database", "Other"
            ]
            valid_severities = ["Low", "Medium", "High", "Critical"]
            valid_priorities = ["P1", "P2", "P3", "P4"]

            return {
                "category": data.get("category", "Other") if data.get("category") in valid_categories else "Other",
                "severity": data.get("severity", "Medium") if data.get("severity") in valid_severities else "Medium",
                "priority": data.get("priority", "P3") if data.get("priority") in valid_priorities else "P3",
                "ai_analysis": str(data.get("ai_analysis", defaults["ai_analysis"]))[:1000],
                "ai_recommendation": str(data.get("ai_recommendation", defaults["ai_recommendation"]))[:1000],
            }
        except Exception as e:
            logger.error(f"Ticket classification failed: {e}")
            return defaults
