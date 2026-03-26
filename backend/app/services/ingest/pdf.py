import io

import pymupdf

from app.services.ingest.base import BaseIngestor, IngestResult


class PdfIngestor(BaseIngestor):
    async def ingest(self, params: dict) -> IngestResult:
        # params["content"] is hex-encoded bytes from the upload endpoint
        pdf_bytes = bytes.fromhex(params["content"])
        filename = params.get("filename", "document.pdf")

        doc = pymupdf.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")
        pages = []
        for page in doc:
            pages.append(page.get_text("markdown"))
        content_md = "\n\n---\n\n".join(pages)

        meta = doc.metadata or {}
        title = meta.get("title") or filename.removesuffix(".pdf")

        return IngestResult(
            title=title,
            content_md=content_md,
            metadata={
                "source_type": "pdf",
                "filename": filename,
                "page_count": doc.page_count,
                "author": meta.get("author"),
            },
            pdf_bytes=pdf_bytes,
        )
