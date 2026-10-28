"""Small language helpers for English, Hindi, and Tamil."""

from typing import Optional

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
}

GROQ_LANGUAGE_CODES = {"en": "en", "hi": "hi", "ta": "ta"}
GTTS_LANGUAGE_CODES = {"en": "en", "hi": "hi", "ta": "ta"}


def detect_language(text: str, selected_language: Optional[str] = "auto") -> str:
    """Detect language using an explicit user choice or Unicode script.

    Script detection is intentionally simple. If a person types Hindi or Tamil
    using Latin characters, they should select that language in the UI.
    """
    if selected_language in {"en", "hi", "ta"}:
        return selected_language

    text = text or ""
    for char in text:
        code = ord(char)
        # Devanagari block used for Hindi text.
        if 0x0900 <= code <= 0x097F:
            return "hi"
        # Tamil Unicode block.
        if 0x0B80 <= code <= 0x0BFF:
            return "ta"
    return "en"


def language_name(code: str) -> str:
    return LANGUAGE_NAMES.get(code, "English")
