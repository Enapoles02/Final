import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import streamlit.components.v1 as components

# ----------------------------
# Temporizador de 30 minutos
# ----------------------------
countdown_html = """
<div id="countdown" style="position: fixed; top: 10px; right: 10px; background-color: #f0f0f0; padding: 10px; border-radius: 5px; font-size: 18px; z-index:1000;">
  30:00
</div>
<script>
var timeLeft = 30 * 60; // 30 minutos en segundos
function updateTimer() {
    var minutes = Math.floor(timeLeft / 60);
    var seconds = timeLeft % 60;
    if (seconds < 10) { seconds = "0" + seconds; }
    document.getElementById("countdown").innerHTML = minutes + ":" + seconds;
    if(timeLeft > 0) {
        timeLeft--;
    } else {
        clearInterval(timerId);
    }
}
var timerId = setInterval(updateTimer, 1000);
</script>
"""
components.html(countdown_html, height=70)

# ----------------------------
# Inicialización de Firebase
# ----------------------------
firebase_config = st.secrets["firebase"]
if not isinstance(firebase_config, dict):
    firebase_config = firebase_config.to_dict()

try:
    cred = credentials.Certificate(firebase_config)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
except Exception as e:
    st.error("Error al inicializar Firebase: " + str(e))
    st.stop()

db = firestore.client()

# ----------------------------
# Interfaz de la aplicación
# ----------------------------
st.title("🔥 Daily Huddle - Enrique 🔥")
menu = ["Overview", "Attendance", "Top 3", "Action Board", "Communications", "Calendar"]
choice = st.sidebar.selectbox("📌 Selecciona una pestaña:", menu)

if choice == "Overview":
    st.subheader("📋 ¿Qué es el Daily Huddle?")
    st.write("""
    Bienvenido a tu Daily Huddle. Aquí podrás registrar tu asistencia, prioridades, acciones pendientes y eventos importantes del equipo.
    \n👈 Usa la barra lateral para navegar entre las diferentes secciones.
    """)

elif choice == "Attendance":
    st.subheader("📝 Registro de Asistencia")
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
    health_problem = st.radio("❓ ¿Te has sentido con problemas de salud esta semana?", ["Sí", "No"])
    
    if st.button("✅ Registrar asistencia"):
        doc_ref = db.collection("attendance").document("Enrique")
        doc_ref.set({
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "estado_animo": feelings[selected_feeling],
            "problema_salud": health_problem
        })
        st.success("Asistencia registrada correctamente.")

elif choice == "Top 3":
    st.subheader("📌 Top 3 Prioridades")
    st.write("Ingresa las tres prioridades con sus fechas y status correspondientes.")
    
    # Prioridad 1
    st.write("### Prioridad 1")
    prioridad1 = st.text_input("Descripción", key="p1")
    fecha_inicio1 = st.date_input("Fecha de inicio", key="ti1")
    fecha_compromiso1 = st.date_input("Fecha compromiso", key="tc1")
    fecha_real1 = st.date_input("Fecha real", key="tr1")
    status1 = st.selectbox("Status", ["Pendiente", "En proceso", "Completado"], key="s1")
    
    # Prioridad 2
    st.write("### Prioridad 2")
    prioridad2 = st.text_input("Descripción", key="p2")
    fecha_inicio2 = st.date_input("Fecha de inicio", key="ti2")
    fecha_compromiso2 = st.date_input("Fecha compromiso", key="tc2")
    fecha_real2 = st.date_input("Fecha real", key="tr2")
    status2 = st.selectbox("Status", ["Pendiente", "En proceso", "Completado"], key="s2")
    
    # Prioridad 3
    st.write("### Prioridad 3")
    prioridad3 = st.text_input("Descripción", key="p3")
    fecha_inicio3 = st.date_input("Fecha de inicio", key="ti3")
    fecha_compromiso3 = st.date_input("Fecha compromiso", key="tc3")
    fecha_real3 = st.date_input("Fecha real", key="tr3")
    status3 = st.selectbox("Status", ["Pendiente", "En proceso", "Completado"], key="s3")
    
    if st.button("📌 Guardar prioridades"):
        doc_ref = db.collection("top3").document("Enrique")
        doc_ref.set({
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "prioridades": [
                {"descripcion": prioridad1, "fecha_inicio": fecha_inicio1.strftime("%Y-%m-%d"), 
                 "fecha_compromiso": fecha_compromiso1.strftime("%Y-%m-%d"), "fecha_real": fecha_real1.strftime("%Y-%m-%d"), "status": status1},
                {"descripcion": prioridad2, "fecha_inicio": fecha_inicio2.strftime("%Y-%m-%d"), 
                 "fecha_compromiso": fecha_compromiso2.strftime("%Y-%m-%d"), "fecha_real": fecha_real2.strftime("%Y-%m-%d"), "status": status2},
                {"descripcion": prioridad3, "fecha_inicio": fecha_inicio3.strftime("%Y-%m-%d"), 
                 "fecha_compromiso": fecha_compromiso3.strftime("%Y-%m-%d"), "fecha_real": fecha_real3.strftime("%Y-%m-%d"), "status": status3}
            ]
        })
        st.success("Prioridades guardadas.")

elif choice == "Action Board":
    st.subheader("✅ Acciones y Seguimiento")
    accion = st.text_input("✍️ Describe la acción", key="action_desc")
    fecha_inicio_a = st.date_input("Fecha de inicio", key="action_ti")
    fecha_compromiso_a = st.date_input("Fecha compromiso", key="action_tc")
    fecha_real_a = st.date_input("Fecha real", key="action_tr")
    status_a = st.selectbox("Status", ["Pendiente", "En proceso", "Completado"], key="action_status")
    
    if st.button("✅ Guardar acción"):
        doc_ref = db.collection("actions").document()
        doc_ref.set({
            "usuario": "Enrique",
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "accion": accion,
            "fecha_inicio": fecha_inicio_a.strftime("%Y-%m-%d"),
            "fecha_compromiso": fecha_compromiso_a.strftime("%Y-%m-%d"),
            "fecha_real": fecha_real_a.strftime("%Y-%m-%d"),
            "status": status_a
        })
        st.success("Acción guardada.")

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
        st.success("Mensaje enviado.")

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
        st.success("Evento agendado.")
