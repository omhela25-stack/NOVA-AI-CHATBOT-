import json
import streamlit as st
import streamlit.components.v1 as components
from groq import Groq


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="NOVA AI",
    page_icon="✦",
    layout="wide"
)


# ---------------- SESSION STATE ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "welcome_played" not in st.session_state:
    st.session_state.welcome_played = False


# ---------------- GROQ CONFIGURATION ----------------

MODELS = {
    "general": "openai/gpt-oss-120b",
    "coding": "qwen/qwen3.8-27b"
}

# The key must be stored in Streamlit Cloud > App settings > Secrets:
# GROQ_API_KEY = "your_key"
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as exc:
    st.error(
        "NOVA cannot find GROQ_API_KEY. Add it to your Streamlit Secrets "
        "and restart the app."
    )
    st.stop()


# ---------------- VOICE OUTPUT ----------------

def speak_text(text):
    """Speak text in the visitor's browser using its built-in speech engine."""
    safe_text = json.dumps(str(text))

    voice_html = f"""
    <script>
    const textToSpeak = {safe_text};

    function speakNOVA() {{
        if (!("speechSynthesis" in window)) return;

        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(textToSpeak);
        utterance.lang = "en-US";
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        const voices = window.speechSynthesis.getVoices();
        const preferred = voices.find(v => v.lang === "en-US");
        if (preferred) utterance.voice = preferred;

        window.speechSynthesis.speak(utterance);
    }}

    speakNOVA();
    </script>
    """

    components.html(voice_html, height=0)


# ---------------- AI MODEL SELECTION ----------------

def select_model(prompt):
    coding_keywords = [
        "python", "code", "coding", "program", "debug",
        "error", "bug", "function", "javascript", "html",
        "css", "sql", "algorithm", "streamlit", "api"
    ]

    if any(word in prompt.lower() for word in coding_keywords):
        return MODELS["coding"]

    return MODELS["general"]

