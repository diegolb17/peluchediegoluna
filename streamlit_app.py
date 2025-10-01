import streamlit as st
from streamlit_mic_recorder import mic_recorder  # ✅ estable en todos los navegadores

try:
    import google.generativeai as genai
except ImportError:
    st.error("❌ Instala: pip install google-generativeai")
    st.stop()

# ===== Configuración general =====
st.set_page_config(page_title="Chatbot con Gemini", page_icon="🤖")
st.title("🎙️ Chatbot con Gemini (voz + texto)")

# 🔐 API Key (recomendado: úsala desde secrets en deploy)
API_KEY = "AIzaSyAzpQw6qxWMmXx_XMIMv3OABU5ZMvPzfUw"

# Configurar Gemini (usa 1.5 para transcribir audio)
try:
    genai.configure(api_key=API_KEY)
    model_chat = genai.GenerativeModel("gemini-2.0-flash-lite")   # para responder
    model_stt  = genai.GenerativeModel("gemini-1.5-flash")        # para transcribir audio
except Exception as e:
    st.error(f"No se pudo configurar Gemini: {e}")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("Opciones")
    if st.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.rerun()
    st.caption("🎤 Grabación: mic_recorder (compatible con Firefox/Chrome)")

# Historial
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ===== Helpers =====
def transcribe_with_gemini(audio_bytes: bytes, mime: str = "audio/webm") -> str:
    """
    Envía audio a Gemini 1.5 para obtener texto (español).
    """
    try:
        parts = [
            {"mime_type": mime, "data": audio_bytes},
            {"text": "Transcribe el audio al español. Devuelve solo el texto transcrito, sin comillas."}
        ]
        resp = model_stt.generate_content(parts)
        text = getattr(resp, "text", "").strip()
        return text
    except Exception as e:
        st.error(f"Error al transcribir audio: {e}")
        return ""

# ===== Entrada por voz (robusta) =====
st.subheader("Habla con el bot")
audio = mic_recorder(
    start_prompt="🎙️ Presiona para hablar",
    stop_prompt="🛑 Detener",
    use_container_width=True,
    format="webm",          # devuelve audio/webm como bytes
    key="mic_rec"
)

voice_text = None
if audio and "bytes" in audio:
    st.audio(audio["bytes"], format="audio/webm")
    with st.spinner("📝 Transcribiendo..."):
        voice_text = transcribe_with_gemini(audio["bytes"], mime="audio/webm")
        if voice_text:
            st.success("✅ Transcripción lista")
            st.write(f"**Tú dijiste:** {voice_text}")

# ===== Entrada por texto (opcional)
text_input = st.chat_input("Escribe aquí...")

# Unificar entrada
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
                text = getattr(resp, "text", "").strip() or "No recibí texto de respuesta."
                st.markdown(text)
                st.session_state.messages.append({"role": "assistant", "content": text})
            except Exception as e:
                st.error(f"Error: {e}")
