import streamlit as st
from streamlit_mic_recorder import mic_recorder

try:
    import google.generativeai as genai
except ImportError:
    st.error("❌ Instala: pip install google-generativeai")
    st.stop()

st.set_page_config(page_title="Chatbot con Gemini", page_icon="🤖")
st.title("🎙️ Chatbot con Gemini (voz + texto)")

API_KEY = "TU_API_KEY_AQUI"  # ⚠️ no subas esto público

# ---- Configuración API (forzamos v1, que es la estable) ----
genai.configure(api_key=API_KEY)  # con >=0.7.x queda en v1

# Modelos: primero intentamos 2.0 (multimodal) y luego 1.5-8b
CHAT_MODEL_CANDIDATES = ["gemini-2.0-flash-lite", "gemini-2.0-flash"]
STT_MODEL_CANDIDATES  = ["gemini-2.0-flash", "gemini-1.5-flash-8b"]

def pick_first_available(candidates):
    for m in candidates:
        try:
            _ = genai.GenerativeModel(m)
            return m
        except Exception:
            continue
    return None

chat_model_name = pick_first_available(CHAT_MODEL_CANDIDATES) or "gemini-2.0-flash-lite"
stt_model_name  = pick_first_available(STT_MODEL_CANDIDATES)  or "gemini-1.5-flash-8b"

model_chat = genai.GenerativeModel(chat_model_name)
model_stt  = genai.GenerativeModel(stt_model_name)

with st.sidebar:
    st.header("Opciones")
    if st.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.rerun()
    st.caption(f"💬 Modelo chat: {chat_model_name}")
    st.caption(f"📝 Modelo STT: {stt_model_name}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

def transcribe_with_gemini(audio_bytes: bytes, mime: str) -> str:
    """
    Transcribe audio en español con el modelo seleccionado.
    Acepta audio/webm, audio/ogg, audio/wav (según lo que devuelva el navegador).
    """
    try:
        parts = [
            {"mime_type": mime, "data": audio_bytes},
            {"text": "Transcribe al español. Devuelve solo la transcripción, sin comillas."}
        ]
        resp = model_stt.generate_content(parts)
        return (getattr(resp, "text", "") or "").strip()
    except Exception as e:
        st.error(f"Error al transcribir audio: {e}")
        return ""

st.subheader("Habla con el bot")
audio = mic_recorder(
    start_prompt="🎙️ Presiona para hablar",
    stop_prompt="🛑 Detener",
    use_container_width=True,
    format="webm",   # en Chrome/Firefox suele ser webm/ogg; cámbialo a "wav" si lo prefieres
    key="mic_rec"
)

voice_text = None
if audio and "bytes" in audio:
    # Detección simple de MIME por extensión elegida
    mime = "audio/webm"
    st.audio(audio["bytes"], format=mime)
    with st.spinner("📝 Transcribiendo..."):
        voice_text = transcribe_with_gemini(audio["bytes"], mime=mime)
        if voice_text:
            st.success("✅ Transcripción lista")
            st.write(f"**Tú dijiste:** {voice_text}")

text_input = st.chat_input("Escribe aquí...")
user_input = voice_text or text_input

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("⏳"):
            try:
                resp = model_chat.generate_content(user_input)
                text = (getattr(resp, "text", "") or "").strip() or "No recibí texto de respuesta."
                st.markdown(text)
                st.session_state.messages.append({"role": "assistant", "content": text})
            except Exception as e:
                st.error(f"Error: {e}")
