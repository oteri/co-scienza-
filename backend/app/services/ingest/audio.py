import os
import tempfile

from faster_whisper import WhisperModel

from app.services.ingest.base import BaseIngestor, IngestResult

_model: WhisperModel | None = None


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel("base", device="cpu", compute_type="int8")
    return _model


class AudioIngestor(BaseIngestor):
    async def ingest(self, params: dict) -> IngestResult:
        audio_bytes = bytes.fromhex(params["content"])
        filename = params.get("filename", "audio.mp3")

        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1], delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name

        try:
            model = _get_model()
            segments, info = model.transcribe(tmp_path, beam_size=5)
            text = " ".join(seg.text for seg in segments)
        finally:
            os.unlink(tmp_path)

        # Group into paragraphs every ~300 words
        words = text.split()
        paragraphs = [" ".join(words[i:i+300]) for i in range(0, len(words), 300)]
        content_md = "\n\n".join(paragraphs)

        return IngestResult(
            title=filename.removesuffix(os.path.splitext(filename)[1]),
            content_md=content_md,
            metadata={
                "source_type": "audio",
                "filename": filename,
                "language": info.language,
                "duration_s": round(info.duration, 1),
            },
        )
