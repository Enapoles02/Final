import streamlit as st
import json
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# Cargar configuración de Firebase desde los secrets de Streamlit
firebase_config = json.loads(json.dumps(st.secrets["firebase"]))

# Inicializar Firebase si no está ya inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Función para obtener acciones de la pizarra
def get_actions():
    docs = db.collection("actions").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

# Inicializar sesión para manejar estado
if "show_action_form" not in st.session_state:
    st.session_state["show_action_form"] = False

# Título principal
st.title("📌 Daily Huddle - Enrique")

# Botón para mostrar el formulario
if st.button("➕ Agregar Acción"):
    st.session_state["show_action_form"] = not st.session_state["show_action_form"]

# Mostrar formulario solo si el botón ha sido presionado
if st.session_state["show_action_form"]:
    st.subheader("Agregar Nueva Acción")
    action_text = st.text_area("Describe la acción:", key="action_input")
    action_priority = st.selectbox("Prioridad:", ["Alta", "Media", "Baja"], key="priority_input")
    
    if st.button("Guardar acción"):
        if action_text:
            action_data = {
                "text": action_text,
                "priority": action_priority,
                "timestamp": datetime.datetime.utcnow()
            }
            db.collection("actions").add(action_data)
            st.success("✅ Acción guardada correctamente")
            st.session_state["show_action_form"] = False
            st.experimental_rerun()  # Recargar para reflejar cambios
        else:
            st.error("⚠️ Debes escribir una acción antes de guardar.")

# Sección de la Pizarra de Acciones
st.subheader("📌 Pizarra de Acciones")
actions = get_actions()

if actions:
    for action in actions:
        st.write(f"📝 **{action['text']}** | 🔥 *{action['priority']}* | ⏳ {action['timestamp'].strftime('%Y-%m-%d %H:%M')}")
else:
    st.info("No hay acciones registradas aún.")
