"""Speech-to-text and text-to-speech helpers."""

from io import BytesIO
from typing import Optional

from gtts import gTTS
from groq import Groq

from kisanvaani.language import GROQ_LANGUAGE_CODES, GTTS_LANGUAGE_CODES

STT_MODEL_DEFAULT = "whisper-large-v3-turbo"


def transcribe_audio(
    audio_bytes: bytes,
    client: Groq,
    input_language: str = "auto",
    model: str = STT_MODEL_DEFAULT,
) -> str:
    """Transcribe recorded audio to text, optionally hinting at its language."""
    if not audio_bytes:
        raise ValueError("No audio was supplied. Record a question first.")

    options = {
        "file": ("kisanvaani-question.wav", audio_bytes),
        "model": model,
        "response_format": "text",
    }
    language_code = GROQ_LANGUAGE_CODES.get(input_language)
    if language_code:
        options["language"] = language_code

    result = client.audio.transcriptions.create(**options)
    if isinstance(result, str):
        transcript = result.strip()
    else:
        transcript = str(getattr(result, "text", "")).strip()

    if not transcript:
        raise ValueError("Speech recognition returned an empty transcript.")
    return transcript


def make_speech_audio(text: str, language_code: str) -> bytes:
    """Generate an MP3 reply through gTTS for English, Hindi, or Tamil.

    gTTS relies on an internet connection and a third-party service. It is used
    here for an educational prototype, not as a production SLA-backed service.
    """
    clean_text = (text or "").strip()
    if not clean_text:
        raise ValueError("There is no answer text to speak.")

    tts_language = GTTS_LANGUAGE_CODES.get(language_code, "en")
    mp3_buffer = BytesIO()
    speech = gTTS(text=clean_text, lang=tts_language, slow=False)
    speech.write_to_fp(mp3_buffer)
    return mp3_buffer.getvalue()
