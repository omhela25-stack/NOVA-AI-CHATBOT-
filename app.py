        "Browsers may block sound until you interact with the page."
    )
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
    st.info("Qwen 3 · Coding AI")

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
    st.caption("Engine: Groq")
    st.caption("Connection: Cloud API")
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

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant" and message.get("model"):
            st.caption("✦ " + message["model"])

if st.session_state.messages:
    last_answer = next(
        (
            message["content"]
            for message in reversed(st.session_state.messages)
            if message["role"] == "assistant"
        ),
        None
    )

    if last_answer and st.button("🔊 Replay Last Response"):
        speak_text(last_answer)


# ---------------- USER INPUT ----------------

prompt = st.chat_input(f"Message NOVA, {user_name}...")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    selected_model = select_model(prompt)

    with st.chat_message("assistant"):
        with st.spinner("✦ NOVA is thinking..."):
            try:
                answer = get_ai_response(
                    st.session_state.messages,
                    selected_model
                )

                st.markdown(answer)
                st.caption("✦ Powered by " + selected_model)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "model": selected_model
                })

                if voice_enabled:
                    speak_text(answer)

            except Exception as exc:
                st.error(f"Groq AI connection error: {exc}")
