"""
Celery tasks for source ingestion.

Flow for every source type:
  1. Select the right ingestor
  2. Run ingestor → IngestResult (title, content_md, metadata, pdf_bytes)
  3. Save files to GDrive folder for this source
  4. Trigger Vertex AI RAG Engine re-index for the uploaded GDrive file
  5. Update source record in SQLite: status=ready, gdrive_folder_id, title, metadata
"""

import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.workers.celery_app import celery_app

# Synchronous SQLAlchemy engine for Celery (not async)
_sync_engine = create_engine(settings.DATABASE_URL.replace("+aiosqlite", ""))
SyncSession = sessionmaker(bind=_sync_engine)

INGESTOR_MAP = {
    "url": "app.services.ingest.url.UrlIngestor",
    "pdf": "app.services.ingest.pdf.PdfIngestor",
    "doi": "app.services.ingest.doi.DoiIngestor",
    "arxiv": "app.services.ingest.arxiv.ArxivIngestor",
    "youtube": "app.services.ingest.youtube.YoutubeIngestor",
    "audio": "app.services.ingest.audio.AudioIngestor",
    "image": "app.services.ingest.image.ImageIngestor",
}


def _get_ingestor(source_type: str):
    import importlib
    path = INGESTOR_MAP.get(source_type)
    if not path:
        raise ValueError(f"Unknown source type: {source_type}")
    module_path, class_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)()


def _update_source(db: Session, source_id: str, **kwargs) -> None:
    from app.models.source import Source
    source = db.get(Source, source_id)
    if source:
        for k, v in kwargs.items():
            setattr(source, k, v)
        source.updated_at = datetime.now(timezone.utc)
        db.commit()


@celery_app.task(bind=True, max_retries=3)
def ingest_source(self, source_id: str, params: dict) -> dict:
    source_type = params.get("type")
    db = SyncSession()
    try:
        _update_source(db, source_id, status="processing")

        ingestor = _get_ingestor(source_type)
        result = asyncio.run(ingestor.ingest(params))

        # TODO: upload to GDrive via GDriveClient
        # TODO: call datastore.import_gdrive_file(gdrive_file_id)

        year = result.metadata.get("year") or datetime.now().year
        slug = f"{source_id[:8]}"

        _update_source(
            db,
            source_id,
            status="ready",
            title=result.title,
            source_metadata=result.metadata,
        )
        return {"status": "ready", "source_id": source_id}

    except Exception as exc:
        _update_source(db, source_id, status="failed", error=str(exc))
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    finally:
        db.close()
