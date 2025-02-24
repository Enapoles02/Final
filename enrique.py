import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import ast

# Verificar el contenido y tipo de st.secrets["firebase"]
firebase_config = st.secrets["firebase"]
st.write("Tipo de st.secrets['firebase']:", type(firebase_config))
st.write("Contenido de st.secrets['firebase']:", firebase_config)

# Si es una cadena, convertirla a diccionario usando ast.literal_eval
if isinstance(firebase_config, str):
    try:
        firebase_config = ast.literal_eval(firebase_config)
        st.write("Después de la conversión, tipo:", type(firebase_config))
    except Exception as e:
        st.error("Error al convertir la configuración a diccionario: " + str(e))
        raise

# Inicializar Firebase con la configuración verificada
try:
    cred = credentials.Certificate(firebase_config)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    st.success("Firebase inicializado correctamente.")
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
    st.success("✅ Firebase se conectó correctamente.")

# Puedes continuar con el resto de tus pestañas...
