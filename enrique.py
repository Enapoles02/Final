import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

# 🔹 Cargar credenciales de Firebase desde GitHub Secrets
firebase_cred = os.getenv("FIREBASE_CREDENTIALS")

if firebase_cred:
    cred_dict = json.loads(firebase_cred)
    cred = credentials.Certificate(cred_dict)
    try:
        firebase_admin.initialize_app(cred)
    except ValueError:
        pass
    db = firestore.client()
else:
    st.error("⚠️ No se encontró la configuración de Firebase. Revisa tu clave JSON.")

# 🔹 Configuración de usuario (Enrique)
USER_NAME = "Enrique"
USER_ID = "user_enrique"

# 🔹 Sidebar con menú de navegación
st.sidebar.title(f"🔹 {USER_NAME}'s Dashboard")
page = st.sidebar.radio("Menú", ["📌 Overview", "🔥 Top 3", "✅ Action Board", "📢 Communications", "📅 Calendar"])

# 🔹 Pantallas personalizadas para Enrique
if page == "📌 Overview":
    st.title(f"Bienvenido, {USER_NAME} 👋")
    st.write("Esta es tu plataforma personalizada. Aquí puedes gestionar tus tareas diarias.")
    
elif page == "🔥 Top 3":
    st.title("🔥 Prioridades del Día")
    top3_ref = db.collection("users").document(USER_ID).collection("top3")

    # Mostrar las prioridades actuales
    top3_tasks = [doc.to_dict() for doc in top3_ref.stream()]
    for task in top3_tasks:
        st.write(f"✅ {task['title']}")

    # Agregar nueva prioridad
    new_task = st.text_input("Añadir nueva prioridad:")
    if st.button("Agregar"):
        if new_task:
            top3_ref.add({"title": new_task})
            st.success("Prioridad añadida!")

elif page == "✅ Action Board":
    st.title("✅ Tareas y Acciones")
    action_board_ref = db.collection("users").document(USER_ID).collection("action_board")

    # Mostrar tareas actuales
    tasks = [doc.to_dict() for doc in action_board_ref.stream()]
    for task in tasks:
        st.write(f"📌 {task['task']} - {task['status']}")

    # Agregar nueva acción
    new_action = st.text_input("Añadir nueva tarea:")
    status = st.selectbox("Estado", ["Pendiente", "En progreso", "Completada"])
    if st.button("Agregar"):
        if new_action:
            action_board_ref.add({"task": new_action, "status": status})
            st.success("Tarea añadida!")

elif page == "📢 Communications":
    st.title("📢 Comunicaciones")
    comm_ref = db.collection("users").document(USER_ID).collection("communications")

    # Mostrar mensajes actuales
    messages = [doc.to_dict() for doc in comm_ref.stream()]
    for msg in messages:
        st.write(f"📝 {msg['message']}")

    # Agregar nueva comunicación
    new_msg = st.text_input("Añadir nuevo mensaje:")
    if st.button("Enviar"):
        if new_msg:
            comm_ref.add({"message": new_msg})
            st.success("Mensaje enviado!")

elif page == "📅 Calendar":
    st.title("📅 Eventos y Fechas Clave")
    calendar_ref = db.collection("users").document(USER_ID).collection("calendar")

    # Mostrar eventos actuales
    events = [doc.to_dict() for doc in calendar_ref.stream()]
    for event in events:
        st.write(f"📅 {event['date']}: {event['event']}")

    # Agregar nuevo evento
    new_event = st.text_input("Añadir nuevo evento:")
    event_date = st.date_input("Seleccionar fecha")
    if st.button("Agregar Evento"):
        if new_event:
            calendar_ref.add({"event": new_event, "date": str(event_date)})
            st.success("Evento añadido!")

st.sidebar.write("🔹 **Desarrollado por tu bot favorito 🤖**")
