import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io, base64
from pydub import AudioSegment

# ================== Configuración general ==================
st.set_page_config(page_title="🧸 Peluche IA", page_icon="🧸", layout="wide")

# ========= Estilos (solo UI) =========
st.markdown("""
    <style>
    /* Fuente redondeada y colores suaves */
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Nunito', sans-serif;
        color: #394253;
    }
    /* Fondo pastel suave con ilustraciones sutiles */
    .stApp {
        background: linear-gradient(180deg, #FDF7F2 0%, #F7FAFF 100%);
    }
    /* Ocultar el header por limpieza visual */
    header[data-testid="stHeader"] { 
        background: transparent; 
    }
    /* Contenedor principal card */
    .kid-card {
        background: #FFFFFFCC;
        border: 2px solid #F0F2F6;
        border-radius: 24px;
        padding: 20px 24px;
        box-shadow: 0 8px 20px rgba(56, 91, 173, 0.08);
        backdrop-filter: blur(4px);
    }
    /* Título grande estilo peluche */
    .title {
        font-weight: 800;
        font-size: 34px;
        letter-spacing: .3px;
        margin: 0 0 8px 0;
        color: #2E3A59;
    }
    .subtitle {
        margin-top: 0;
        color: #6D7B9A;
        font-weight: 600;
    }
    /* Input nombre más grande */
    .name-box input {
        background: #FFFFFF;
        border: 2px solid #E6ECFA !important;
        border-radius: 16px !important;
        padding: 14px 16px !important;
        font-size: 18px !important;
    }
    /* Burbujas de chat */
    .bubble { 
        padding: 14px 16px; 
        border-radius: 18px; 
        margin: 8px 0; 
        line-height: 1.5;
        font-size: 18px;
        word-wrap: break-word;
        white-space: pre-wrap;
    }
    .user-bubble {
        background: #E6F5FF;
        border: 2px solid #CBE9FF;
        color: #1A3458;
        border-top-right-radius: 6px;
        margin-left: 40px;
    }
    .bot-bubble {
        background: #FFF1F3;
        border: 2px solid #FFD9DE;
        color: #43293E;
        border-top-left-radius: 6px;
        margin-right: 40px;
    }
    /* Chat input más amable */
    div[data-baseweb="textarea"] textarea, .stChatInput input {
        background: #FFFFFF !important;
        border: 2px solid #E6ECFA !important;
        border-radius: 18px !important;
        padding: 14px 16px !important;
        font-size: 18px !important;
    }
    /* Botón pensar (spinner) más visible */
    .stSpinner > div {
        color: #6D7B9A !important;
        font-weight: 700;
    }
    /* Peluche gigante (posición fija en desktop) */
    .teddy-wrap {
        position: sticky;
        top: 16px;
    }
    .teddy {
        width: 100%;
        max-width: 420px;
        filter: drop-shadow(0 12px 24px rgba(0,0,0,0.1));
    }

    /* Chips decorativos */
    .chip {
        display: inline-block;
        background: #EEF7FF;
        border: 1px solid #D6EBFF;
        color: #2E5B98;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 14px;
        margin-right: 8px;
        margin-top: 6px;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# ====== Cabecera con columnas y peluche gigante (SVG inline) ======
left, right = st.columns([3, 2], gap="large")

with left:
    st.markdown('<div class="kid-card">', unsafe_allow_html=True)
    st.markdown('<div class="title">🧸 Tu Amigo Virtual de Compañía</div>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Un espacio seguro para hablar, jugar y sentirte acompañado.</p>', unsafe_allow_html=True)
    st.markdown('<div class="chip">Amabilidad</div><div class="chip">Escucha</div><div class="chip">Comprensión</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="teddy-wrap">', unsafe_allow_html=True)
    # SVG de peluche (inline, sin dependencias externas)
    teddy_svg = """
    <svg class="teddy" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="fur" x1="0" x2="1">
          <stop offset="0%" stop-color="#FFDACF"/>
          <stop offset="100%" stop-color="#FFC2AE"/>
        </linearGradient>
        <linearGradient id="inner" x1="0" x2="1">
          <stop offset="0%" stop-color="#FFF3E6"/>
          <stop offset="100%" stop-color="#FFE6CF"/>
        </linearGradient>
      </defs>
      <!-- orejas -->
      <circle cx="128" cy="120" r="70" fill="url(#fur)"/>
      <circle cx="384" cy="120" r="70" fill="url(#fur)"/>
      <circle cx="128" cy="120" r="42" fill="url(#inner)"/>
      <circle cx="384" cy="120" r="42" fill="url(#inner)"/>
      <!-- cabeza -->
      <circle cx="256" cy="180" r="120" fill="url(#fur)"/>
      <!-- hocico -->
      <ellipse cx="256" cy="210" rx="70" ry="50" fill="url(#inner)"/>
      <circle cx="236" cy="170" r="10" fill="#4C2E2E"/>
      <circle cx="276" cy="170" r="10" fill="#4C2E2E"/>
      <ellipse cx="256" cy="200" rx="14" ry="10" fill="#4C2E2E"/>
      <path d="M236 220 Q256 235 276 220" stroke="#4C2E2E" stroke-width="6" fill="none" stroke-linecap="round"/>
      <!-- cuerpo -->
      <ellipse cx="256" cy="345" rx="150" ry="130" fill="url(#fur)"/>
      <ellipse cx="256" cy="365" rx="90" ry="90" fill="url(#inner)"/>
      <!-- brazos -->
      <ellipse cx="120" cy="300" rx="60" ry="80" fill="url(#fur)"/>
      <ellipse cx="392" cy="300" rx="60" ry="80" fill="url(#fur)"/>
      <!-- piernas -->
      <ellipse cx="176" cy="440" rx="70" ry="50" fill="url(#fur)"/>
      <ellipse cx="336" cy="440" rx="70" ry="50" fill="url(#fur)"/>
      <ellipse cx="176" cy="440" rx="36" ry="24" fill="url(#inner)"/>
      <ellipse cx="336" cy="440" rx="36" ry="24" fill="url(#inner)"/>
      <!-- corazón pequeño -->
      <path d="M250 315
               C240 300,215 300,214 320
               C214 340,240 350,250 365
               C260 350,286 340,286 320
               C285 300,260 300,250 315 Z"
            fill="#FF7C93" opacity="0.8"/>
    </svg>
    """
    st.markdown(teddy_svg, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ========= Lógica original (sin cambios funcionales) =========

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

with left:
    st.markdown('<div class="kid-card name-box">', unsafe_allow_html=True)
    st.session_state.child_name = st.text_input("👦💬 Escribe tu nombre para que el peluche te llame por él:",
                                                value=st.session_state.child_name)
    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.child_name.strip():
    st.info("Por favor escribe tu nombre arriba para comenzar 🧸")
    st.stop()

# ===== Historial =====
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render de historial con burbujas
with left:
    st.markdown('<div class="kid-card">', unsafe_allow_html=True)
    for m in st.session_state.messages:
        role_class = "user-bubble" if m["role"] == "user" else "bot-bubble"
        st.markdown(f'<div class="bubble {role_class}">{m["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ===== Prompt base (sin cambios) =====
ROLE_PROMPT = (
    f"Eres un peluche virtual llamado Osito Amigo. "
    f"Tu misión es acompañar, escuchar y dar apoyo emocional a niños. "
    f"Habla con ternura, sencillez y comprensión, como un amigo peluche. "
    f"Siempre llama al niño por su nombre: {st.session_state.child_name}. "
    f"No uses negritas ni asteriscos. "
    f"Tu objetivo es que el niño se sienta comprendido y acompañado."
)

# ===== Entrada de texto =====
with left:
    user_input = st.chat_input(f"Escribe aquí lo que quieras contarme, {st.session_state.child_name}...")

# ===== Procesar conversación (igual que tu versión) =====
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with left:
        st.markdown('<div class="kid-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="bubble user-bubble">{user_input}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with left:
        with st.spinner("⏳ Pensando..."):
            try:
                history_text = "\n".join(
                    [f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages]
                )
                full_prompt = ROLE_PROMPT + "\n\n" + history_text + "\nAssistant:"

                resp = model_chat.generate_content(full_prompt)
                answer = (getattr(resp, "text", "") or "").strip() or "No entendí bien, ¿me cuentas otra vez?"

                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.markdown('<div class="kid-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="bubble bot-bubble">{answer}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # --- TTS (igual) ---
                tts = gTTS(answer, lang="es")
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)

                audio_bytes.seek(0)
                sound = AudioSegment.from_file(audio_bytes, format="mp3")
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
