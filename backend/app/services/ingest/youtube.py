import re

from youtube_transcript_api import YouTubeTranscriptApi

from app.services.ingest.base import BaseIngestor, IngestResult


def _extract_video_id(url: str) -> str:
    patterns = [
        r"youtu\.be/([^?&]+)",
        r"youtube\.com/watch\?v=([^&]+)",
        r"youtube\.com/embed/([^?&]+)",
    ]
    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    return url


class YoutubeIngestor(BaseIngestor):
    async def ingest(self, params: dict) -> IngestResult:
        video_id = _extract_video_id(params["url"])

        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        lines = [entry["text"] for entry in transcript_list]
        content_md = " ".join(lines)

        # Group into paragraphs every ~300 words
        words = content_md.split()
        paragraphs = [" ".join(words[i:i+300]) for i in range(0, len(words), 300)]
        content_md = "\n\n".join(paragraphs)

        title = params.get("title") or f"YouTube: {video_id}"

        return IngestResult(
            title=title,
            content_md=content_md,
            metadata={
                "source_type": "youtube",
                "video_id": video_id,
                "url": params["url"],
            },
        )
