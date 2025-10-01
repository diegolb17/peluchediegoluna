import os
import streamlit as st
from streamlit_mic_recorder import mic_recorder, speech_to_text

import google.generativeai as genai

st.set_page_config(page_title="Chatbot con Gemini", page_icon="🤖")
st.title("🎙️ Chatbot con Gemini (voz + texto)")

API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

chat_model_name = "gemini-2.0-flash-lite"
stt_model_name  = "gemini-2.0-flash"  # admite audio en v1

model_chat = None
model_stt  = None
api_ok = False
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model_chat = genai.GenerativeModel(chat_model_name)
        model_stt  = genai.GenerativeModel(stt_model_name)
        api_ok = True
    except Exception as e:
        st.warning(f"⚠️ La clave no funcionó: {e}")

with st.sidebar:
    st.header("Opciones")
    if st.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.rerun()
    st.caption("🔐 API: " + ("OK" if api_ok else "no disponible"))
    st.caption("🎤 Modo voz: " + ("Gemini STT" if api_ok else "Web Speech (navegador)"))

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

def transcribe_gemini(audio_bytes: bytes, mime: str = "audio/webm") -> str:
    parts = [
        {"mime_type": mime, "data": audio_bytes},
        {"text": "Transcribe el audio al español. Devuelve solo el texto, sin comillas."}
    ]
    resp = model_stt.generate_content(parts)
    return (getattr(resp, "text", "") or "").strip()

st.subheader("Habla con el bot")

voice_text = None
if api_ok:
    # Graba siempre (independiente del navegador) y transcribe en servidor
    audio = mic_recorder(
        start_prompt="🎙️ Presiona para hablar",
        stop_prompt="🛑 Detener",
        use_container_width=True,
        format="webm",
        key="mic_rec",
    )
    if audio and "bytes" in audio:
        st.audio(audio["bytes"], format="audio/webm")
        with st.spinner("📝 Transcribiendo..."):
            try:
                voice_text = transcribe_gemini(audio["bytes"], "audio/webm")
                if voice_text:
                    st.success("✅ Transcripción lista")
                    st.write(f"**Tú dijiste:** {voice_text}")
            except Exception as e:
                st.error(f"Error al transcribir audio: {e}")
else:
    # Sin API key válida: usa STT del navegador (Chrome/Edge)
    st.info("Usando reconocimiento de voz del navegador (mejor en Chrome/Edge).")
    voice_text = speech_to_text(
        language="es",
        start_prompt="🎙️ Presiona para hablar",
        stop_prompt="🛑 Detener",
        use_container_width=True,
        key="mic_browser",
    )

text_input = st.chat_input("Escribe aquí...")
user_input = voice_text or text_input

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            if api_ok and model_chat:
                resp = model_chat.generate_content(user_input)
                answer = (getattr(resp, "text", "") or "").strip() or "No recibí texto de respuesta."
            else:
                # Respuesta local mínima si no hay API (para no romper UX)
                answer = "Necesito una API key válida para responder con Gemini. Ve a la barra lateral."
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Error: {e}")
