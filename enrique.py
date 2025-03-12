import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, date, timedelta
import json, random, uuid
import pandas as pd

# Para efectos de depuración, comentamos el autorefresh
# from streamlit_autorefresh import st_autorefresh

# -------------------------------
# Definición de usuarios (simplificada para debug)
# -------------------------------
valid_users = {
    "CNAPOLES": "Napoles Escorsante Christopher Enrique",
    "ALECCION": "TL GL NAMER LATAM",
    "WORLEAD": "TL WOR SGBS",
    "R2RGRAL": "TL R2R GRAL",
    "FALEAD": "TL FA",
    "ICLEAD": "TL IC",
    "LARANDA": "RH - Luis Aranda",
    "KPI": "KPI Reporte"
}

TL_USERS = {"ALECCION", "WORLEAD", "R2RGRAL", "FALEAD", "ICLEAD"}

# -------------------------------
# Pantalla de Login
# -------------------------------
if "user_code" not in st.session_state:
    st.session_state["user_code"] = None

def show_login():
    st.title("🔥 Daily Huddle - Login")
    user_input = st.text_input("Código de usuario:")
    if st.button("Ingresar"):
        user_input = user_input.strip().upper()
        if user_input in valid_users:
            st.session_state.user_code = user_input
            st.success(f"¡Bienvenido, {valid_users[user_input]}!")
        else:
            st.error("Código inválido.")

if st.session_state["user_code"] is None:
    show_login()
    st.stop()

# -------------------------------
# Inicialización de Firebase
# -------------------------------
def init_firebase():
    firebase_config = st.secrets.get("firebase")
    if not firebase_config:
        st.error("No se encontró la clave 'firebase' en los secrets.")
        st.stop()
    if not isinstance(firebase_config, dict):
        firebase_config = firebase_config.to_dict()
    try:
        cred = credentials.Certificate(firebase_config)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        st.write("DEBUG: Firebase inicializado correctamente")
        return db
    except Exception as e:
        st.error(f"Error al inicializar Firebase: {e}")
        st.stop()

db = init_firebase()

# -------------------------------
# Función para obtener fecha activa (día laboral)
# -------------------------------
def get_active_date():
    today = date.today()
    if today.weekday() == 5:  # sábado
        active = today - timedelta(days=1)
    elif today.weekday() == 6:  # domingo
        active = today - timedelta(days=2)
    else:
        active = today
    return active.strftime("%Y-%m-%d")

# -------------------------------
# Función para mostrar Asistencia (debug)
# -------------------------------
def show_asistencia():
    st.subheader("📝 Registro de Asistencia")
    today_date = datetime.now().strftime("%Y-%m-%d")
    st.write("DEBUG: Hoy es", today_date)
    # Consultamos el documento de asistencia
    attendance_doc = db.collection("attendance").document(st.session_state.user_code).get()
    st.write("DEBUG: attendance_doc.exists =", attendance_doc.exists)
    if attendance_doc.exists:
        data = attendance_doc.to_dict()
        st.write("DEBUG: Datos de asistencia previos:", data)
        if data.get("fecha") != today_date:
            db.collection("attendance").document(st.session_state.user_code).delete()
            st.write("DEBUG: Se eliminó asistencia antigua.")
    # Formulario de asistencia
    feelings = {"😃": "Feliz", "😐": "Normal", "😔": "Triste"}
    selected_feeling = st.radio("Estado de ánimo:", list(feelings.keys()))
    if st.button("Registrar asistencia"):
        db.collection("attendance").document(st.session_state.user_code).set({
            "fecha": today_date,
            "estado_animo": feelings[selected_feeling],
            "usuario": st.session_state.user_code
        })
        st.success("Asistencia registrada.")
        st.write("DEBUG: Asistencia registrada en Firebase.")

# -------------------------------
# Función para mostrar Top 3 (simplificada con debug)
# -------------------------------
def show_top3():
    st.subheader("📌 Tareas Top 3")
    active_date = get_active_date()
    st.write("DEBUG: Fecha activa =", active_date)
    tasks = list(db.collection("top3").where("fecha_inicio", "==", active_date).stream())
    st.write("DEBUG: Tareas Top 3 encontradas =", len(tasks))
    if tasks:
        attendance_list = []
        for task in tasks:
            data = task.to_dict()
            st.write("DEBUG: Tarea:", data)
            attendance_list.append({
                "Descripción": data.get("descripcion", "Sin descripción"),
                "Fecha Inicio": data.get("fecha_inicio", ""),
                "Fecha Compromiso": data.get("fecha_compromiso", ""),
                "Status": data.get("status", "")
            })
        df = pd.DataFrame(attendance_list)
        st.dataframe(df)
    else:
        st.info("No hay tareas Top 3 para el día activo.")

# -------------------------------
# Función principal
# -------------------------------
def show_main_app():
    st.write("DEBUG: Entrando a show_main_app")
    user_code = st.session_state["user_code"]
    st.write("DEBUG: Usuario =", user_code)
    
    # Menú principal (simplificado para depuración)
    menu_options = ["Asistencia", "Top 3", "Consultorio Optimizacion", "Contacto"]
    menu_choice = st.sidebar.selectbox("Selecciona una pestaña:", menu_options)
    st.write("DEBUG: Menú seleccionado =", menu_choice)
    
    if menu_choice == "Asistencia":
        show_asistencia()
    elif menu_choice == "Top 3":
        show_top3()
    elif menu_choice == "Consultorio Optimizacion":
        st.subheader("Consultorio de Optimización")
        with st.form("consultorio_form"):
            mensaje = st.text_area("Describe tu requerimiento:")
            archivo = st.file_uploader("Adjuntar archivo (opcional)")
            submit = st.form_submit_button("Enviar Consulta")
        if submit:
            db.collection("consultorio").add({
                "usuario": user_code,
                "mensaje": mensaje,
                "archivo": archivo.name if archivo else None,
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "destinatario": "CNAPOLES"
            })
            st.success("Consulta enviada a CNAPOLES.")
    elif menu_choice == "Contacto":
        st.subheader("Contacto / Reporte de Problemas")
        with st.form("contacto_form"):
            asunto = st.text_input("Asunto:")
            mensaje = st.text_area("Describe tu problema:")
            submit = st.form_submit_button("Enviar Reporte")
        if submit:
            db.collection("contacto").add({
                "usuario": user_code,
                "asunto": asunto,
                "mensaje": mensaje,
                "fecha": datetime.now().strftime("%Y-%m-%d")
            })
            st.success("Reporte enviado.")

st.write("DEBUG: Llamando a show_main_app")
show_main_app()
