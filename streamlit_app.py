import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import base64

# ================== Configuración general ==================
st.set_page_config(page_title="Chatbot con Gemini", page_icon="🤖")
st.title("🤖 Chatbot con Gemini (texto + voz automático)")

# 🔐 Clave API
API_KEY = "AIzaSyAzpQw6qxWMmXx_XMIMv3OABU5ZMvPzfUw"

# Configurar Gemini
try:
    genai.configure(api_key=API_KEY)
    model_chat = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error(f"No se pudo configurar Gemini: {e}")
    st.stop()

# ===== Historial =====
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ===== Entrada de texto =====
user_input = st.chat_input("Escribe aquí tu mensaje...")

# ===== Procesar conversación =====
if user_input:
    # Mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Respuesta del bot
    with st.chat_message("assistant"):
        with st.spinner("⏳"):
            try:
                resp = model_chat.generate_content(user_input)
                answer = (getattr(resp, "text", "") or "").strip() or "No recibí texto de respuesta."

                # Mostrar texto
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

                # Convertir a voz
                tts = gTTS(answer, lang="es")
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes = audio_bytes.getvalue()

                # Codificar en base64 para incrustar en HTML
                b64 = base64.b64encode(audio_bytes).decode()
                audio_html = f"""
                    <audio autoplay="true">
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {e}")
