import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io

# ================== Configuración general ==================
st.set_page_config(page_title="Chatbot con Gemini", page_icon="🤖")
st.title("🤖 Chatbot con Gemini (texto + voz)")

# 🔐 Clave API (⚠️ no la subas a repos públicos)
API_KEY = "AIzaSyAzpQw6qxWMmXx_XMIMv3OABU5ZMvPzfUw"

# Configurar Gemini
try:
    genai.configure(api_key=API_KEY)
    model_chat = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error(f"No se pudo configurar Gemini: {e}")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("Opciones")
    if st.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.rerun()
    st.caption("🔐 API cargada")
    st.caption("🤖 Modelo: gemini-2.0-flash")
    st.caption("🔊 Salida con voz activada")

# Historial de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        # Reproducir voz para las respuestas del bot
        if m["role"] == "assistant":
            try:
                tts = gTTS(m["content"], lang="es")
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                st.audio(audio_bytes.getvalue(), format="audio/mp3")
            except Exception as e:
                st.error(f"Error en TTS: {e}")

# ===== Entrada de texto =====
user_input = st.chat_input("Escribe aquí tu mensaje...")

# ===== Procesar conversación =====
if user_input:
    # Mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Respuesta del modelo
    with st.chat_message("assistant"):
        with st.spinner("⏳"):
            try:
                resp = model_chat.generate_content(user_input)
                answer = (getattr(resp, "text", "") or "").strip() or "No recibí texto de respuesta."
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

                # Convertir respuesta a voz
                tts = gTTS(answer, lang="es")
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                st.audio(audio_bytes.getvalue(), format="audio/mp3")

            except Exception as e:
                st.error(f"Error: {e}")
