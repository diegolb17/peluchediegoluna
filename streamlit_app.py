import streamlit as st
try:
    import google.generativeai as genai
    import speech_recognition as sr
    from audiorecorder import audiorecorder
except ImportError as e:
    st.error(f"❌ Instala las dependencias necesarias: pip install google-generativeai streamlit-audiorecorder speechrecognition")
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

# Input por texto
prompt = st.chat_input("Escribe aquí...")

# Input por micrófono
st.write("🎙️ O graba tu mensaje:")
audio = audiorecorder("Grabar", "Detener grabación")

# Procesar entrada de audio
if audio:
    with st.spinner("🔊 Transcribiendo audio..."):
        try:
            # Guardar el audio en un archivo temporal
            with open("temp_audio.wav", "wb") as f:
                f.write(audio.tobytes())

            # Usar speech_recognition para transcribir
            recognizer = sr.Recognizer()
            with sr.AudioFile("temp_audio.wav") as source:
                audio_data = recognizer.record(source)
                try:
                    # Transcribir usando Google Speech Recognition (requiere internet)
                    prompt = recognizer.recognize_google(audio_data, language="es-ES")
                    st.success("✅ Transcripción: " + prompt)
                except sr.UnknownValueError:
                    st.error("No se pudo entender el audio. Intenta de nuevo.")
                    prompt = None
                except sr.RequestError as e:
                    st.error(f"Error en la transcripción: {e}")
                    prompt = None
        except Exception as e:
            st.error(f"Error al procesar el audio: {e}")
            prompt = None

# Procesar el prompt (ya sea de texto o audio)
if prompt:
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
