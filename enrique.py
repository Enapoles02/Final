import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import datetime

# Cargar configuración de Firebase desde secretos en Streamlit
firebase_config = json.loads(json.dumps(st.secrets["firebase"]))

# Inicializar Firebase si aún no está inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Título de la app
st.title("Daily Huddle - Enrique")

# 🌟 ✅ Mostrar que Firebase está conectado correctamente
st.success("✅ Firebase se conectó correctamente.")

# 📌 ---- SECCIÓN: REGISTRO DE ASISTENCIA ----
st.subheader("📅 Registro de asistencia")
asistencia = st.checkbox("Marcar asistencia de hoy")

if asistencia:
    fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    db.collection("asistencia").document("Enrique").set({"fecha": fecha})
    st.success("✅ Asistencia registrada para hoy.")

# 📌 ---- SECCIÓN: FEELINGS ----
st.subheader("😊 ¿Cómo te sientes hoy?")
feeling_options = ["😀 Feliz", "😐 Normal", "😔 Triste", "😡 Enojado", "😴 Cansado", "🤒 Enfermo"]
feeling = st.radio("Selecciona un emoji que represente tu día", feeling_options)

db.collection("feelings").document("Enrique").set({"estado": feeling})
st.success(f"Tu estado de ánimo se ha registrado como: {feeling}")

# 📌 ---- SECCIÓN: SALUD ----
st.subheader("🏥 ¿Te has sentido con problemas de salud esta semana?")
salud = st.radio("Selecciona una opción:", ["Sí", "No"])
db.collection("salud").document("Enrique").set({"problemas_salud": salud})
st.success(f"Registro de salud actualizado: {salud}")

# 📌 ---- SECCIÓN: ACTION BOARD ----
st.subheader("📋 Action Board (Pizarra)")
st.markdown("Aquí se mostrarán todas las acciones guardadas:")

# 📌 🔄 Recuperar acciones desde Firebase y mostrarlas en la pizarra
acciones_ref = db.collection("action_board")
acciones = acciones_ref.stream()

for accion in acciones:
    st.write(f"✅ {accion.to_dict()['accion']}")

# 📌 🛠️ Botón flotante para agregar nuevas acciones
if st.button("➕"):
    with st.form("nueva_accion"):
        nueva_accion = st.text_area("Describe la acción:")
        submit = st.form_submit_button("Guardar acción")

        if submit and nueva_accion.strip():
            db.collection("action_board").add({"accion": nueva_accion, "fecha": datetime.datetime.now()})
            st.success("✅ Acción guardada correctamente. Recarga la página para verla en la pizarra.")

