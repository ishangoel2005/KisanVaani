"""KisanVaani: multilingual voice-first agricultural assistant."""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from streamlit_mic_recorder import mic_recorder

from kisanvaani.assistant import ask_kisanvaani
from kisanvaani.i18n import get_ui
from kisanvaani.language import LANGUAGE_NAMES
from kisanvaani.speech import make_speech_audio, transcribe_audio

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

st.set_page_config(
    page_title="KisanVaani | Agricultural Voice Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_setting(name: str, default: str = "") -> str:
    """Read a setting from Streamlit secrets first, then environment variables."""
    try:
        value = st.secrets.get(name)
    except Exception:
        value = None
    return str(value or os.getenv(name, default)).strip()


def language_display(code: str, ui_text: dict) -> str:
    labels = {
        "auto": ui_text["auto_detect"],
        "same": ui_text["same_as_question"],
        "en": ui_text["english"],
        "hi": ui_text["hindi"],
        "ta": ui_text["tamil"],
    }
    return labels.get(code, code)


def process_question(question: str, input_language: str, response_preference: str, ui_text: dict):
    # Remove the previous result before starting a new request so an error cannot
    # leave a stale answer visible below the new question.
    st.session_state.pop("kisanvaani_last_result", None)
    st.session_state.pop("kisanvaani_last_origin", None)
    api_key = get_setting("GROQ_API_KEY")
    if not api_key or api_key == "replace_with_your_groq_api_key":
        st.error(ui_text["key_missing"])
        return

    model = get_setting("GROQ_CHAT_MODEL", "openai/gpt-oss-20b")
    client = Groq(api_key=api_key)
    try:
        with st.spinner(ui_text["working"]):
            result = ask_kisanvaani(
                question=question,
                input_language=input_language,
                response_preference=response_preference,
                client=client,
                model=model,
            )
        # Every answer has text. Voice playback is best-effort; a TTS outage
        # should not erase an otherwise successful answer.
        try:
            result["audio_bytes"] = make_speech_audio(
                result["answer"], result["response_language"]
            )
            result["audio_error"] = None
        except Exception:
            result["audio_bytes"] = None
            result["audio_error"] = ui_text["audio_error"]

        st.session_state["kisanvaani_last_result"] = result
        st.session_state["kisanvaani_last_origin"] = "voice" if st.session_state.get("kisanvaani_current_origin") == "voice" else "text"
        st.session_state.pop("kisanvaani_last_error", None)
    except Exception as exc:
        # Show a useful error without exposing any secret values.
        st.session_state["kisanvaani_last_error"] = f"{ui_text['answer_error']}\n\nTechnical detail: {type(exc).__name__}: {exc}"


# Top-level interface language is independent of the language used for a question.
st.sidebar.title("🌱 KisanVaani")
interface_options = {"English": "en", "हिन्दी": "hi", "தமிழ்": "ta"}
selected_interface = st.sidebar.selectbox(
    "Interface language / இடைமுக மொழி / इंटरफ़ेस की भाषा",
    options=list(interface_options.keys()),
    index=0,
    key="kisanvaani_interface_language",
)
ui_language = interface_options[selected_interface]
t = get_ui(ui_language)

st.sidebar.markdown("---")
question_language = st.sidebar.selectbox(
    t["question_language"],
    options=["auto", "en", "hi", "ta"],
    index=0,
    format_func=lambda code: language_display(code, t),
    key="kisanvaani_question_language",
)
response_preference = st.sidebar.selectbox(
    t["answer_language"],
    options=["same", "en", "hi", "ta"],
    index=0,
    format_func=lambda code: language_display(code, t),
    key="kisanvaani_response_language",
)

with st.sidebar.expander(t["about_title"], expanded=False):
    st.write(t["about_body"])
with st.sidebar.expander(t["try_examples"], expanded=False):
    st.markdown(f"- {t['example_storage']}")
    st.markdown(f"- {t['example_soil']}")
    st.markdown(f"- {t['example_pest']}")
    st.markdown(f"- {t['example_wheat']}")
    st.markdown(f"- {t['example_water']}")

st.title("🌱 " + t["title"])
st.markdown(t["subtitle"])
st.caption(t["privacy_note"])

voice_tab, text_tab = st.tabs([t["voice_tab"], t["text_tab"]])

with voice_tab:
    st.write(t["voice_instructions"])
    st.caption(t["recording_limit"])
    recording = mic_recorder(
        start_prompt=t["record_start"],
        stop_prompt=t["record_stop"],
        just_once=True,
        use_container_width=True,
        key="kisanvaani_mic_recorder",
    )
    if recording and recording.get("bytes"):
        st.audio(recording["bytes"], format="audio/wav")
        st.caption(t["voice_ready"])
        if st.button(t["ask_voice"], type="primary", key="kisanvaani_ask_voice"):
            api_key = get_setting("GROQ_API_KEY")
            if not api_key or api_key == "replace_with_your_groq_api_key":
                st.error(t["key_missing"])
            else:
                st.session_state["kisanvaani_current_origin"] = "voice"
                try:
                    client = Groq(api_key=api_key)
                    stt_model = get_setting("GROQ_STT_MODEL", "whisper-large-v3-turbo")
                    with st.spinner(t["transcribing"]):
                        transcript = transcribe_audio(
                            recording["bytes"],
                            client=client,
                            input_language=question_language,
                            model=stt_model,
                        )
                    st.session_state["kisanvaani_last_transcript"] = transcript
                    process_question(transcript, question_language, response_preference, t)
                except Exception as exc:
                    st.session_state["kisanvaani_last_error"] = (
                        f"{t['speech_error']}\n\nTechnical detail: {type(exc).__name__}: {exc}"
                    )

with text_tab:
    st.write(t["text_instructions"])
    with st.form("kisanvaani_text_question_form", clear_on_submit=False):
        typed_question = st.text_area(
            t["question_label"],
            placeholder=t["question_placeholder"],
            height=110,
            key="kisanvaani_typed_question",
        )
        submitted = st.form_submit_button(t["ask_button"], type="primary", use_container_width=True)
    if submitted:
        st.session_state["kisanvaani_current_origin"] = "text"
        st.session_state.pop("kisanvaani_last_transcript", None)
        process_question(typed_question, question_language, response_preference, t)

if st.session_state.get("kisanvaani_last_error"):
    st.error(st.session_state["kisanvaani_last_error"])

last_result = st.session_state.get("kisanvaani_last_result")
if last_result:
    st.markdown("---")
    if st.session_state.get("kisanvaani_last_origin") == "voice":
        st.subheader(t["transcript"])
        st.info(last_result["question"])

    st.subheader(t["answer"])
    st.markdown(last_result["answer"])

    if last_result.get("audio_bytes"):
        st.caption(t["audio_caption"])
        st.audio(last_result["audio_bytes"], format="audio/mp3")
    elif last_result.get("audio_error"):
        st.info(last_result["audio_error"])

    docs = last_result.get("documents", [])
    st.subheader(t["sources"])
    if docs:
        for index, document in enumerate(docs, start=1):
            with st.expander(f"[S{index}] {document['title']}  ·  {t['relevance']}: {document['score']}"):
                st.write(document["content"])
                st.markdown(f"**{t['source_label']}:** [{document['source_title']}]({document['source_url']})")
    else:
        st.info(t["no_sources"])

    with st.expander(t["disclaimer_title"], expanded=False):
        st.write(t["disclaimer_body"])

    if st.button(t["clear_button"], key="kisanvaani_clear_answer"):
        st.session_state.pop("kisanvaani_last_result", None)
        st.session_state.pop("kisanvaani_last_origin", None)
        st.session_state.pop("kisanvaani_last_transcript", None)
        st.session_state.pop("kisanvaani_last_error", None)
        st.rerun()

st.markdown("---")
st.caption(t["language_hint"])
st.caption("KisanVaani student prototype · Built with Streamlit, Groq Whisper, RAG retrieval and gTTS")
