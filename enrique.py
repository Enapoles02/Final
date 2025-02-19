import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
from datetime import datetime

# Cargar credenciales de Firebase desde los secrets de Streamlit
if not firebase_admin._apps:
    cred = credentials.Certificate(json.loads(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Título de la app
st.title("🔥 Daily Huddle - Enrique 🔥")

# Sidebar con las pestañas
menu = ["Overview", "Attendance", "Top 3", "Action Board", "Communications", "Calendar"]
choice = st.sidebar.selectbox("📌 Selecciona una pestaña:", menu)

# ---------- PESTAÑA 1: OVERVIEW ----------
if choice == "Overview":
    st.subheader("📋 ¿Qué es el Daily Huddle?")
    st.write("""
    Bienvenido a tu Daily Huddle. Aquí podrás registrar tu asistencia, prioridades, acciones pendientes y eventos importantes del equipo.
    \n👈 Usa la barra lateral para navegar entre las diferentes secciones.
    """)
    st.success("✅ Firebase se conectó correctamente.")

# ---------- PESTAÑA 2: ATTENDANCE ----------
elif choice == "Attendance":
    st.subheader("📝 Registro de Asistencia")

    # Selección de estado de ánimo con stickers/emojis
    st.write("💡 ¿Cómo te sientes hoy?")
    feelings = {
        "😃": "Feliz",
        "😐": "Normal",
        "😔": "Triste",
        "😡": "Molesto",
        "😴": "Cansado",
        "🤒": "Enfermo"
    }
    selected_feeling = st.radio("Selecciona tu estado de ánimo:", list(feelings.keys()))

    # Pregunta de salud
    health_problem = st.radio("❓ ¿Te has sentido con problemas de salud esta semana?", ["Sí", "No"])

    # Guardar en Firestore
    if st.button("✅ Registrar asistencia"):
        doc_ref = db.collection("attendance").document("Enrique")
        doc_ref.set({
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "estado_animo": feelings[selected_feeling],
            "problema_salud": health_problem
        })
        st.success("✅ Asistencia registrada correctamente.")

# ---------- PESTAÑA 3: TOP 3 ----------
elif choice == "Top 3":
    st.subheader("📌 Top 3 Prioridades")

    prioridad1 = st.text_input("1️⃣ Prioridad más importante")
    prioridad2 = st.text_input("2️⃣ Segunda prioridad")
    prioridad3 = st.text_input("3️⃣ Tercera prioridad")

    if st.button("📌 Guardar prioridades"):
        doc_ref = db.collection("top3").document("Enrique")
        doc_ref.set({
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "prioridad_1": prioridad1,
            "prioridad_2": prioridad2,
            "prioridad_3": prioridad3
        })
        st.success("✅ Prioridades guardadas.")

# ---------- PESTAÑA 4: ACTION BOARD ----------
elif choice == "Action Board":
    st.subheader("📝 Action Board")

    # Botón para abrir formulario de agregar acción
    if st.button("➕ Agregar Acción"):
        st.session_state["show_form"] = not st.session_state.get("show_form", False)

    # Formulario de acción (se muestra solo si se presiona el botón)
    if st.session_state.get("show_form", False):
        accion = st.text_input("✍️ Describe la acción")
        estado = st.selectbox("📌 Estado:", ["Pendiente", "En proceso", "Completado"])

        if st.button("✅ Guardar acción"):
            doc_ref = db.collection("actions").document()
            doc_ref.set({
                "usuario": "Enrique",
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "accion": accion,
                "estado": estado
            })
            st.success("✅ Acción guardada.")
            st.session_state["show_form"] = False  # Ocultar el formulario después de guardar

    st.write("---")

    # Mostrar acciones guardadas (Pizarra)
    st.subheader("📋 Acciones Registradas")
    actions = db.collection("actions").where("usuario", "==", "Enrique").stream()
    
    for action in actions:
        data = action.to_dict()
        st.markdown(f"**📌 {data['accion']}**\n\n🗓 {data['fecha']} - 🏷 {data['estado']}")
        st.write("---")

# ---------- PESTAÑA 5: COMMUNICATIONS ----------
elif choice == "Communications":
    st.subheader("📢 Mensajes Importantes")

    mensaje = st.text_area("📝 Escribe un mensaje o anuncio")
    
    if st.button("📩 Enviar mensaje"):
        doc_ref = db.collection("communications").document()
        doc_ref.set({
            "usuario": "Enrique",
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "mensaje": mensaje
        })
        st.success("✅ Mensaje enviado.")

# ---------- PESTAÑA 6: CALENDAR ----------
elif choice == "Calendar":
    st.subheader("📅 Eventos y Fechas Clave")

    evento = st.text_input("📌 Nombre del evento")
    fecha_evento = st.date_input("📅 Selecciona la fecha")

    if st.button("✅ Agendar evento"):
        doc_ref = db.collection("calendar").document()
        doc_ref.set({
            "usuario": "Enrique",
            "evento": evento,
            "fecha": fecha_evento.strftime("%Y-%m-%d")
        })
        st.success("✅ Evento agendado.")
