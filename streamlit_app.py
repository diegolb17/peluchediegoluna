import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io, base64
from pydub import AudioSegment

# ================== Configuración general ==================
st.set_page_config(page_title="🧸 Peluche IA", page_icon="🧸", layout="centered")

# Custom CSS for a minimalist, child-friendly design
st.markdown("""
<style>
    body {
        background-color: #F0F4F8;
        font-family: 'Comic Sans MS', 'Chalkboard SE', sans-serif;
    }
    .main {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        max-width: 700px;
        margin: auto;
    }
    h1 {
        color: #FF9999;
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 20px;
    }
    .stTextInput > div > div > input {
        background-color: #E6F3FA;
        border: 2px solid #A3D8F4;
        border-radius: 15px;
        padding: 10px;
        font-size: 1.2em;
        color: #333;
    }
    .stTextInput > div > div > input:focus {
        border-color: #FF9999;
        box-shadow: 0 0 5px rgba(255, 153, 153, 0.5);
    }
    .stChatInput {
        background-color: #FFF5E6;
        border: 2px solid #FFDAB9;
        border-radius: 15px;
        padding: 10px;
    }
    .stChatMessage {
        border-radius: 15px;
        margin: 10px 0;
        padding: 15px;
    }
    .stChatMessage[data-testid="user"] {
        background-color: #E6F3FA;
        border: 2px solid #A3D8F4;
    }
    .stChatMessage[data-testid="assistant"] {
        background-color: #FFF5E6;
        border: 2px solid #FFDAB9;
    }
    .stSpinner > div > div {
        color: #FF9999;
    }
    .teddy-image {
        display: block;
        margin: 20px auto;
        max-width: 200px;
        animation: bounce 2s infinite;
    }
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
</style>
""", unsafe_allow_html=True)

# Giant teddy bear image (using a free, child-friendly teddy bear image URL)
st.image("https://www.pngall.com/wp-content/uploads/5/Teddy-Bear-PNG-Image.png", 
         caption="¡Osito Amigo está aquí para ti!", 
         use_column_width=False, 
         width=200, 
         output_format="PNG",
         cls="teddy-image")

st.title("🧸 Tu Amigo Virtual de Compañía")

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
    placeholder="Tu nombre aquí..."
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
