import streamlit as st
import google.generativeai as genai
import os

# -----------------------------
# Configuración de la página
# -----------------------------
st.set_page_config(
    page_title="SolarTech AI",
    page_icon="☀️",
    layout="centered"
)

# -----------------------------
# Cargar API Key (Streamlit Secrets)
# -----------------------------
api_key = None

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
elif os.getenv("GEMINI_API_KEY"):
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ No se ha encontrado la API Key de Gemini.")
    st.stop()

genai.configure(api_key=api_key)

# -----------------------------
# Crear modelo Gemini
# -----------------------------
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        system_instruction=(
            "Eres un experto técnico en energía solar fotovoltaica. "
            "Respondes con claridad, precisión y lenguaje profesional."
        )
    )
except Exception as e:
    st.error(f"❌ Error al inicializar el modelo: {e}")
    st.stop()

# -----------------------------
# Interfaz
# -----------------------------
st.title("☀️ Asistente Solar Fotovoltaico")

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    st.chat_message(msg["role"]).write(msg["content"])

prompt = st.chat_input("Duda sobre instalaciones solares, inversores, baterías...")

if prompt:
    st.session_state.history.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        chat = model.start_chat(
            history=[
                {
                    "role": "user" if m["role"] == "user" else "model",
                    "parts": m["content"]
                }
                for m in st.session_state.history[:-1]
            ]
        )

        response = chat.send_message(prompt)

        st.session_state.history.append(
            {"role": "assistant", "content": response.text}
        )
        st.chat_message("assistant").write(response.text)

    except Exception as e:
        st.error(f"❌ Error durante la generación: {e}")

