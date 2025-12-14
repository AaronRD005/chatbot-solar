import streamlit as st
import google.generativeai as genai
import os

# =====================================================
# CONFIGURACIÓN DE LA PÁGINA
# =====================================================
st.set_page_config(
    page_title="SolarTech AI",
    page_icon="☀️",
    layout="centered"
)

# =====================================================
# CARGA SEGURA DE LA API KEY (STREAMLIT CLOUD / LOCAL)
# =====================================================
api_key = None

# 1. Streamlit Secrets (Cloud)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

# 2. Variable de entorno (local)
elif os.getenv("GEMINI_API_KEY"):
    api_key = os.getenv("GEMINI_API_KEY")

# Si no existe la clave → detener app
if not api_key:
    st.error("❌ No se ha encontrado la API Key de Gemini.")
    st.stop()

# Configurar Gemini
genai.configure(api_key=api_key)

# =====================================================
# CREACIÓN DEL MODELO GEMINI
# =====================================================
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        system_instruction=(
            "Eres un asistente técnico experto en energía solar fotovoltaica. "
            "Respondes con explicaciones claras, precisas y profesionales. "
            "Si faltan datos, indícalo y pide aclaraciones."
        )
    )
except Exception as e:
    st.error(f"❌ Error al inicializar el modelo Gemini: {e}")
    st.stop()

# =====================================================
# INTERFAZ DE USUARIO
# =====================================================
st.title("☀️ Asistente Solar Fotovoltaico")
st.caption("Soporte técnico para instalaciones solares, inversores, baterías y mantenimiento")

# =====================================================
# ESTADO DE LA CONVERSACIÓN
# =====================================================
if "history" not in st.session_state:
    st.session_state.history = []

# Mostrar historial
for msg in st.session_state.history:
    st.chat_message(msg["role"]).write(msg["content"])

# =====================================================
# INPUT DEL USUARIO
# =====================================================
prompt = st.chat_input("Escribe tu duda técnica sobre energía solar...")

if prompt:
    # Mostrar mensaje usuario
    st.session_state.history.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        # Convertir historial al formato Gemini
        chat = model.start_chat(
            history=[
                {
                    "role": "user" if m["role"] == "user" else "model",
                    "parts": m["content"]
                }
                for m in st.session_state.history[:-1]
            ]
        )

        # Enviar mensaje
        response = chat.send_message(prompt)

        # Mostrar respuesta
        st.session_state.history.append(
            {"role": "assistant", "content": response.text}
        )
        st.chat_message("assistant").write(response.text)

    except Exception as e:
        st.error(f"❌ Error durante la generación de la respuesta: {e}")


