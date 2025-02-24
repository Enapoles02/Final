import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import streamlit.components.v1 as components
import json

# -------------------------------------------------------------------
# Encabezado: Solo el título (sin imagen)
# -------------------------------------------------------------------
st.title("🔥 Daily Huddle - Enrique")

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

# Función para combinar status y status personalizado
def get_status(selected, custom):
    return custom.strip() if custom and custom.strip() != "" else selected

# Diccionario para colores de status
status_colors = {
    "Pendiente": "red",
    "En proceso": "orange",
    "Completado": "green"
}

# -------------------------------------------------------------------
# Menú principal
# -------------------------------------------------------------------
st.markdown("---")
menu = ["Overview", "Attendance", "Recognition", "Escalations", "Top 3", "Action Board", "Communications", "Calendar"]
choice = st.sidebar.selectbox("📌 Selecciona una pestaña:", menu)

# ----------------
# Overview
# ----------------
if choice == "Overview":
    st.subheader("📋 ¿Qué es el Daily Huddle?")
    st.write("""
    Bienvenido a tu Daily Huddle. Aquí podrás registrar tu asistencia, prioridades, acciones, 
    reconocimientos, escalaciones y eventos importantes del equipo.
    \n👈 Usa la barra lateral para navegar entre las diferentes secciones.
    """)

# ----------------
# Attendance
# ----------------
elif choice == "Attendance":
    st.subheader("📝 Registro de Asistencia")
    today_date = datetime.now().strftime("%Y-%m-%d")
    attendance_doc = db.collection("attendance").document("Enrique").get()
    if attendance_doc.exists:
        data = attendance_doc.to_dict()
        if data.get("fecha") != today_date:
            db.collection("attendance").document("Enrique").delete()
    
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
    
    st.write("Nivel de energía:")
    energy_options = ["Nivel 1", "Nivel 2", "Nivel 3", "Nivel 4", "Nivel 5"]
    energy_level = st.radio("Selecciona tu nivel de energía:", options=energy_options, horizontal=True)
    level_mapping = {
        "Nivel 1": 20,
        "Nivel 2": 40,
        "Nivel 3": 60,
        "Nivel 4": 80,
        "Nivel 5": 100
    }
    fill_percent = level_mapping[energy_level]
    battery_html = f"""
    <div style="display: inline-block; border: 2px solid #000; width: 40px; height: 100px; position: relative;">
      <div style="position: absolute; bottom: 0; width: 100%; height: {fill_percent}%; background-color: #00ff00;"></div>
    </div>
    """
    st.markdown(battery_html, unsafe_allow_html=True)
    
    if st.button("✅ Registrar asistencia"):
         db.collection("attendance").document("Enrique").set({
             "fecha": today_date,
             "estado_animo": feelings[selected_feeling],
             "problema_salud": health_problem,
             "energia": energy_level
         })
         st.success("Asistencia registrada correctamente.")

# ----------------
# Recognition
# ----------------
elif choice == "Recognition":
    st.subheader("🎉 Recognition")
    st.write("Envía un reconocimiento a un compañero.")
    with st.form("recognition_form"):
        destinatario = st.text_input("Email del destinatario")
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
# Escalations
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
# Top 3: Tareas y prioridades (con edición de status)
# ----------------
elif choice == "Top 3":
    st.subheader("📌 Top 3 Prioridades - Resumen")
    top3_container = st.empty()
    def load_top3():
        tasks = list(db.collection("top3").where("usuario", "==", "Enrique").stream())
        top3_container.empty()
        with top3_container.container():
            st.markdown("---")
            if tasks:
                for task in tasks:
                    task_id = task.id
                    task_data = task.to_dict()
                    st.markdown(f"**{task_data.get('descripcion','(Sin descripción)')}**")
                    st.write(f"Inicio: {task_data.get('fecha_inicio','')} | Compromiso: {task_data.get('fecha_compromiso','')} | Real: {task_data.get('fecha_real','')}")
                    
                    status_val = task_data.get('status', '')
                    color = status_colors.get(status_val, "black")
                    st.markdown(f"**Status actual:** <span style='color: {color};'>{status_val}</span>", unsafe_allow_html=True)
                    
                    new_status = st.selectbox(
                        "Editar status",
                        ["Pendiente", "En proceso", "Completado"],
                        index=(["Pendiente", "En proceso", "Completado"].index(status_val)
                               if status_val in ["Pendiente", "En proceso", "Completado"] else 0),
                        key=f"select_top3_{task_id}"
                    )
                    custom_status = st.text_input("Status personalizado (opcional)", key=f"custom_top3_{task_id}")
                    
                    if st.button("Actualizar Status", key=f"update_top3_{task_id}"):
                        final_status = get_status(new_status, custom_status)
                        if final_status.lower() == "completado":
                            fecha_real = datetime.now().strftime("%Y-%m-%d")
                        else:
                            fecha_real = task_data.get("fecha_real", "")
                        db.collection("top3").document(task_id).update({
                            "status": final_status,
                            "fecha_real": fecha_real
                        })
                        st.success("Status actualizado.")
                        try:
                            load_top3()
                        except Exception:
                            pass
                    
                    if st.button("🗑️ Eliminar", key=f"delete_top3_{task_id}"):
                        db.collection("top3").document(task_id).delete()
                        st.success("Tarea eliminada.")
                        try:
                            load_top3()
                        except Exception:
                            pass
                    st.markdown("---")
            else:
                st.info("No hay tareas de Top 3 registradas.")
    load_top3()
    
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
                load_top3()
            except Exception:
                pass

# ----------------
# Action Board: Acciones y seguimiento (con edición de status)
# ----------------
elif choice == "Action Board":
    st.subheader("✅ Acciones y Seguimiento - Resumen")
    action_container = st.empty()
    def load_actions():
        actions = list(db.collection("actions").where("usuario", "==", "Enrique").stream())
        action_container.empty()
        with action_container.container():
            st.markdown("---")
            if actions:
                for action in actions:
                    action_id = action.id
                    act_data = action.to_dict()
                    st.markdown(f"**{act_data.get('accion','(Sin descripción)')}**")
                    st.write(f"Inicio: {act_data.get('fecha_inicio','')} | Compromiso: {act_data.get('fecha_compromiso','')} | Real: {act_data.get('fecha_real','')}")
                    
                    status_val = act_data.get('status', '')
                    color = status_colors.get(status_val, "black")
                    st.markdown(f"**Status actual:** <span style='color: {color};'>{status_val}</span>", unsafe_allow_html=True)
                    
                    new_status = st.selectbox(
                        "Editar status",
                        ["Pendiente", "En proceso", "Completado"],
                        index=(["Pendiente", "En proceso", "Completado"].index(status_val)
                               if status_val in ["Pendiente", "En proceso", "Completado"] else 0),
                        key=f"select_action_{action_id}"
                    )
                    custom_status = st.text_input("Status personalizado (opcional)", key=f"custom_action_{action_id}")
                    
                    if st.button("Actualizar Status", key=f"update_action_{action_id}"):
                        final_status = get_status(new_status, custom_status)
                        if final_status.lower() == "completado":
                            fecha_real = datetime.now().strftime("%Y-%m-%d")
                        else:
                            fecha_real = act_data.get("fecha_real", "")
                        db.collection("actions").document(action_id).update({
                            "status": final_status,
                            "fecha_real": fecha_real
                        })
                        st.success("Status actualizado.")
                        try:
                            load_actions()
                        except Exception:
                            pass
                    
                    if st.button("🗑️ Eliminar", key=f"delete_action_{action_id}"):
                        db.collection("actions").document(action_id).delete()
                        st.success("Acción eliminada.")
                        try:
                            load_actions()
                        except Exception:
                            pass
                    st.markdown("---")
            else:
                st.info("No hay acciones registradas.")
    try:
        load_actions()
    except Exception:
        pass
    
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
                load_actions()
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
                "start": data.get("fecha")
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
