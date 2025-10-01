import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import base64

# ================== Configuración general ==================
st.set_page_config(page_title="🧸 Peluche IA", page_icon="🧸")
st.title("🧸 Tu Amigo Virtual de Compañía")

# 🔐 Clave API
API_KEY = "AIzaSyAzpQw6qxWMmXx_XMIMv3OABU5ZMvPzfUw"

# Configurar Gemini
try:
    genai.configure(api_key=API_KEY)
    model_chat = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error(f"No se pudo configurar Gemini: {e}")
    st.stop()

# ===== Nombre del niño =====
if "child_name" not in st.session_state:
    st.session_state.child_name = ""

st.session_state.child_name = st.text_input("👦💬 Escribe tu nombre para que el peluche te llame por él:", 
                                            value=st.session_state.child_name)

if not st.session_state.child_name.strip():
    st.info("Por favor escribe tu nombre arriba para comenzar 🧸")
    st.stop()

# ===== Historial =====
if "messages" not in st.session_state:
    # Instrucción inicial al modelo
    st.session_state.messages = [{
        "role": "system",
        "content": (
            f"Eres un peluche virtual llamado Osito Amigo. "
            f"Tu misión es acompañar, escuchar y dar apoyo emocional a niños. "
            f"Habla con ternura, sencillez y comprensión, como un amigo peluche. "
            f"Siempre llama al niño por su nombre: {st.session_state.child_name}. "
            f"Usa frases cortas, sin usar negritas, asteriscos ni símbolos extra. "
            f"Tu objetivo es que el niño se sienta comprendido y acompañado."
        )
    }]

for m in st.session_state.messages:
    if m["role"] != "system":  # no mostrar instrucciones ocultas
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# ===== Entrada de texto =====
user_input = st.chat_input(f"Escribe aquí lo que quieras contarme, {st.session_state.child_name}...")

# ===== Procesar conversación =====
if user_input:
    # Mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Respuesta del peluche IA
    with st.chat_message("assistant"):
        with st.spinner("⏳ Pensando..."):
            try:
                # Pasamos TODO el historial al modelo para coherencia
                prompt = [ {"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages ]
                resp = model_chat.generate_content(prompt)
                answer = (getattr(resp, "text", "") or "").strip() or "No entendí bien, ¿me cuentas otra vez?"

                # Guardar y mostrar
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.markdown(answer)

                # Convertir a voz automáticamente
                tts = gTTS(answer, lang="es")
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes = audio_bytes.getvalue()

                b64 = base64.b64encode(audio_bytes).decode()
                audio_html = f"""
                    <audio autoplay="true">
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {e}")
