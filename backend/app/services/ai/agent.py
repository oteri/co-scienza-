"""
ADK root agent — Gemini 2.5 Flash with:
  1. VertexAiRagRetrieval  — semantic search over the user's library (GDrive-backed corpus)
  2. search_sources_by_metadata — filter by author, year, type, tag (SQLite)
  3. get_source_content         — fetch full content.md of a specific source
  4. google_search              — live web grounding (used sparingly)
"""

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.adk.tools.retrieval import VertexAiRagRetrieval
import vertexai

from app.core.config import settings
from app.services.ai.tools import get_source_content, search_sources_by_metadata

_runner: Runner | None = None


def _build_agent() -> Agent:
    vertexai.init(
        project=settings.GOOGLE_CLOUD_PROJECT,
        location=settings.VERTEX_AI_LOCATION,
    )

    rag_retrieval = VertexAiRagRetrieval(
        rag_corpus=settings.VERTEX_AI_RAG_CORPUS,
        similarity_top_k=5,
        vector_distance_threshold=0.5,
    )

    return Agent(
        name="coscienza_assistant",
        model=settings.GEMINI_MODEL,
        description="Personal knowledge assistant grounded in the user's library.",
        instruction=(
            "You are a personal research assistant with access to the user's knowledge library.\n"
            "Always ground your answers in retrieved content from the library. "
            "Cite sources with title and page/section.\n"
            "Use google_search only when the user's question requires up-to-date information "
            "not found in the library.\n"
            "If you don't find relevant content, say so clearly."
        ),
        tools=[
            rag_retrieval,
            search_sources_by_metadata,
            get_source_content,
            google_search,
        ],
    )


async def get_agent_runner() -> Runner:
    global _runner
    if _runner is None:
        agent = _build_agent()
        session_service = InMemorySessionService()
        _runner = Runner(
            agent=agent,
            app_name="coscienza",
            session_service=session_service,
        )
    return _runner
