import streamlit as st
from streamlit_mic_recorder import speech_to_text

try:
    import google.generativeai as genai
except ImportError:
    st.error("❌ Instala: pip install google-generativeai")
    st.stop()

# ===== Configuración general =====
st.set_page_config(page_title="Chatbot con Gemini", page_icon="🤖")
st.title("🎙️ Chatbot con Gemini (voz + texto)")

# 🔐 Clave API embebida (reemplaza con tu clave real)
API_KEY = "AIzaSyAzpQw6qxWMmXx_XMIMv3OABU5ZMvPzfUw"  # ⚠️ No la subas a repos públicos

# Configurar Gemini
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
except Exception as e:
    st.error(f"No se pudo configurar Gemini: {e}")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("Opciones")
    if st.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.rerun()

# Historial
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar chat previo
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 🎤 Input por voz
voice_input = speech_to_text(
    language='es',  # idioma español
    start_prompt="🎙️ Presiona para hablar",
    stop_prompt="🛑 Detener",
    use_container_width=True,
    key="mic"
)

# ✍️ Input por texto (opcional)
text_input = st.chat_input("Escribe aquí...")

# Unificar entrada (voz o texto)
user_input = voice_input or text_input

# Procesar si hay input
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("⏳"):
            try:
                response = model.generate_content(user_input)
                text = getattr(response, "text", "").strip() or "No recibí texto de respuesta."
                st.markdown(text)
                st.session_state.messages.append({"role": "assistant", "content": text})
            except Exception as e:
                st.error(f"Error: {e}")
