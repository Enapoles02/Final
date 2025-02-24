import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import streamlit.components.v1 as components
import json

# -------------------------------------------------------------------
# Temporizador: Solo se inicia al presionar "Start Timer"
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

# -------------------------------------------------------------------
# Opciones de status con colores/íconos
# -------------------------------------------------------------------
status_options = {
    "Pendiente": "🔴 Pendiente",
    "En proceso": "🟡 En proceso",
    "Completado": "🟢 Completado"
}

# -------------------------------------------------------------------
# Interfaz de la aplicación
# -------------------------------------------------------------------
st.title("🔥 Daily Huddle - Enrique 🔥")
menu = ["Overview", "Attendance", "Top 3", "Action Board", "Communications", "Calendar"]
choice = st.sidebar.selectbox("📌 Selecciona una pestaña:", menu)

# ---------- OVERVIEW ----------
if choice == "Overview":
    st.subheader("📋 ¿Qué es el Daily Huddle?")
    st.write("""
    Bienvenido a tu Daily Huddle. Aquí podrás registrar tu asistencia, prioridades, acciones pendientes, reconocimientos, escalaciones y eventos importantes del equipo.
    \n👈 Usa la barra lateral para navegar entre las diferentes secciones.
    """)

# ---------- ATTENDANCE ----------
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
        db.collection("attendance").document("Enrique").set({
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "estado_animo": feelings[selected_feeling],
            "problema_salud": health_problem
        })
        st.success("Asistencia registrada correctamente.")

# ---------- TOP 3 ----------
elif choice == "Top 3":
    st.subheader("📌 Top 3 Prioridades - Resumen")
    
    # Mostrar resumen de tareas en Top 3 para el usuario "Enrique"
    tasks = list(db.collection("top3").where("usuario", "==", "Enrique").stream())
    if tasks:
        for task in tasks:
            task_data = task.to_dict()
            st.markdown(f"**{task_data.get('descripcion','')}**")
            st.write(f"Inicio: {task_data.get('fecha_inicio','')}  |  Compromiso: {task_data.get('fecha_compromiso','')}  |  Real: {task_data.get('fecha_real','')}")
            st.write(f"Status: {task_data.get('status','')}")
            st.write(f"Nivel de energía: {task_data.get('energia','')}")
            if task_data.get("reconocimiento"):
                st.info(f"Reconocimiento: {task_data.get('reconocimiento')}")
            if task_data.get("escalacion"):
                escal = task_data.get("escalacion")
                st.warning(f"Escalación -> Quien: {escal.get('quien','')}, Por: {escal.get('por','')}, Para: {escal.get('para','')}, Con: {escal.get('con','')}")
            if st.button("🗑️ Eliminar", key=f"delete_top3_{task.id}"):
                db.collection("top3").document(task.id).delete()
                st.success("Tarea eliminada. Recarga la página para ver el cambio.")
                try:
                    st.experimental_rerun()
                except Exception:
                    pass
    else:
        st.info("No hay tareas de Top 3 registradas.")
    
    # Botón para mostrar formulario de agregar tarea
    if st.button("➕ Agregar Tarea de Top 3"):
        st.session_state.show_top3_form = True
    if st.session_state.get("show_top3_form"):
        with st.form("top3_add_form"):
            st.markdown("### Nueva Tarea - Top 3")
            p = st.text_input("Descripción")
            ti = st.date_input("Fecha de inicio")
            tc = st.date_input("Fecha compromiso")
            s = st.selectbox("Status", list(status_options.keys()))
            energia = st.slider("Nivel de energía (0 a 5)", 0, 5, 3)
            reconocimiento = st.text_area("Mensaje de reconocimiento (opcional)")
            st.markdown("#### Datos de Escalación (opcional)")
            escal_quien = st.text_input("Quien escala")
            escal_por = st.text_input("Por qué")
            escal_para = st.text_input("Para quién")
            escal_con = st.text_input("Con quién se tiene el tema")
            submit_new_top3 = st.form_submit_button("Guardar tarea")
        if submit_new_top3:
            fecha_real = datetime.now().strftime("%Y-%m-%d") if s == "Completado" else ""
            escalacion = None
            if escal_quien or escal_por or escal_para or escal_con:
                escalacion = {
                    "quien": escal_quien,
                    "por": escal_por,
                    "para": escal_para,
                    "con": escal_con
                }
            db.collection("top3").add({
                "usuario": "Enrique",
                "descripcion": p,
                "fecha_inicio": ti.strftime("%Y-%m-%d"),
                "fecha_compromiso": tc.strftime("%Y-%m-%d"),
                "fecha_real": fecha_real,
                "status": status_options[s],
                "energia": energia,
                "reconocimiento": reconocimiento,
                "escalacion": escalacion,
                "timestamp": datetime.now()
            })
            st.success("Tarea de Top 3 guardada.")
            st.session_state.show_top3_form = False
            try:
                st.experimental_rerun()
            except Exception:
                pass

# ---------- ACTION BOARD ----------
elif choice == "Action Board":
    st.subheader("✅ Acciones y Seguimiento - Resumen")
    
    # Mostrar resumen de acciones en Action Board para el usuario "Enrique"
    actions = list(db.collection("actions").where("usuario", "==", "Enrique").stream())
    if actions:
        for action in actions:
            act_data = action.to_dict()
            st.markdown(f"**{act_data.get('accion','')}**")
            st.write(f"Inicio: {act_data.get('fecha_inicio','')}  |  Compromiso: {act_data.get('fecha_compromiso','')}  |  Real: {act_data.get('fecha_real','')}")
            st.write(f"Status: {act_data.get('status','')}")
            st.write(f"Nivel de energía: {act_data.get('energia','')}")
            if act_data.get("reconocimiento"):
                st.info(f"Reconocimiento: {act_data.get('reconocimiento')}")
            if act_data.get("escalacion"):
                escal = act_data.get("escalacion")
                st.warning(f"Escalación -> Quien: {escal.get('quien','')}, Por: {escal.get('por','')}, Para: {escal.get('para','')}, Con: {escal.get('con','')}")
            if st.button("🗑️ Eliminar", key=f"delete_action_{action.id}"):
                db.collection("actions").document(action.id).delete()
                st.success("Acción eliminada. Recarga la página para ver el cambio.")
                try:
                    st.experimental_rerun()
                except Exception:
                    pass
    else:
        st.info("No hay acciones registradas.")
    
    # Botón para mostrar formulario de agregar acción
    if st.button("➕ Agregar Acción"):
        st.session_state.show_action_form = True
    if st.session_state.get("show_action_form"):
        with st.form("action_add_form"):
            st.markdown("### Nueva Acción")
            accion = st.text_input("Descripción de la acción")
            ti = st.date_input("Fecha de inicio")
            tc = st.date_input("Fecha compromiso")
            status = st.selectbox("Status", list(status_options.keys()))
            energia = st.slider("Nivel de energía (0 a 5)", 0, 5, 3)
            reconocimiento = st.text_area("Mensaje de reconocimiento (opcional)")
            st.markdown("#### Datos de Escalación (opcional)")
            escal_quien = st.text_input("Quien escala")
            escal_por = st.text_input("Por qué")
            escal_para = st.text_input("Para quién")
            escal_con = st.text_input("Con quién se tiene el tema")
            submit_new_action = st.form_submit_button("Guardar acción")
        if submit_new_action:
            fecha_real = datetime.now().strftime("%Y-%m-%d") if status == "Completado" else ""
            escalacion = None
            if escal_quien or escal_por or escal_para or escal_con:
                escalacion = {
                    "quien": escal_quien,
                    "por": escal_por,
                    "para": escal_para,
                    "con": escal_con
                }
            db.collection("actions").add({
                "usuario": "Enrique",
                "accion": accion,
                "fecha_inicio": ti.strftime("%Y-%m-%d"),
                "fecha_compromiso": tc.strftime("%Y-%m-%d"),
                "fecha_real": fecha_real,
                "status": status_options[status],
                "energia": energia,
                "reconocimiento": reconocimiento,
                "escalacion": escalacion,
                "fecha": datetime.now().strftime("%Y-%m-%d")
            })
            st.success("Acción guardada.")
            st.session_state.show_action_form = False
            try:
                st.experimental_rerun()
            except Exception:
                pass

# ---------- COMMUNICATIONS ----------
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

# ---------- CALENDAR ----------
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
        # Recuperar eventos de Firestore
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
         
