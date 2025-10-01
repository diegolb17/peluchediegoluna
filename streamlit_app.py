import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io, base64
from pydub import AudioSegment

# ================== Configuración general ==================
st.set_page_config(page_title="🧸 Peluche IA", page_icon="🧸", layout="wide")

# ========= Estilos (UI) =========
st.markdown("""
<style>
/* Fuente redondeada y colores suaves */
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Nunito', sans-serif; color:#394253; }

/* Fondo pastel */
.stApp { background: linear-gradient(180deg,#FFF8F3 0%, #F7FAFF 100%); }

/* Contenedor central */
.container { max-width: 1200px; margin: 0 auto; }

/* Tarjetas suaves */
.card {
  background:#fff; border:2px solid #EEF2FA; border-radius:22px;
  box-shadow:0 6px 20px rgba(62,115,198,.08); padding:18px 20px;
}

/* Título/subtítulo */
.h-title{ font-size:34px; font-weight:800; margin:0; color:#2E3A59;}
.h-sub{ margin:.35rem 0 0; color:#6D7B9A; font-weight:600; }

/* Chips */
.chips { margin-top:8px;}
.chip{ display:inline-block; background:#EEF7FF; border:1px solid #D6EBFF;
  color:#2E5B98; padding:6px 12px; border-radius:999px; font-size:14px;
  font-weight:700; margin-right:8px; }

/* Entrada nombre */
.name-box input{
  background:#fff; border:2px solid #E6ECFA !important; border-radius:16px !important;
  padding:12px 14px !important; font-size:18px !important;
}

/* Caja de chat scrollable */
.chat-box{
  height: 52vh; min-height: 360px; overflow-y: auto; padding:6px 4px;
  scroll-behavior: smooth; background:#FCFDFE; border-radius:18px; border:2px solid #EEF2FA;
}

/* Burbujas */
.bubble{ padding:12px 14px; border-radius:16px; margin:8px 0; line-height:1.5; font-size:18px; white-space:pre-wrap; }
.user{ background:#E6F5FF; border:2px solid #CBE9FF; color:#163457; border-top-right-radius:6px; margin-left:48px;}
.bot{  background:#FFF1F3; border:2px solid #FFD9DE; color:#3E2A39; border-top-left-radius:6px; margin-right:48px;}

/* Input chat más amigable */
.stChatInput input{
  background:#fff !important; border:2px solid #E6ECFA !important; border-radius:18px !important;
  padding:14px 16px !important; font-size:18px !important;
}

/* Lado derecho peluche */
.teddy-card{ text-align:center; }
.teddy{ width:100%; max-width:420px; filter: drop-shadow(0 12px 24px rgba(0,0,0,.1)); }
.tip{ font-size:16px; color:#5b6c8a; }

/* Quitar padding lateral extra de contenedores */
.block-container{ padding-top:1.5rem; }
</style>
""", unsafe_allow_html=True)

# ====== Layout base ======
st.markdown('<div class="container">', unsafe_allow_html=True)

# Cabecera
colH1, colH2 = st.columns([3,2], gap="large")
with colH1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h1 class="h-title">Tu Amigo Virtual de Compañía</h1>', unsafe_allow_html=True)
    st.markdown('<p class="h-sub">Un espacio seguro para hablar, jugar y sentirte acompañado.</p>', unsafe_allow_html=True)
    st.markdown('<div class="chips"><span class="chip">Amabilidad</span><span class="chip">Escucha</span><span class="chip">Comprensión</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with colH2:
    st.markdown('<div class="card teddy-card">', unsafe_allow_html=True)
    teddy_svg = """
    <svg class="teddy" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="fur" x1="0" x2="1"><stop offset="0%" stop-color="#FFD8CC"/><stop offset="100%" stop-color="#FFC1AE"/></linearGradient>
        <linearGradient id="inner" x1="0" x2="1"><stop offset="0%" stop-color="#FFF3E6"/><stop offset="100%" stop-color="#FFE6CF"/></linearGradient>
      </defs>
      <circle cx="128" cy="120" r="70" fill="url(#fur)"/><circle cx="384" cy="120" r="70" fill="url(#fur)"/>
      <circle cx="128" cy="120" r="42" fill="url(#inner)"/><circle cx="384" cy="120" r="42" fill="url(#inner)"/>
      <circle cx="256" cy="180" r="120" fill="url(#fur)"/>
      <ellipse cx="256" cy="210" rx="70" ry="50" fill="url(#inner)"/>
      <circle cx="236" cy="170" r="10" fill="#4C2E2E"/><circle cx="276" cy="170" r="10" fill="#4C2E2E"/>
      <ellipse cx="256" cy="200" rx="14" ry="10" fill="#4C2E2E"/>
      <path d="M236 220 Q256 235 276 220" stroke="#4C2E2E" stroke-width="6" fill="none" stroke-linecap="round"/>
      <ellipse cx="256" cy="345" rx="150" ry="130" fill="url(#fur)"/><ellipse cx="256" cy="365" rx="90" ry="90" fill="url(#inner)"/>
      <ellipse cx="120" cy="300" rx="60" ry="80" fill="url(#fur)"/><ellipse cx="392" cy="300" rx="60" ry="80" fill="url(#fur)"/>
      <ellipse cx="176" cy="440" rx="70" ry="50" fill="url(#fur)"/><ellipse cx="336" cy="440" rx="70" ry="50" fill="url(#fur)"/>
      <ellipse cx="176" cy="440" rx="36" ry="24" fill="url(#inner)"/><ellipse cx="336" cy="440" rx="36" ry="24" fill="url(#inner)"/>
      <path d="M250 315 C240 300,215 300,214 320 C214 340,240 350,250 365 C260 350,286 340,286 320 C285 300,260 300,250 315 Z" fill="#FF7C93" opacity="0.85"/>
    </svg>
    """
    st.markdown(teddy_svg, unsafe_allow_html=True)
    st.markdown('<p class="tip">Hola, soy Osito Amigo. Estoy aquí para escucharte siempre 💖</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ========= Lógica original (no cambiada) =========

API_KEY = "AIzaSyAzpQw6qxWMmXx_XMIMv3OABU5ZMvPzfUw"
try:
    genai.configure(api_key=API_KEY)
    model_chat = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error(f"No se pudo configurar Gemini: {e}")
    st.stop()

# Prompt rol
def role_prompt(child_name:str)->str:
    return (
        f"Eres un peluche virtual llamado Osito Amigo. "
        f"Tu misión es acompañar, escuchar y dar apoyo emocional a niños. "
        f"Habla con ternura, sencillez y comprensión, como un amigo peluche. "
        f"Siempre llama al niño por su nombre: {child_name}. "
        f"No uses negritas ni asteriscos. "
        f"Tu objetivo es que el niño se sienta comprendido y acompañado."
    )

# Estado
if "child_name" not in st.session_state: st.session_state.child_name = ""
if "messages" not in st.session_state: st.session_state.messages = []

# Zona principal dos columnas (chat / peluche ya arriba)
left, right = st.columns([3,2], gap="large")

# Nombre y chat en la izquierda
with left:
    # Nombre
    st.markdown('<div class="card name-box">', unsafe_allow_html=True)
    st.session_state.child_name = st.text_input("👦💬 Escribe tu nombre para que el peluche te llame por él:",
                                                value=st.session_state.child_name)
    st.markdown('</div>', unsafe_allow_html=True)

    if not st.session_state.child_name.strip():
        st.info("Por favor escribe tu nombre arriba para comenzar 🧸")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # Historial en caja scroll
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for m in st.session_state.messages:
        cls = "user" if m["role"] == "user" else "bot"
        st.markdown(f'<div class="bubble {cls}">{m["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Input de chat abajo (queda a lo ancho de la columna izquierda)
with left:
    user_input = st.chat_input(f"Escribe aquí lo que quieras contarme, {st.session_state.child_name}...")

# ===== Procesar =====
if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})

    # Construir prompt con historial
    history_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages])
    full_prompt = role_prompt(st.session_state.child_name) + "\n\n" + history_text + "\nAssistant:"

    try:
        resp = model_chat.generate_content(full_prompt)
        answer = (getattr(resp, "text", "") or "").strip() or "No entendí bien, ¿me cuentas otra vez?"
        st.session_state.messages.append({"role":"assistant","content":answer})

        # TTS + autoplay
        tts = gTTS(answer, lang="es")
        audio_bytes = io.BytesIO(); tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        sound = AudioSegment.from_file(audio_bytes, format="mp3")
        faster_sound = sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * 1.3)
        }).set_frame_rate(sound.frame_rate)
        out_bytes = io.BytesIO(); faster_sound.export(out_bytes, format="mp3")
        audio_data = out_bytes.getvalue()
        b64 = base64.b64encode(audio_data).decode()
        st.markdown(f"""
            <audio autoplay="true">
              <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}")

st.markdown('</div>', unsafe_allow_html=True)  # /container
