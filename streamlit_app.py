import streamlit as st
from streamlit_mic_recorder import mic_recorder
import google.generativeai as genai
import hashlib

# ================== Configuración general ==================
st.set_page_config(page_title="Chatbot con Gemini", page_icon="🤖")
st.title("🎙️ Chatbot con Gemini (voz + texto)")

# 🔐 Clave API (tú pediste dejarla fija aquí)
API_KEY = "AIzaSyAzpQw6qxWMmXx_XMIMv3OABU5ZMvPzfUw"

# Configurar Gemini
try:
    genai.configure(api_key=API_KEY)
    model_chat = genai.GenerativeModel("gemini-2.0-flash")  # para responder
    model_stt  = genai.GenerativeModel("gemini-2.0-flash")  # para transcribir audio
except Exception as e:
    st.error(f"No se pudo configurar Gemini: {e}")
    st.stop()

# ===== Estado =====
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_audio" not in st.session_state:
    st.session_state.pending_audio = None
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None
if "processing" not in st.session_state:
    st.session_state.processing = False

# ===== Sidebar =====
with st.sidebar:
    st.header("Opciones")
    if st.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.session_state.pending_audio = None
        st.session_state.last_audio_hash = None
        st.rerun()
    st.caption("🔐 API cargada")
    st.caption("🤖 Modelo: gemini-2.0-flash")

# ===== Mostrar historial =====
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ===== Helpers =====
def bhash(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()  # suficiente para detectar repetidos

def transcribe_with_gemini(audio_bytes: bytes, mime: str = "audio/webm") -> str:
    parts = [
        {"mime_type": mime, "data": audio_bytes},
        {"text": "Transcribe el audio al español. Devuelve solo el texto transcrito, sin comillas."}
    ]
    resp = model_stt.generate_content(parts)
    return (getattr(resp, "text", "") or "").strip()

def append_and_answer(user_text: str):
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)
    with st.chat_message("assistant"):
        with st.spinner("⏳"):
            resp = model_chat.generate_content(user_text)
            answer = (getattr(resp, "text", "") or "").strip() or "No recibí texto de respuesta."
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

# ===== Entrada por voz (robusta, ciclada) =====
st.subheader("Habla con el bot")

# 1) Captura cruda (no procesa aún)
raw_audio = mic_recorder(
    start_prompt="🎙️ Presiona para hablar",
    stop_prompt="🛑 Detener",
    use_container_width=True,
    format="webm",
    key="mic_rec",  # clave fija; controlamos el ciclo via session_state
)

# 2) Si llegó audio nuevo, guárdalo en la bandeja
if raw_audio and "bytes" in raw_audio:
    new_hash = bhash(raw_audio["bytes"])
    if new_hash != st.session_state.last_audio_hash:
        st.session_state.pending_audio = {"bytes": raw_audio["bytes"], "mime": "audio/webm", "hash": new_hash}
    # si es el mismo hash, no hacemos nada (evita re-procesar en cada rerun)

# 3) Si hay audio pendiente, mostrarlo y dar botón para procesar o descartar
if st.session_state.pending_audio and not st.session_state.processing:
    st.audio(st.session_state.pending_audio["bytes"], format="audio/webm")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Transcribir", key="btn_transcribe"):
            st.session_state.processing = True
            st.rerun()
    with col2:
        if st.button("🗑️ Descartar", key="btn_discard"):
            st.session_state.pending_audio = None
            st.rerun()

# 4) Proceso de transcripción (en una pasada aislada)
voice_text = None
if st.session_state.processing and st.session_state.pending_audio:
    with st.spinner("📝 Transcribiendo..."):
        try:
            pa = st.session_state.pending_audio
            voice_text = transcribe_with_gemini(pa["bytes"], pa["mime"])
            if voice_text:
                st.success("✅ Transcripción lista")
                st.write(f"**Tú dijiste:** {voice_text}")
                # marcar como procesado para no reusar el mismo
                st.session_state.last_audio_hash = pa["hash"]
                # limpiar bandeja y estado de proceso
                st.session_state.pending_audio = None
        except Exception as e:
            st.error(f"Error al transcribir audio: {e}")
        finally:
            st.session_state.processing = False
            st.rerun()  # 🔁 deja el widget listo para la siguiente toma

# ===== Entrada por texto =====
text_input = st.chat_input("Escribe aquí...")

# ===== Unificar entrada =====
user_input = voice_text or text_input

# ===== Procesar conversación =====
if user_input:
    append_and_answer(user_input)
