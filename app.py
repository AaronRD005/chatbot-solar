import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="SolarTech AI - Asistente FV",
    page_icon="☀️",
    layout="centered"
)

# --- CONFIGURACIÓN DE LA API (SECRETA) ---
# Intentamos obtener la clave desde los secretos de Streamlit
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("No se ha encontrado la API Key. Por favor configura los secretos en Streamlit Cloud.")
    st.stop()

genai.configure(api_key=api_key)

# --- CONFIGURACIÓN DEL MODELO Y EL ROL (SYSTEM PROMPT) ---
# Aquí definimos la personalidad fija del asistente
generation_config = {
    "temperature": 0.7, # Creatividad moderada
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

system_instruction = """
Eres un asistente técnico experto en instalaciones fotovoltaicas (energía solar).
Tu objetivo es ayudar a instaladores y usuarios finales con dudas técnicas.
Tus respuestas deben ser precisas, técnicas pero comprensibles, y siempre priorizando la seguridad eléctrica.
Si te preguntan algo que no tenga nada que ver con energía solar o electricidad, responde amablemente que solo puedes responder sobre instalaciones fotovoltaicas.
Usa unidades correctas (W, kW, kWh, V, A).
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # Modelo rápido y gratuito
    generation_config=generation_config,
    system_instruction=system_instruction,
)

# --- INTERFAZ DE USUARIO ---
st.title("☀️ Asistente Técnico Fotovoltaico")
st.markdown("Bienvenido. Soy una IA especializada en resolver dudas sobre paneles solares, inversores y baterías.")

# Inicializar historial de chat si no existe
if "history" not in st.session_state:
    st.session_state.history = []

# --- BOTONES DE EJEMPLO (Requisito: Mínimo 3) ---
col1, col2, col3 = st.columns(3)
example_question = None

with col1:
    if st.button("Calculo de Baterías"):
        example_question = "¿Cómo calculo la capacidad de batería necesaria para una casa que consume 10kWh al día?"
with col2:
    if st.button("Inclinación Óptima"):
        example_question = "¿Cuál es la inclinación óptima para paneles solares en el sur de España?"
with col3:
    if st.button("Mantenimiento"):
        example_question = "¿Qué mantenimiento básico requieren los paneles solares?"

# Si se pulsó un botón, procesarlo como input
if example_question:
    # Añadir al historial visual y procesar
    # (La lógica de envío está más abajo, esto solo "pre-carga" el input)
    st.session_state.last_button_query = example_question

# --- MOSTRAR HISTORIAL DE CHAT ---
for message in st.session_state.history:
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message["content"])

# --- LÓGICA DE INTERACCIÓN ---
# Capturar input del usuario o del botón
query = st.chat_input("Escribe tu duda técnica aquí...")

# Si hay una pregunta de botón pendiente, la usamos
if "last_button_query" in st.session_state and st.session_state.last_button_query:
    query = st.session_state.last_button_query
    st.session_state.last_button_query = None # Limpiar para la próxima

if query:
    # 1. Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(query)
    
    # 2. Guardar en historial
    st.session_state.history.append({"role": "user", "content": query})

    # 3. Generar respuesta con la IA
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Enviar historial completo a Gemini para mantener contexto
        chat = model.start_chat(history=[
            {"role": "user" if m["role"] == "user" else "model", "parts": m["content"]}
            for m in st.session_state.history[:-1] # Excluir el último mensaje recién añadido para enviarlo ahora
        ])
        
        try:
            response = chat.send_message(query, stream=True)
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Error al conectar con la IA: {e}")
            full_response = "Lo siento, hubo un error de conexión."

    # 4. Guardar respuesta en historial
    st.session_state.history.append({"role": "model", "content": full_response})
