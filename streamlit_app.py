import streamlit as st
from streamlit_mic_recorder import mic_recorder
import google.generativeai as genai

# ================== Configuración general ==================
st.set_page_config(page_title="Chatbot con Gemini", page_icon="🤖")
st.title("🎙️ Chatbot con Gemini (voz + texto)")

# 🔐 Clave API (¡no la subas a un repo público!)
API_KEY = "AIzaSyAzpQw6qxWMmXx_XMIMv3OABU5ZMvPzfUw"

# Configurar Gemini
try:
    genai.configure(api_key=API_KEY)
    model_chat = genai.GenerativeModel("gemini-2.0-flash")  # para responder
    model_stt = genai.GenerativeModel("gemini-2.0-flash")   # para transcribir audio
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

# Historial de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ===== Función para transcripción =====
def transcribe_with_gemini(audio_bytes: bytes, mime: str = "audio/webm") -> str:
    try:
        parts = [
            {"mime_type": mime, "data": audio_bytes},
            {"text": "Transcribe el audio al español. Devuelve solo el texto transcrito, sin comillas."}
        ]
        resp = model_stt.generate_content(parts)
        return (getattr(resp, "text", "") or "").strip()
    except Exception as e:
        st.error(f"Error al transcribir audio: {e}")
        return ""

# ===== Entrada por voz =====
st.subheader("Habla con el bot")
audio = mic_recorder(
    start_prompt="🎙️ Presiona para hablar",
    stop_prompt="🛑 Detener",
    use_container_width=True,
    format="webm",   # formato estándar
    key="mic_rec"
)

voice_text = None
if audio and "bytes" in audio:
    st.audio(audio["bytes"], format="audio/webm")
    with st.spinner("📝 Transcribiendo..."):
        voice_text = transcribe_with_gemini(audio["bytes"], "audio/webm")
        if voice_text:
            st.success("✅ Transcripción lista")
            st.write(f"**Tú dijiste:** {voice_text}")

# ===== Entrada por texto =====
text_input = st.chat_input("Escribe aquí...")
user_input = voice_text or text_input

# ===== Procesar conversación =====
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("⏳"):
            try:
                resp = model_chat.generate_content(user_input)
                answer = (getattr(resp, "text", "") or "").strip() or "No recibí texto de respuesta."
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Error: {e}")
