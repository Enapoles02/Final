import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import streamlit.components.v1 as components

# --------------------------------------------------
# Botón para iniciar el temporizador de 30 minutos
# --------------------------------------------------
if "timer_started" not in st.session_state:
    st.session_state.timer_started = False

if not st.session_state.timer_started:
    if st.button("Start Timer"):
        st.session_state.timer_started = True

# Si el timer ya inició, se inyecta el código HTML/JS para mostrarlo en la esquina superior derecha
if st.session_state.timer_started:
    countdown_html = """
    <div id="countdown" style="position: fixed; top: 10px; right: 10px; background-color: #f0f0f0; padding: 10px; border-radius: 5px; font-size: 18px; z-index:1000;">
      30:00
    </div>
    <script>
    var timeLeft = 30 * 60;
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

# --------------------------------------------------
# Inicialización de Firebase
# --------------------------------------------------
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

# --------------------------------------------------
# Interfaz de la aplicación
# --------------------------------------------------
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
    st.write("Ingresa las tres prioridades. Completa la descripción, fecha de inicio y compromiso, y selecciona el status. Si el status es 'Completado', se asigna automáticamente la fecha real.")
    
    with st.form("top3_form"):
        # Prioridad 1
        st.markdown("**Prioridad 1**")
        p1 = st.text_input("Descripción", key="p1")
        ti1 = st.date_input("Fecha de inicio", key="ti1")
        tc1 = st.date_input("Fecha compromiso", key="tc1")
        s1 = st.selectbox("Status", ["Pendiente", "En proceso", "Completado"], key="s1")
        
        # Prioridad 2
        st.markdown("**Prioridad 2**")
        p2 = st.text_input("Descripción", key="p2")
        ti2 = st.date_input("Fecha de inicio", key="ti2")
        tc2 = st.date_input("Fecha compromiso", key="tc2")
        s2 = st.selectbox("Status", ["Pendiente", "En proceso", "Completado"], key="s2")
        
        # Prioridad 3
        st.markdown("**Prioridad 3**")
        p3 = st.text_input("Descripción", key="p3")
        ti3 = st.date_input("Fecha de inicio", key="ti3")
        tc3 = st.date_input("Fecha compromiso", key="tc3")
        s3 = st.selectbox("Status", ["Pendiente", "En proceso", "Completado"], key="s3")
        
        submit_top3 = st.form_submit_button("Guardar prioridades")
    
    if submit_top3:
        # Para cada prioridad, si el status es 'Completado', asignamos la fecha real actual; de lo contrario, dejamos vacío.
        prioridades = []
        for desc, ti, tc, s in [(p1, ti1, tc1, s1), (p2, ti2, tc2, s2), (p3, ti3, tc3, s3)]:
            fecha_real = datetime.now().strftime("%Y-%m-%d") if s == "Completado" else ""
            prioridades.append({
                "descripcion": desc,
                "fecha_inicio": ti.strftime("%Y-%m-%d"),
                "fecha_compromiso": tc.strftime("%Y-%m-%d"),
                "fecha_real": fecha_real,
                "status": s
            })
        doc_ref = db.collection("top3").document("Enrique")
        doc_ref.set({
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "prioridades": prioridades
        })
        st.success("Prioridades guardadas.")

elif choice == "Action Board":
    st.subheader("✅ Acciones y Seguimiento")
    st.write("Agrega una nueva acción. Completa la descripción, fecha de inicio y compromiso, y selecciona el status. Si el status es 'Completado', se asigna automáticamente la fecha real.")
    
    with st.form("action_board_form"):
        accion = st.text_input("Descripción de la acción", key="action_desc")
        ti = st.date_input("Fecha de inicio", key="action_ti")
        tc = st.date_input("Fecha compromiso", key="action_tc")
        status = st.selectbox("Status", ["Pendiente", "En proceso", "Completado"], key="action_status")
        submit_action = st.form_submit_button("Guardar acción")
    
    if submit_action:
        fecha_real = datetime.now().strftime("%Y-%m-%d") if status == "Completado" else ""
        doc_ref = db.collection("actions").document()
        doc_ref.set({
            "usuario": "Enrique",
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "accion": accion,
            "fecha_inicio": ti.strftime("%Y-%m-%d"),
            "fecha_compromiso": tc.strftime("%Y-%m-%d"),
            "fecha_real": fecha_real,
            "status": status
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
