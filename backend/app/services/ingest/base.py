"""
Base class for all source importers.

Each importer:
  1. Extracts content → (title, content_md, metadata, optional pdf_bytes)
  2. Saves to GDrive: source.pdf, content.md, metadata.json
  3. Triggers Vertex AI RAG Engine re-index for the uploaded file
  4. Updates source status in SQLite
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class IngestResult:
    title: str
    content_md: str
    metadata: dict
    pdf_bytes: bytes | None = None


class BaseIngestor(ABC):
    @abstractmethod
    async def ingest(self, params: dict) -> IngestResult:
        """Extract content from the source. Raise on failure."""
        ...
