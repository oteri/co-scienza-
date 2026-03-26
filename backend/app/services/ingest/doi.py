import httpx

from app.services.ingest.base import BaseIngestor, IngestResult
from app.services.ingest.pdf import PdfIngestor

CROSSREF_API = "https://api.crossref.org/works"
UNPAYWALL_API = "https://api.unpaywall.org/v2"


class DoiIngestor(BaseIngestor):
    async def ingest(self, params: dict) -> IngestResult:
        doi = params["doi"].strip().lstrip("https://doi.org/")

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{CROSSREF_API}/{doi}", headers={"User-Agent": "co-scienza/1.0"})
            resp.raise_for_status()
            data = resp.json()["message"]

        title = data.get("title", [doi])[0]
        authors = [
            f"{a.get('given', '')} {a.get('family', '')}".strip()
            for a in data.get("author", [])
        ]
        year = (data.get("published") or data.get("created") or {}).get("date-parts", [[None]])[0][0]
        abstract = data.get("abstract", "")
        journal = data.get("container-title", [None])[0]

        # Try Unpaywall for open-access PDF
        pdf_bytes: bytes | None = None
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                up = await client.get(f"{UNPAYWALL_API}/{doi}?email=coscienza@localhost")
                if up.status_code == 200:
                    best = up.json().get("best_oa_location") or {}
                    pdf_url = best.get("url_for_pdf")
                    if pdf_url:
                        pr = await client.get(pdf_url, follow_redirects=True, timeout=60)
                        pdf_bytes = pr.content
        except Exception:
            pass

        content_md = f"# {title}\n\n**Authors:** {', '.join(authors)}\n\n**Abstract:** {abstract}"
        if pdf_bytes:
            pdf_result = await PdfIngestor().ingest({"content": pdf_bytes.hex(), "filename": f"{doi.replace('/', '_')}.pdf"})
            content_md += f"\n\n---\n\n{pdf_result.content_md}"

        return IngestResult(
            title=title,
            content_md=content_md,
            metadata={
                "source_type": "doi",
                "doi": doi,
                "authors": authors,
                "year": year,
                "journal": journal,
                "abstract": abstract,
            },
            pdf_bytes=pdf_bytes,
        )
