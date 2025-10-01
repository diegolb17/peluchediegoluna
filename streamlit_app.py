import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io, base64
from pydub import AudioSegment

# ================== Configuración general ==================
st.set_page_config(page_title="🧸 Peluche IA", page_icon="🧸", layout="wide")  # Cambié a 'wide' para mejor espacio al peluche

# Custom CSS for a minimalist, child-friendly design
# Custom CSS for a minimalist, child-friendly design
# Custom CSS for a minimalist, child-friendly design
st.markdown("""
<style>
    body {
        background: linear-gradient(135deg, #FFFFFF 0%, #FFFDF7 100%);
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }
    .main {
        background-color: #FFFFFF;
        border-radius: 25px;
        padding: 25px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.05);
        max-width: 900px;
        margin: auto;
    }
    h1 {
        color: #FF9999;
        text-align: center;
        font-size: 2.8em;
        margin-bottom: 15px;
        text-shadow: 2px 2px 4px rgba(255, 153, 153, 0.25);
    }
    .stTextInput > div > div > input {
        background-color: #F9FBFF;
        border: 3px solid #CDE9FF;
        border-radius: 20px;
        padding: 12px;
        font-size: 1.3em;
        color: #333;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.03);
    }
    .stTextInput > div > div > input:focus {
        border-color: #FFB6C1;
        box-shadow: 0 0 8px rgba(255, 182, 193, 0.5);
    }
    .stChatInput {
        background-color: #FFFDF7;
        border: 3px solid #FFEFD5;
        border-radius: 20px;
        padding: 12px;
        margin-top: 10px;
    }
    .stChatMessage {
        border-radius: 20px;
        margin: 12px 0;
        padding: 18px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }
    .stChatMessage[data-testid="user"] {
        background-color: #F0FAFF;
        border: 2px solid #CDE9FF;
    }
    .stChatMessage[data-testid="assistant"] {
        background-color: #FFF9F0;
        border: 2px solid #FFEFD5;
    }
    .stSpinner > div > div {
        color: #FF9999;
        font-size: 1.2em;
    }
    .stInfo {
        background-color: #F0FFF0;
        border: 2px solid #B5E3B5;
        border-radius: 15px;
        padding: 15px;
        color: #2E8B57;
    }
    .stError {
        background-color: #FFF0F0;
        border: 2px solid #FFB6C1;
        border-radius: 15px;
        padding: 15px;
        color: #8B0000;
    }
    .teddy-container {
        text-align: center;
        margin: 20px 0;
    }
    .teddy-image {
        max-width: 250px;
        height: auto;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        animation: bounce 2s infinite ease-in-out;
    }
    @keyframes bounce {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-12px) rotate(1deg); }
    }
    .stSidebar {
        background-color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)



# Crear columnas para layout: peluche a la izquierda, chat a la derecha
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="teddy-container">', unsafe_allow_html=True)
    # Imagen del peluche gigante (URL estable y gratuita)
    st.image("https://www.freeiconspng.com/thumbs/teddy-bear-png/teddy-bear-png-0.png", 
             caption="¡Hola! Soy tu Peluche IA 🧸", 
             use_column_width=True, 
             output_format="PNG")
    st.markdown('</div>', unsafe_allow_html=True)
    # Agregar un mensaje juguetón debajo del peluche
    st.markdown("**¡Estoy aquí para escucharte y jugar contigo!** 💕")

with col2:
    st.title("🧸 Tu Peluche IA de Compañía")

API_KEY = "AIzaSyAzpQw6qxWMmXx_XMIMv3OABU5ZMvPzfUw"
try:
    genai.configure(api_key=API_KEY)
    model_chat = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error(f"No se pudo configurar Gemini: {e}")
    st.stop()

# ===== Nombre del niño =====
if "child_name" not in st.session_state:
    st.session_state.child_name = ""

st.session_state.child_name = st.text_input(
    "👦💬 Escribe tu nombre para que el peluche te llame por él:",
    value=st.session_state.child_name,
    placeholder="Tu nombre aquí... 😊"
)

if not st.session_state.child_name.strip():
    st.info("Por favor escribe tu nombre arriba para comenzar 🧸")
    st.stop()

# ===== Historial =====
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ===== Prompt base =====
ROLE_PROMPT = (
    f"Eres un peluche virtual llamado Osito Amigo. "
    f"Tu misión es acompañar, escuchar y dar apoyo emocional a niños. "
    f"Habla con ternura, sencillez y comprensión, como un amigo peluche. "
    f"Siempre llama al niño por su nombre: {st.session_state.child_name}. "
    f"No uses negritas ni asteriscos. "
    f"Tu objetivo es que el niño se sienta comprendido y acompañado."
)

# ===== Entrada de texto =====
user_input = st.chat_input(f"Escribe aquí lo que quieras contarme, {st.session_state.child_name}... 💭")

# ===== Procesar conversación =====
if user_input:
    # Mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Respuesta del peluche IA
    with st.chat_message("assistant"):
        with st.spinner("⏳ Pensando... ¡Osito está escuchando!"):
            try:
                history_text = "\n".join(
                    [f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages]
                )
                full_prompt = ROLE_PROMPT + "\n\n" + history_text + "\nAssistant:"
                resp = model_chat.generate_content(full_prompt)
                answer = (getattr(resp, "text", "") or "").strip() or "No entendí bien, ¿me cuentas otra vez?"
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.markdown(answer)

                # --- TTS ---
                tts = gTTS(answer, lang="es")
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                # Volver a abrir con pydub
                audio_bytes.seek(0)
                sound = AudioSegment.from_file(audio_bytes, format="mp3")
                # Aumentar velocidad (ej: 1.3x)
                faster_sound = sound._spawn(sound.raw_data, overrides={
                    "frame_rate": int(sound.frame_rate * 1.3)
                }).set_frame_rate(sound.frame_rate)
                out_bytes = io.BytesIO()
                faster_sound.export(out_bytes, format="mp3")
                audio_data = out_bytes.getvalue()
                b64 = base64.b64encode(audio_data).decode()
                audio_html = f"""
                <audio autoplay="true">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
