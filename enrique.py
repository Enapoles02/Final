import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import streamlit.components.v1 as components
import json

# -------------------------------------------------------------------
# Temporizador: Se inicia solo al presionar "Start Timer"
# -------------------------------------------------------------------
if "timer_started" not in st.session_state:
    st.session_state.timer_started = False

if not st.session_state.timer_started:
    if st.button("Start Timer"):
        st.session_state.timer_started = True

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

# -------------------------------------------------------------------
# Inicialización de Firebase
# -------------------------------------------------------------------
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

# Función para determinar el status (usa el personalizado si se ingresa)
def get_status(selected, custom):
    return custom.strip() if custom and custom.strip() != "" else selected

# Diccionario para colores de status
status_colors = {
    "Pendiente": "red",
    "En proceso": "orange",
    "Completado": "green"
}

# -------------------------------------------------------------------
# Menú principal (se han añadido Recognition y Escalations)
# -------------------------------------------------------------------
st.title("🔥 Daily Huddle - Enrique 🔥")
menu = ["Overview", "Attendance", "Recognition", "Escalations", "Top 3", "Action Board", "Communications", "Calendar"]
choice = st.sidebar.selectbox("📌 Selecciona una pestaña:", menu)

# ----------------
# Overview
# ----------------
if choice == "Overview":
    st.subheader("📋 ¿Qué es el Daily Huddle?")
    st.write("""
    Bienvenido a tu Daily Huddle. Aquí podrás registrar tu asistencia, prioridades, acciones, reconocimientos, escalaciones y eventos importantes del equipo.
    \n👈 Usa la barra lateral para navegar entre las diferentes secciones.
    """)

# ----------------
# Attendance: Agregamos rating de energía tipo rating (estrellas)
# ----------------
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
    # Agregamos rating de energía (estrellas)
    energy = st.radio("Nivel de energía:", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], horizontal=True)
    
    if st.button("✅ Registrar asistencia"):
        db.collection("attendance").document("Enrique").set({
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "estado_animo": feelings[selected_feeling],
            "problema_salud": health_problem,
            "energia": energy
        })
        st.success("Asistencia registrada correctamente.")

# ----------------
# Recognition: Enviar felicitaciones
# ----------------
elif choice == "Recognition":
    st.subheader("🎉 Recognition")
    st.write("Envía un reconocimiento a un compañero.")
    with st.form("recognition_form"):
        destinatario = st.text_input("Email destinatario")
        asunto = st.text_input("Asunto")
        mensaje = st.text_area("Mensaje de felicitación")
        submit_recognition = st.form_submit_button("Enviar reconocimiento")
    if submit_recognition:
        db.collection("recognitions").add({
            "usuario": "Enrique",
            "destinatario": destinatario,
            "asunto": asunto,
            "mensaje": mensaje,
            "fecha": datetime.now().strftime("%Y-%m-%d")
        })
        st.success("Reconocimiento enviado.")

# ----------------
# Escalations: Registrar escalaciones
# ----------------
elif choice == "Escalations":
    st.subheader("⚠️ Escalations")
    st.write("Registra una escalación con la información requerida.")
    with st.form("escalation_form"):
        quien_escala = st.text_input("¿Quién escala?")
        por_que = st.text_area("¿Por qué?")
        para_quien = st.text_input("¿Para quién?")
        con_quien = st.text_input("¿Con quién se tiene el tema?")
        submit_escalation = st.form_submit_button("Enviar escalación")
    if submit_escalation:
        db.collection("escalations").add({
            "usuario": "Enrique",
            "quien_escala": quien_escala,
            "por_que": por_que,
            "para_quien": para_quien,
            "con_quien": con_quien,
            "fecha": datetime.now().strftime("%Y-%m-%d")
        })
        st.success("Escalación registrada.")

# ----------------
# Top 3: Tareas y prioridades
# ----------------
elif choice == "Top 3":
    st.subheader("📌 Top 3 Prioridades - Resumen")
    # Mostrar resumen de tareas en Top 3 para el usuario "Enrique"
    tasks = list(db.collection("top3").where("usuario", "==", "Enrique").stream())
    if tasks:
        for task in tasks:
            task_data = task.to_dict()
            st.markdown(f"**{task_data.get('descripcion','')}**")
            st.write(f"Inicio: {task_data.get('fecha_inicio','')} | Compromiso: {task_data.get('fecha_compromiso','')} | Real: {task_data.get('fecha_real','')}")
            status_val = task_data.get('status', '')
            color = status_colors.get(status_val, "black")
            st.markdown(f"**Status:** <span style='color: {color};'>{status_val}</span>", unsafe_allow_html=True)
            if st.button("🗑️ Eliminar", key=f"delete_top3_{task.id}"):
                db.collection("top3").document(task.id).delete()
                st.success("Tarea eliminada. Recarga la página para ver el cambio.")
                try:
                    st.experimental_rerun()
                except Exception:
                    pass
    else:
        st.info("No hay tareas de Top 3 registradas.")
    
    if st.button("➕ Agregar Tarea de Top 3"):
        st.session_state.show_top3_form = True
    if st.session_state.get("show_top3_form"):
        with st.form("top3_add_form"):
            st.markdown("### Nueva Tarea - Top 3")
            p = st.text_input("Descripción")
            ti = st.date_input("Fecha de inicio")
            tc = st.date_input("Fecha compromiso")
            s = st.selectbox("Status", ["Pendiente", "En proceso", "Completado"], key="top3_status")
            custom_status = st.text_input("Status personalizado (opcional)", key="custom_status_top3")
            submit_new_top3 = st.form_submit_button("Guardar tarea")
        if submit_new_top3:
            final_status = get_status(s, custom_status)
            fecha_real = datetime.now().strftime("%Y-%m-%d") if final_status.lower() == "completado" else ""
            data = {
                "usuario": "Enrique",
                "descripcion": p,
                "fecha_inicio": ti.strftime("%Y-%m-%d"),
                "fecha_compromiso": tc.strftime("%Y-%m-%d"),
                "fecha_real": fecha_real,
                "status": final_status,
                "timestamp": datetime.now()
            }
            db.collection("top3").add(data)
            st.success("Tarea de Top 3 guardada.")
            st.session_state.show_top3_form = False
            try:
                st.experimental_rerun()
            except Exception:
                pass

# ----------------
# Action Board: Acciones y seguimiento
# ----------------
elif choice == "Action Board":
    st.subheader("✅ Acciones y Seguimiento - Resumen")
    # Mostrar resumen de acciones para el usuario "Enrique"
    actions = list(db.collection("actions").where("usuario", "==", "Enrique").stream())
    if actions:
        for action in actions:
            act_data = action.to_dict()
            st.markdown(f"**{act_data.get('accion','')}**")
            st.write(f"Inicio: {act_data.get('fecha_inicio','')} | Compromiso: {act_data.get('fecha_compromiso','')} | Real: {act_data.get('fecha_real','')}")
            status_val = act_data.get('status', '')
            color = status_colors.get(status_val, "black")
            st.markdown(f"**Status:** <span style='color: {color};'>{status_val}</span>", unsafe_allow_html=True)
            if st.button("🗑️ Eliminar", key=f"delete_action_{action.id}"):
                db.collection("actions").document(action.id).delete()
                st.success("Acción eliminada. Recarga la página para ver el cambio.")
                try:
                    st.experimental_rerun()
                except Exception:
                    pass
    else:
        st.info("No hay acciones registradas.")
    
    if st.button("➕ Agregar Acción"):
        st.session_state.show_action_form = True
    if st.session_state.get("show_action_form"):
        with st.form("action_add_form"):
            st.markdown("### Nueva Acción")
            accion = st.text_input("Descripción de la acción")
            ti = st.date_input("Fecha de inicio")
            tc = st.date_input("Fecha compromiso")
            s = st.selectbox("Status", ["Pendiente", "En proceso", "Completado"], key="action_status")
            custom_status = st.text_input("Status personalizado (opcional)", key="custom_status_action")
            submit_new_action = st.form_submit_button("Guardar acción")
        if submit_new_action:
            final_status = get_status(s, custom_status)
            fecha_real = datetime.now().strftime("%Y-%m-%d") if final_status.lower() == "completado" else ""
            data = {
                "usuario": "Enrique",
                "accion": accion,
                "fecha_inicio": ti.strftime("%Y-%m-%d"),
                "fecha_compromiso": tc.strftime("%Y-%m-%d"),
                "fecha_real": fecha_real,
                "status": final_status,
                "fecha": datetime.now().strftime("%Y-%m-%d")
            }
            db.collection("actions").add(data)
            st.success("Acción guardada.")
            st.session_state.show_action_form = False
            try:
                st.experimental_rerun()
            except Exception:
                pass

# ----------------
# Communications
# ----------------
elif choice == "Communications":
    st.subheader("📢 Mensajes Importantes")
    mensaje = st.text_area("📝 Escribe un mensaje o anuncio")
    if st.button("📩 Enviar mensaje"):
        db.collection("communications").document().set({
            "usuario": "Enrique",
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "mensaje": mensaje
        })
        st.success("Mensaje enviado.")

# ----------------
# Calendar
# ----------------
elif choice == "Calendar":
    st.subheader("📅 Calendario")
    cal_option = st.radio("Selecciona una opción", ["Crear Evento", "Ver Calendario"])
    
    if cal_option == "Crear Evento":
        evento = st.text_input("📌 Nombre del evento")
        fecha_evento = st.date_input("📅 Selecciona la fecha")
        if st.button("✅ Agendar evento"):
            db.collection("calendar").document().set({
                "usuario": "Enrique",
                "evento": evento,
                "fecha": fecha_evento.strftime("%Y-%m-%d")
            })
            st.success("Evento agendado.")
    else:
        events_ref = db.collection("calendar")
        events_docs = events_ref.stream()
        events = []
        for doc in events_docs:
            data = doc.to_dict()
            events.append({
                "title": data.get("evento", "Evento"),
                "start": data.get("fecha")  # Se asume formato YYYY-MM-DD
            })
        events_json = json.dumps(events)
        
        calendar_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset='utf-8' />
          <link href='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.css' rel='stylesheet' />
          <script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.js'></script>
          <style>
            body {{
              margin: 0;
              padding: 0;
            }}
            #calendar {{
              max-width: 900px;
              margin: 40px auto;
            }}
          </style>
        </head>
        <body>
          <div id='calendar'></div>
          <script>
            document.addEventListener('DOMContentLoaded', function() {{
              var calendarEl = document.getElementById('calendar');
              var calendar = new FullCalendar.Calendar(calendarEl, {{
                initialView: 'dayGridMonth',
                events: {events_json}
              }});
              calendar.render();
            }});
          </script>
        </body>
        </html>
        """
        components.html(calendar_html, height=600, scrolling=True)
