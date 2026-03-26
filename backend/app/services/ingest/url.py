import httpx
import trafilatura

from app.services.ingest.base import BaseIngestor, IngestResult


class UrlIngestor(BaseIngestor):
    async def ingest(self, params: dict) -> IngestResult:
        url = params["url"]
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "co-scienza/1.0"})
            resp.raise_for_status()
            html = resp.text

        content_md = trafilatura.extract(
            html,
            output_format="markdown",
            include_links=False,
            include_images=False,
        ) or ""
        title = trafilatura.extract_metadata(html)
        title_str = title.title if title and title.title else url

        metadata = {"url": url, "source_type": "url"}
        if title:
            metadata.update({
                "author": title.author,
                "date": title.date,
                "sitename": title.sitename,
            })

        return IngestResult(title=title_str, content_md=content_md, metadata=metadata)
