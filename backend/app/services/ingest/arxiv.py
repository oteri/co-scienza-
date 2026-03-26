import re

import httpx

from app.services.ingest.base import BaseIngestor, IngestResult
from app.services.ingest.pdf import PdfIngestor

ARXIV_API = "https://export.arxiv.org/api/query"


def _parse_id(raw: str) -> str:
    """Extract arXiv ID from URL or plain ID like '2301.00001' or 'abs/2301.00001'."""
    match = re.search(r"(\d{4}\.\d{4,5}(v\d+)?)", raw)
    return match.group(1) if match else raw.strip()


class ArxivIngestor(BaseIngestor):
    async def ingest(self, params: dict) -> IngestResult:
        arxiv_id = _parse_id(params.get("arxiv_id") or params.get("url", ""))

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(ARXIV_API, params={"id_list": arxiv_id, "max_results": 1})
            resp.raise_for_status()
            xml = resp.text

        # Basic XML parse — no lxml needed for this simple case
        def _tag(tag: str) -> str:
            m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", xml, re.DOTALL)
            return m.group(1).strip() if m else ""

        title = _tag("title") or arxiv_id
        abstract = _tag("summary")
        authors = re.findall(r"<name>(.*?)</name>", xml)
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        # Download PDF
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            pdf_resp = await client.get(pdf_url)
            pdf_resp.raise_for_status()
            pdf_bytes = pdf_resp.content

        pdf_result = await PdfIngestor().ingest(
            {"content": pdf_bytes.hex(), "filename": f"{arxiv_id}.pdf"}
        )

        metadata = {
            "source_type": "arxiv",
            "arxiv_id": arxiv_id,
            "authors": authors,
            "abstract": abstract,
        }

        return IngestResult(
            title=title,
            content_md=f"# {title}\n\n**Abstract:** {abstract}\n\n---\n\n{pdf_result.content_md}",
            metadata=metadata,
            pdf_bytes=pdf_bytes,
        )
