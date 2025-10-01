import streamlit as st

try:
    import google.generativeai as genai
except ImportError:
    st.error("❌ Instala: pip install google-generativeai")
    st.stop()

# ===== Configuración general =====
st.set_page_config(page_title="Chatbot con Gemini", page_icon="🤖")
st.title("🤖 Chatbot con Google Gemini")

# 🔐 Clave API embebida (reemplaza el texto por tu clave real)
API_KEY = "AIzaSyAzpQw6qxWMmXx_XMIMv3OABU5ZMvPzfUw"  # ⚠️ Evita subir esta clave a repos públicos

# Configurar Gemini
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
except Exception as e:
    st.error(f"No se pudo configurar Gemini: {e}")
    st.stop()

# Sidebar (sin pedir API)
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

# Input del usuario
if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("⏳"):
            try:
                response = model.generate_content(prompt)
                text = getattr(response, "text", "").strip() or "No recibí texto de respuesta."
                st.markdown(text)
                st.session_state.messages.append({"role": "assistant", "content": text})
            except Exception as e:
                st.error(f"Error: {e}")
