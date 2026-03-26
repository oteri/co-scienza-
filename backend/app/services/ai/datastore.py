"""
Vertex AI RAG Engine corpus management.

On first run, creates a RAG corpus and links it to the GDrive /co-scienza/sources/ folder.
After each ingestion, triggers a re-import so the corpus stays in sync.
"""

import vertexai
from vertexai.preview import rag

from app.core.config import settings


def _init_vertexai() -> None:
    vertexai.init(
        project=settings.GOOGLE_CLOUD_PROJECT,
        location=settings.VERTEX_AI_LOCATION,
    )


async def ensure_corpus() -> str:
    """Return the corpus resource name, creating it if it doesn't exist yet."""
    _init_vertexai()

    if settings.VERTEX_AI_RAG_CORPUS:
        return settings.VERTEX_AI_RAG_CORPUS

    corpus = rag.create_corpus(display_name="coscienza-library")
    corpus_name = corpus.name

    # Persist corpus name — in production, write back to .env or a config store
    print(f"[datastore] Created RAG corpus: {corpus_name}")
    print(f"[datastore] Add VERTEX_AI_RAG_CORPUS={corpus_name} to your .env")

    return corpus_name


async def import_gdrive_folder(folder_id: str) -> None:
    """Import (or re-import) an entire GDrive folder into the RAG corpus."""
    corpus_name = await ensure_corpus()
    _init_vertexai()

    gdrive_url = f"https://drive.google.com/drive/folders/{folder_id}"
    response = rag.import_files(
        corpus_name=corpus_name,
        paths=[gdrive_url],
        chunk_size=512,
        chunk_overlap=100,
    )
    print(f"[datastore] Import response: {response}")


async def import_gdrive_file(file_id: str) -> None:
    """Import a single GDrive file into the RAG corpus."""
    corpus_name = await ensure_corpus()
    _init_vertexai()

    gdrive_url = f"https://drive.google.com/file/d/{file_id}"
    rag.import_files(
        corpus_name=corpus_name,
        paths=[gdrive_url],
        chunk_size=512,
        chunk_overlap=100,
    )
