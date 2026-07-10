"""Voice transcription. Prefers a local model (faster-whisper — fits the
self-hosted, zero-cloud ethos); falls back to OpenAI Whisper if a key is
set. Optional dependency: pip install "mystic-agent[voice]".
"""

import asyncio

_model = None


def _local_available() -> bool:
    try:
        import faster_whisper  # noqa: F401

        return True
    except ImportError:
        return False


def _transcribe_local(path: str) -> str:
    global _model
    from faster_whisper import WhisperModel

    if _model is None:
        _model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _info = _model.transcribe(path, language="pl")
    return " ".join(s.text for s in segments).strip()


async def transcribe(path: str, openai_key: str = "") -> str | None:
    """Return the transcript, or None if no backend is available."""
    if _local_available():
        return await asyncio.to_thread(_transcribe_local, path)
    if openai_key:
        import openai

        client = openai.AsyncOpenAI(api_key=openai_key)
        with open(path, "rb") as f:
            resp = await client.audio.transcriptions.create(
                model="whisper-1", file=f
            )
        return resp.text.strip()
    return None
