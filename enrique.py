import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Convertir el AttrDict a un dict normal
firebase_config = st.secrets["firebase"]
if not isinstance(firebase_config, dict):
    firebase_config = firebase_config.to_dict()

st.write("Tipo de firebase_config:", type(firebase_config))
st.write("Contenido de firebase_config:", firebase_config)

# Inicializar Firebase
try:
    cred = credentials.Certificate(firebase_config)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    st.success("Firebase inicializado correctamente.")
except Exception as e:
    st.error("Error al inicializar Firebase: " + str(e))
    raise

# Crear cliente de Firestore
db = firestore.client()

# Resto de la aplicación
st.title("🔥 Daily Huddle - Enrique 🔥")
menu = ["Overview", "Attendance", "Top 3", "Action Board", "Communications", "Calendar"]
choice = st.sidebar.selectbox("📌 Selecciona una pestaña:", menu)

if choice == "Overview":
    st.subheader("📋 ¿Qué es el Daily Huddle?")
    st.write("""
    Bienvenido a tu Daily Huddle. Aquí podrás registrar tu asistencia, prioridades, acciones pendientes y eventos importantes del equipo.
    \n👈 Usa la barra lateral para navegar entre las diferentes secciones.
    """)
    st.success("✅ Firebase se conectó correctamente.")
