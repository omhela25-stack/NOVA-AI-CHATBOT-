import hashlib
import html
import json

import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
from streamlit_mic_recorder import mic_recorder


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="NOVA AI",
    page_icon="✦",
    layout="wide",
)


# ---------------- SESSION STATE ----------------

DEFAULTS = {
    "messages": [],
    "user_name": "",
    "welcome_played": False,
    "last_audio_hash": "",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------- GROQ CONFIGURATION ----------------

MODELS = {
    "general": "openai/gpt-oss-120b",
    "coding": "qwen/qwen3.8-27b",
}

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error(
        "NOVA cannot find GROQ_API_KEY. Add it in Streamlit Cloud "
        "under App settings → Secrets, then reboot the app."
    )
    st.stop()


# ---------------- BROWSER SPEECH ----------------

def speak_text(text):
    """Read an AI response aloud using the visitor's browser voice."""
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
        const preferredVoice = voices.find(
            voice => voice.lang === "en-US"
        );

        if (preferredVoice) {{
            utterance.voice = preferredVoice;
        }}

        window.speechSynthesis.speak(utterance);
    }}

    speakNOVA();
    </script>
    """
    components.html(voice_html, height=0)


# ---------------- MODEL SELECTION ----------------

def select_model(prompt):
    coding_keywords = [
        "python", "code", "coding", "program", "debug", "error",
        "bug", "function", "javascript", "html", "css", "sql",
        "algorithm", "streamlit", "api",
    ]

    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in coding_keywords):
        return MODELS["coding"]

    return MODELS["general"]


# ---------------- AUDIO TRANSCRIPTION ----------------

def transcribe_audio(audio_bytes):
    """Convert recorded audio into text using Groq Whisper."""
    try:
        result = client.audio.transcriptions.create(
            file=("nova_recording.wav", audio_bytes),
            model="whisper-large-v3-turbo",
            response_format="text",
        )
        transcript = str(result).strip()
        return transcript or None
    except Exception as exc:
        st.error(f"Voice transcription error: {exc}")
        return None


# ---------------- GROQ AI RESPONSE ----------------

def get_ai_response(messages, model):
    user_name = st.session_state.get("user_name") or "there"

    system_message = {
        "role": "system",
        "content": (
            "You are NOVA, a helpful and intelligent AI assistant. "
            f"The user's name is {user_name}. "
            "Address the user by their name naturally when appropriate. "
            "Give clear, accurate and useful answers. "
            "For coding questions, provide complete working code and explain "
            "where it should be placed. If unsure, say so."
        ),
    }

    clean_messages = []
    for message in messages:
        role = message.get("role")
        content = message.get("content")

        if role in ("user", "assistant") and isinstance(content, str):
            clean_messages.append({"role": role, "content": content})

    response = client.chat.completions.create(
        model=model,
        messages=[system_message] + clean_messages,
        temperature=0.7,
        max_completion_tokens=2048,
    )

    return (
        response.choices[0].message.content
        or "I couldn't generate a response."
    )


# ---------------- CUSTOM UI ----------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 10% 5%, #172b55 0%, transparent 40%),
            radial-gradient(ellipse at 90% 90%, #32194d 0%, transparent 40%),
            #080d19;
        color: #f1f5f9;
    }

    [data-testid="stSidebar"] {
        background: rgba(13, 21, 39, 0.96);
        border-right: 1px solid #26344d;
    }

    [data-testid="stSidebar"] * {
        color: #e2e8f0;
    }

    .block-container {
        padding-top: 2.5rem;
        max-width: 1050px;
    }

    .hero {
        padding: 28px;
        border: 1px solid rgba(130, 160, 255, .22);
        border-radius: 22px;
        background: linear-gradient(
            135deg,
            rgba(35, 66, 125, .42),
            rgba(91, 44, 126, .22)
        );
        margin-bottom: 25px;
    }

    .hero h1 {
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 5px;
        color: #ffffff;
    }

    .hero p {
        color: #b7c6e3;
        font-size: 14px;
    }

    div[data-testid="stChatMessage"] {
        background: rgba(25, 37, 62, .72);
        border: 1px solid rgba(130, 160, 255, .13);
        border-radius: 17px;
        padding: 15px;
        margin-bottom: 12px;
    }

    div[data-testid="stTextInput"] input {
        background: #172033;
        color: white;
        border: 1px solid #46577a;
        border-radius: 18px;
        min-height: 48px;
    }

    div[data-testid="stButton"] button,
    div[data-testid="stFormSubmitButton"] button {
        min-height: 45px;
        border-radius: 16px;
        background: linear-gradient(135deg, #6575ed, #805bdc);
        color: white;
        border: 1px solid #46577a;
        transition: all .2s ease;
    }

    div[data-testid="stButton"] button:hover,
    div[data-testid="stFormSubmitButton"] button:hover {
        border-color: #9aabff;
        transform: translateY(-1px);
        box-shadow: 0 5px 20px rgba(91, 120, 255, .25);
    }

    [data-testid="stBottom"] {
        background: transparent !important;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- USER NAME ENTRY ----------------

if not st.session_state.user_name:
    st.markdown(
        """
        <div class="hero" style="text-align:center; padding:45px 20px;">
            <h1>✦ Welcome to NOVA AI</h1>
            <p>Your personal AI assistant. Enter your name to get started.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("nova_user_entry_form"):
        entered_name = st.text_input(
            "What should NOVA call you?",
            placeholder="Enter your name...",
        )
        enter_button = st.form_submit_button(
            "Enter NOVA AI 🚀",
            use_container_width=True,
        )

    if enter_button:
        cleaned_name = entered_name.strip()
        if cleaned_name:
            st.session_state.user_name = cleaned_name
            st.session_state.welcome_played = False
            st.rerun()
        else:
            st.warning("Please enter your name.")

    st.stop()


# ---------------- PERSONALIZED WELCOME ----------------

user_name = st.session_state.user_name

if not st.session_state.welcome_played:
    safe_name = html.escape(user_name)
    st.markdown(
        f"""
        <div class="hero" style="text-align:center;">
            <h1>Welcome, {safe_name}! 👋</h1>
            <p>I'm NOVA, your personal AI assistant. I'm ready to help.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Continue to NOVA AI", use_container_width=True):
        st.session_state.welcome_played = True
        st.rerun()

    st.stop()


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown("## ✦ NOVA AI")
    st.caption("YOUR PERSONAL AI SPACE")
    st.markdown(f"### Welcome, {user_name} 👋")
    st.caption("Built by Om Hela")

    st.divider()

    st.markdown("### 🧠 AI Models")
    st.success("GPT-OSS 120B · General AI")
    st.info("Qwen · Coding AI")

    st.divider()

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_audio_hash = ""
        st.rerun()

    if st.button("✎ Change Name", use_container_width=True):
        st.session_state.user_name = ""
        st.session_state.welcome_played = False
        st.rerun()

    st.markdown("### ⚙️ System")
    st.caption("Engine: Groq")
    st.caption("Connection: Cloud API")
    st.caption("Mode: Automatic selection")

    st.divider()
    st.caption("NOVA AI · Crafted by Om Hela")


# ---------------- MAIN INTERFACE ----------------

st.markdown(
    """
    <div class="hero">
        <h1>✦ NOVA AI</h1>
        <p>Your intelligent workspace. Ask anything, create anything.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    st.markdown("### What can I help you with today?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("💡 **Learn something**")
        st.caption("Understand AI, science and technology.")

    with col2:
        st.markdown("💻 **Build something**")
        st.caption("Write, debug and understand code.")


# ---------------- CHAT HISTORY ----------------

for message_index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            if message.get("model"):
                st.caption("✦ " + message["model"])

            if st.button(
                "🔊 Listen to this response",
                key=f"speak_message_{message_index}",
            ):
                speak_text(message["content"])


# ---------------- SINGLE CHAT COMPOSER ----------------

st.markdown("### Message NOVA")

# A changing key gives each new message a fresh input field after submission.
message_input_key = f"nova_message_input_{len(st.session_state.messages)}"

col_text, col_mic, col_send = st.columns([7, 1, 1])

with col_text:
    typed_message = st.text_input(
        "Message NOVA",
        placeholder=f"Message NOVA, {user_name}...",
        label_visibility="collapsed",
        key=message_input_key,
    )

with col_mic:
    audio = mic_recorder(
        start_prompt="🎙️",
        stop_prompt="⏹️",
        just_once=True,
        use_container_width=True,
        format="wav",
        key="nova_microphone",
    )

with col_send:
    send_clicked = st.button(
        "➤",
        use_container_width=True,
        help="Send message",
    )


# ---------------- DETERMINE THE USER PROMPT ----------------

prompt = None

# Voice has priority if a new recording is returned.
if audio and audio.get("bytes"):
    audio_bytes = audio["bytes"]
    audio_hash = hashlib.sha256(audio_bytes).hexdigest()

    # Prevent the same recording from being transcribed again on reruns.
    if audio_hash != st.session_state.last_audio_hash:
        st.session_state.last_audio_hash = audio_hash

        with st.spinner("NOVA is transcribing your voice..."):
            prompt = transcribe_audio(audio_bytes)

        if prompt:
            st.caption(f"🎙️ You said: {prompt}")

elif send_clicked:
    if typed_message and typed_message.strip():
        prompt = typed_message.strip()
    else:
        st.warning("Type a message or record your voice first.")


# ---------------- SEND TO NOVA ----------------

if prompt:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    selected_model = select_model(prompt)

    try:
        with st.spinner("✦ NOVA is thinking..."):
            answer = get_ai_response(
                st.session_state.messages,
                selected_model,
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "model": selected_model,
            }
        )

        st.rerun()

    except Exception as exc:
        st.error(f"NOVA error: {exc}")
        st.info(
            "Your message has been kept in the chat. Check the model name, "
            "Groq API access, and your Streamlit Secrets before retrying."
        )
