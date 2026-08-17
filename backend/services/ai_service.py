"""
AI Service — orchestrates RAG pipeline for user queries and ticket classification.
This is the single integration point between business logic and the AI layer.
"""
import logging
from typing import Optional

from backend.rag.rag_pipeline import RAGPipeline
from backend.services.ticket_service import TicketService

logger = logging.getLogger(__name__)

_pipeline: Optional[RAGPipeline] = None


def _get_pipeline() -> RAGPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline


class AIService:

    @staticmethod
    def ask_ai(title: str, description: str) -> dict:
        """
        Handle a user's AI question.
        Returns dict with full_response, context_used, retrieval_summary.
        """
        try:
            pipeline = _get_pipeline()
            result = pipeline.ask(title=title, description=description)
            return {
                "success": True,
                "full_response": result["full_response"],
                "context_used": result["context_used"],
                "retrieval_summary": result["retrieval_summary"],
            }
        except ValueError as e:
            # Configuration error (missing API keys)
            error_msg = str(e)
            logger.error(f"AIService.ask_ai configuration error: {e}")
            if "not configured" in error_msg.lower() or "api_key" in error_msg.lower():
                return {
                    "success": False,
                    "full_response": "## Configuration Required\n\nThe AI service needs at least one LLM provider API key to be configured.\n\n---\n\n## Setup Instructions\n\n1. Get a free API key from one of:\n   - **Groq** (recommended): https://console.groq.com/keys\n   - **Google Gemini**: https://aistudio.google.com/app/apikey\n   - **OpenRouter**: https://openrouter.ai/keys\n\n2. Add it to your `.env` file:\n   ```\n   GROQ_API_KEY=your_key_here\n   ```\n\n3. Restart the backend server\n\n---\n\n## Alternative\n\nCreate a support ticket and an engineer will assist you directly.",
                    "context_used": False,
                    "retrieval_summary": "AI configuration incomplete",
                    "error": "Configuration required",
                }
            return {
                "success": False,
                "full_response": f"## Error\n\nAI service configuration error: {error_msg}\n\n---\n\n## Recommended Action\n\nPlease create a support ticket for engineer assistance.",
                "context_used": False,
                "retrieval_summary": "Configuration error",
                "error": str(e),
            }
        except Exception as e:
            logger.error(f"AIService.ask_ai failed: {e}")
            return {
                "success": False,
                "full_response": "## AI Service Temporarily Unavailable\n\nWe're experiencing technical difficulties with the AI assistant.\n\n---\n\n## What to do now\n\n1. **Create a Support Ticket**: Click the \"Didn't Work → Create Ticket\" button below\n2. Our support engineers will assist you directly\n3. Your ticket will be prioritized based on urgency\n\n---\n\n## What went wrong\n\nThe AI service could not process your request. This might be due to:\n- Network connectivity issues\n- API provider rate limits\n- Service maintenance\n\nOur team has been notified and is working to resolve this.",
                "context_used": False,
                "retrieval_summary": "AI service unavailable",
                "error": str(e),
            }

    @staticmethod
    def classify_and_update_ticket(db, ticket_id: int, title: str, description: str) -> bool:
        """
        Classify a ticket and update it with AI-generated metadata.
        Returns True on success.
        """
        try:
            pipeline = _get_pipeline()
            classification = pipeline.classify_ticket(title=title, description=description)

            TicketService.update_ai_classification(
                db=db,
                ticket_id=ticket_id,
                category=classification["category"],
                severity=classification["severity"],
                priority=classification["priority"],
                ai_analysis=classification["ai_analysis"],
                ai_recommendation=classification["ai_recommendation"],
            )
            logger.info(f"Ticket #{ticket_id} classified: {classification['category']} / "
                        f"{classification['severity']} / {classification['priority']}")
            return True
        except Exception as e:
            logger.error(f"Ticket classification failed for #{ticket_id}: {e}")
            return False
