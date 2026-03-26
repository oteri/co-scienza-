"""
Custom ADK tools backed by SQLite — complement the Vertex AI RAG retrieval.
"""

from google.adk.tools import FunctionTool
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.source import Source


async def _search_sources_by_metadata(
    author: str | None = None,
    year: int | None = None,
    source_type: str | None = None,
    tag: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """Search the library by metadata filters (author, year, type, tag).

    Args:
        author: Filter by author name (partial match).
        year: Filter by publication year.
        source_type: Filter by type (pdf, url, doi, arxiv, youtube, audio, image, text).
        tag: Filter by tag name.
        limit: Maximum number of results.

    Returns:
        List of matching sources with id, title, type, and metadata.
    """
    async with AsyncSessionLocal() as db:
        query = select(Source).where(Source.status == "ready")
        if source_type:
            query = query.where(Source.type == source_type)
        result = await db.execute(query.limit(limit))
        sources = result.scalars().all()

    out = []
    for s in sources:
        meta = s.source_metadata or {}
        if author and author.lower() not in str(meta.get("authors", "")).lower():
            continue
        if year and str(year) not in str(meta.get("year", "")):
            continue
        out.append({"id": s.id, "title": s.title, "type": s.type, "metadata": meta})
    return out


async def _get_source_content(source_id: str) -> dict:
    """Fetch the full extracted text content of a specific source.

    Args:
        source_id: The UUID of the source.

    Returns:
        Dict with title and full content markdown text.
    """
    async with AsyncSessionLocal() as db:
        source = await db.get(Source, source_id)
    if not source:
        return {"error": f"Source {source_id} not found"}
    if source.local_cache_path:
        import aiofiles
        import os
        content_path = os.path.join(source.local_cache_path, "content.md")
        if os.path.exists(content_path):
            async with aiofiles.open(content_path) as f:
                content = await f.read()
            return {"id": source_id, "title": source.title, "content": content}
    return {"id": source_id, "title": source.title, "content": "(content not cached locally)"}


search_sources_by_metadata = FunctionTool(_search_sources_by_metadata)
get_source_content = FunctionTool(_get_source_content)
