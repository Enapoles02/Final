import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Convertir el AttrDict a dict normal si es necesario
firebase_config = st.secrets["firebase"]
if not isinstance(firebase_config, dict):
    firebase_config = firebase_config.to_dict()

# Inicializar Firebase (sin mensajes de éxito para el usuario)
try:
    cred = credentials.Certificate(firebase_config)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
except Exception as e:
    st.error("Error al inicializar Firebase: " + str(e))
    raise

# Crear el cliente de Firestore
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
