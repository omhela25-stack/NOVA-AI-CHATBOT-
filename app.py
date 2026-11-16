import streamlit as st
from groq import Groq
import streamlit.components.v1 as components
import json

def speak_text(text):
    safe_text = json.dumps(text)

    voice_html = f"""
    <script>
    const text = {safe_text};

    function speak() {{
        const speech = new SpeechSynthesisUtterance(text);

        speech.lang = "en-US";
        speech.rate = 1.0;
        speech.pitch = 1.0;
        speech.volume = 1.0;

        const voices = window.speechSynthesis.getVoices();

        const preferredVoice = voices.find(
            voice => voice.lang === "en-US"
        );

        if (preferredVoice) {{
            speech.voice = preferredVoice;
        }}

        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(speech);
    }}

    if (window.speechSynthesis.getVoices().length > 0) {{
        speak();
    }} else {{
        window.speechSynthesis.onvoiceschanged = speak;
    }}
    </script>
    """

    components.html(voice_html, height=0)


st.set_page_config(
    page_title="NOVA AI",
    page_icon="✦",
    layout="wide"
)


MODELS = {
    "general": "openai/gpt-oss-120b",
    "coding": "qwen/qwen3.8-27b"
}


client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)
# ---------------- CUSTOM UI ----------------

st.markdown("""
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

[data-testid="stChatInput"] {
    background: rgba(15, 25, 45, 0.96) !important;
    border: 1px solid #46577a !important;
    border-radius: 22px !important;
    padding: 8px 12px !important;
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
    backdrop-filter: blur(18px);
}

[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] textarea:focus {
    outline: none !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] button {
    background: linear-gradient(135deg,#6575ed,#9864e8) !important;
    color: white !important;
    border-radius: 14px !important;
}

[data-testid="stBottom"] {
    background: transparent !important;
}
}

.stButton button {
    border-radius: 12px;
    border: 1px solid #34496f;
    background: linear-gradient(135deg, #263e72, #50347f);
    color: white;
    transition: all .2s ease;
}

.stButton button:hover {
    border-color: #9aabff;
    transform: translateY(-2px);
    box-shadow: 0 5px 20px rgba(91, 120, 255, .25);
}

div[data-testid="stStatusWidget"] {
    background: #14213a;
}

#MainMenu, footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent;
}
</style>
""", unsafe_allow_html=True)


# ---------------- MODEL SELECTION ----------------

def select_model(prompt):
    coding_keywords = [
        "python", "code", "coding", "program",
        "debug", "error", "bug", "function",
        "javascript", "html", "css", "sql",
        "algorithm", "streamlit", "api"
    ]

    if any(word in prompt.lower() for word in coding_keywords):
        return MODELS["coding"]

    return MODELS["general"]

prompt = st.chat_input(f"Message NOVA, {st.session_state.user_name}...")
# ---------------- OLLAMA CONNECTION ----------------


def get_ai_response(messages, model):

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_completion_tokens=2048
    )

    return response.choices[0].message.content


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown("## ✦ NOVA AI")
    st.caption("YOUR PERSONAL AI SPACE")
    st.markdown("### Welcome, Om 👋")
    st.caption("Built by Om Hela")

    st.divider()

    st.markdown("### 🧠 AI Models")
    st.success("Llama 3.2 · General AI")
    st.info("Qwen 2.5 · Coding AI")

    st.divider()

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.markdown("### 🔊 Voice Settings")

    voice_enabled = st.toggle(
        "Speak AI responses",
        value=True
    )

    st.caption("Automatic voice output")

    st.markdown("### ⚙️ System")
    st.caption("Engine: Ollama")
    st.caption("Connection: Localhost")
    st.caption("Mode: Automatic selection")

    st.divider()
    st.caption("NOVA AI · Crafted by Om Hela")


# ---------------- MAIN INTERFACE ----------------

st.markdown("""
<div class="hero">
    <h1>✦ NOVA AI</h1>
    <p>Your intelligent workspace. Ask anything, create anything.</p>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown("### What can I help you with today?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("💡 **Learn something**")
        st.caption("Understand AI, science and technology.")

    with col2:
        st.markdown("💻 **Build something**")
        st.caption("Write, debug and understand code.")


# ---------------- WELCOME SCREEN ----------------


# ---------------- USER ENTRY & PERSONAL WELCOME ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "welcome_played" not in st.session_state:
    st.session_state.welcome_played = False


# Ask for the user's name before entering NOVA
if not st.session_state.user_name:

    st.markdown("""
    <div style="text-align:center; padding:45px 15px;">
        <h1 style="color:white;">Welcome to NOVA AI ✨</h1>
        <p style="color:#cbd5e1;">
            Your personal AI assistant is waiting for you.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("user_entry_form"):
        entered_name = st.text_input(
            "What should NOVA call you?",
            placeholder="Enter your name..."
        )

        enter_button = st.form_submit_button(
            "Enter NOVA AI 🚀",
            use_container_width=True
        )

        if enter_button:
            if entered_name.strip():
                st.session_state.user_name = entered_name.strip()
                st.rerun()
            else:
                st.warning("Please enter your name.")

    st.stop()


# Personalized welcome after entering
user_name = st.session_state.user_name

welcome_text = (
    f"Welcome to NOVA AI, {user_name}! "
    "I'm your personal AI assistant. "
    "How can I help you today?"
)

if not st.session_state.welcome_played:
    st.markdown(f"""
    <div style="
        text-align:center;
        padding:35px 15px;
        border-radius:20px;
        background:linear-gradient(135deg,#111827,#312e81);
        margin-bottom:20px;
    ">
        <h1 style="color:white;">Welcome, {user_name}! 👋</h1>
        <p style="color:#cbd5e1;">
            I'm NOVA. Your personal AI assistant is ready.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔊 Hear Your Welcome", use_container_width=True):
        speak_text(welcome_text)
        st.session_state.welcome_played = True
        st.rerun()


    
# ---------------- CHAT HISTORY ----------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Replay last AI response
last_answer = next(
    (
        message["content"]
        for message in reversed(st.session_state.messages)
        if message["role"] == "assistant"
    ),
    None
)

if last_answer:
    if st.button("🔊 Replay Last Response"):
        speak_text(last_answer)




# ---------------- USER INPUT ----------------

prompt = st.chat_input("Message NOVA AI...")

if prompt:

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Automatically select AI model
    selected_model = select_model(prompt)

    # Generate AI response
    with st.chat_message("assistant"):

        with st.spinner("✦ NOVA is thinking..."):

     
            try:
                # Prepare clean conversation history
                user_name = st.session_state.get("user_name", "there")

                ai_messages = [
                    {
                        "role": "system",
                        "content": (
                            f"You are NOVA, a helpful and intelligent AI assistant. "
                            f"The user's name is {user_name}. "
                            "Address the user by their name naturally when appropriate. "
                            "Give clear and accurate answers."
                        )
                    }
                ]

                # Only send role and content to Groq
                for message in st.session_state.messages:
                    if message.get("role") in ["user", "assistant"]:
                        ai_messages.append({
                            "role": message["role"],
                            "content": message["content"]
                        })

                # Get response from Groq
                answer = get_ai_response(ai_messages, selected_model)

                st.markdown(answer)

                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

                st.caption("✦ Powered by " + selected_model)

                if voice_enabled:
                    speak_text(answer)

            except Exception as e:
                st.error(f"AI connection error: {e}")

        # Keep only valid Groq message fields
        clean_messages = [
            {
                "role": message["role"],
                "content": message["content"]
            }
            for message in messages
            if message.get("role") in ["user", "assistant"]
            and isinstance(message.get("content"), str)
        ]

        response = client.chat.completions.create(
            model=model,
            messages=[system_message] + clean_messages,
            temperature=0.7,
            max_completion_tokens=2048
        )

        return response.choices[0].message.content

  except Exception as e:
        return f"NOVA encountered an error: {str(e)}"


                # Display AI response
                st.markdown(answer)

                st.caption("✦ Powered by " + selected_model)

                # Save clean assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

                # Speak AI response if voice is enabled
                if voice_enabled:
                    speak_text(answer)

            except Exception as e:

                st.error(
                    f"AI connection error: {e}"
                )

