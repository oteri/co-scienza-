import base64

from google import genai
from google.genai import types

from app.core.config import settings
from app.services.ingest.base import BaseIngestor, IngestResult

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GOOGLE_GENAI_API_KEY)
    return _client


class ImageIngestor(BaseIngestor):
    async def ingest(self, params: dict) -> IngestResult:
        image_bytes = bytes.fromhex(params["content"])
        filename = params.get("filename", "image.png")
        mime = params.get("mime", "image/png")

        client = _get_client()
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime),
                "Describe this image in detail. Extract any visible text verbatim. "
                "Provide a structured markdown description.",
            ],
        )
        content_md = response.text or ""
        title = filename.rsplit(".", 1)[0]

        return IngestResult(
            title=title,
            content_md=content_md,
            metadata={"source_type": "image", "filename": filename},
        )
