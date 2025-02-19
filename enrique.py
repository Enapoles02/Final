import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Cargar configuración de Firebase desde secrets
firebase_config = dict(st.secrets["firebase"])
firebase_config["private_key"] = firebase_config["private_key"].replace("\\n", "\n")  # Corrige los saltos de línea

# Inicializar Firebase solo si no está inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Prueba si Firebase está funcionando
st.title("Daily Huddle - Enrique")
st.write("Bienvenido a tu dashboard.")

try:
    # Intentamos acceder a la base de datos
    doc_ref = db.collection("prueba").document("test")
    doc_ref.set({"mensaje": "Firebase conectado con éxito!"})
    st.success("✅ Firebase se conectó correctamente.")
except Exception as e:
    st.error(f"⚠️ Error al conectar con Firebase: {e}")

    st.success("Evento añadido!")

st.sidebar.write("🔹 **Desarrollado por tu bot favorito 🤖**")
