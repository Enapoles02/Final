import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, date
import streamlit.components.v1 as components
import json, random
import pandas as pd

# ================================
# Definición de usuarios y áreas
# ================================
valid_users = {
    # R2R NAMER:
    "VREYES": "Reyes Escorsia Victor Manuel",
    "RCRUZ": "Cruz Madariaga Rodrigo",
    "AZENTENO": "Zenteno Perez Alejandro",
    "XGUTIERREZ": "Gutierrez Hernandez Ximena",
    "CNAPOLES": "Napoles Escalante Christopher Enrique",
    "MCANO": "Marco Antonio Cano Calzada"
    # R2R LATAM:
    # (Miriam Sanchez se retira de este grupo)
    "MHERNANDEZ": "Hernandez Ponce Maria Guadalupe",
    "MGARCIA": "Garcia Vazquez Mariana Aketzalli",
    "PSARACHAGA": "Paula Sarachaga",
    # TL para GL NAMER & LATAM:
    "ALECCION": "TL GL NAMER LATAM",
    # R2R GRAL:
    "ANDRES": "Andres",
    "MIRIAMGRAL": "Miriam GRAL",
    "YAEL": "Yael",
    "R2RGRAL": "TL R2R GRAL",
    "MSANCHEZ": "Miriam Sanchez",  # Ahora en grupo R2R GRAL
    # WOR SGBS:
    "MLOPEZ": "Miguel Lopez",
    "GMAJORAL": "Guillermo Mayoral",
    "BOSNAYA": "Becerril Osnaya",
    "JTHIAGO": "Jose Thiago",
    "IOROZCO": "Isaac Orozco",
    "WORLEAD": "TL WOR SGBS",
    # RH para WOR SGBS (monedas):
    "LARANDA": "RH - Luis Aranda",
    # FA:
    "GAVILES": "Gabriel Aviles",
    "JLOPEZ": "Jesus Lopez",
    "FALEAD": "TL FA",
    "ABARRERA": "Andres Barrera",
    # IC:
    "CCIBARRA": "Carlos Candelas Ibarra",
    "LEDYANEZ": "Luis Enrique Delhumeau Yanez",
    "EIMARTINEZ": "Elizabeth Ibanez Martinez",
    "ICLEAD": "TL IC"
}

group_namer    = {"VREYES", "RCRUZ", "AZENTENO", "XGUTIERREZ", "CNAPOLES", "MCANO"}
group_latam    = {"MHERNANDEZ", "MGARCIA", "PSARACHAGA"}
group_r2r_gral = {"ANDRES", "MIRIAMGRAL", "YAEL", "R2RGRAL", "MSANCHEZ"}
group_wor      = {"MLOPEZ", "GMAJORAL", "BOSNAYA", "JTHIAGO", "IOROZCO", "WORLEAD", "LARANDA"}
group_fa       = {"GAVILES", "JLOPEZ", "FALEAD", "ABARRERA"}
group_ic       = {"CCIBARRA", "LEDYANEZ", "EIMARTINEZ", "ICLEAD"}

# ================================
# Pantalla de Login
# ================================
if "user_code" not in st.session_state:
    st.session_state["user_code"] = None

def show_login():
    st.title("🔥 Daily Huddle - Login")
    st.write("Ingresa tu código de usuario")
    user_input = st.text_input("Código de usuario:", max_chars=20)
    if st.button("Ingresar"):
        user_input = user_input.strip().upper()
        if user_input in valid_users:
            st.session_state.user_code = user_input
            st.success(f"¡Bienvenido, {valid_users[user_input]}!")
            try:
                st.experimental_rerun()
            except Exception:
                pass
        else:
            st.error("Código de usuario inválido. Intenta nuevamente.")

if st.session_state["user_code"] is None:
    show_login()
    st.stop()

# ================================
# Función para agrupar tareas por área
# ================================
def group_tasks_by_area(tasks):
    groups = {
        "NAMER": {},
        "LATAM": {},
        "R2R GRAL": {},
        "WOR SGBS": {},
        "FA": {},
        "IC": {},
        "Sin Región": {}
    }
    for task in tasks:
        data = task.to_dict()
        data["id"] = task.id
        user = data.get("usuario")
        if isinstance(user, list) and len(user) > 0:
            primary = user[0]
        elif isinstance(user, str):
            primary = user
        else:
            primary = "Sin Usuario"
        if primary in group_namer:
            area = "NAMER"
        elif primary in group_latam:
            area = "LATAM"
        elif primary in group_r2r_gral:
            area = "R2R GRAL"
        elif primary in group_wor:
            area = "WOR SGBS"
        elif primary in group_fa:
            area = "FA"
        elif primary in group_ic:
            area = "IC"
        else:
            area = "Sin Región"
        if primary not in groups[area]:
            groups[area][primary] = []
        groups[area][primary].append(data)
    return {a: groups[a] for a in groups if groups[a]}

# ================================
# Repositorio de actividades (simulado)
# ================================
activity_repo = [
    "Reunión de planificación corporativa",
    "Actualización de estrategia logística",
    "Análisis de desempeño trimestral",
    "Sesión de brainstorming para innovación"
]

# ================================
# Inicialización de Firebase usando secrets (TOML)
# ================================
def init_firebase():
    firebase_config = st.secrets["firebase"]
    if not isinstance(firebase_config, dict):
        firebase_config = firebase_config.to_dict()
    try:
        cred = credentials.Certificate(firebase_config)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        return db
    except Exception as e:
        st.error(f"Error al inicializar Firebase: {e}")
        st.stop()

db = init_firebase()

# ================================
# Función para determinar el jefe directo según el destinatario
# ================================
def get_direct_boss(destinatario_code):
    if destinatario_code in (group_namer.union(group_latam)):
        return "ALECCION"
    elif destinatario_code in group_r2r_gral:
        return "R2RGRAL"
    elif destinatario_code in group_wor:
        return "WORLEAD"
    elif destinatario_code in group_fa:
        return "FALEAD"
    elif destinatario_code in group_ic:
        return "ICLEAD"
    else:
        return "N/A"

# ================================
# App Principal
# ================================
def show_main_app():
    user_code = st.session_state["user_code"]

    st.image(
        "http://bulk-distributor.com/wp-content/uploads/2016/01/DB-Schenker-Hub-Salzburg.jpg",
        caption="DB Schenker",
        use_container_width=True
    )
    
    st.title("🔥 Daily Huddle")
    st.markdown(f"**Usuario:** {valid_users[user_code]}  ({user_code})")
    
    menu_choice = st.sidebar.selectbox("📌 Selecciona una pestaña:", 
                                         ["Asistencia", "Top 3", "Action Board", "Escalation", "Recognition", "Store DBSCHENKER", "Wallet", "Communications", "Calendar", "Roles", "Compliance", "Todas las Tareas"])
    
    # ------------------- Asistencia -------------------
    if menu_choice == "Asistencia":
        st.subheader("📝 Registro de Asistencia")
        today_date = datetime.now().strftime("%Y-%m-%d")
        attendance_doc = db.collection("attendance").document(user_code).get()
        if attendance_doc.exists:
            data = attendance_doc.to_dict()
            if data.get("fecha") != today_date:
                db.collection("attendance").document(user_code).delete()
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
        st.write("Nivel de energía (elige 10, 20, 30, 40 o 50):")
        energy_options = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        energy_level = st.radio("Nivel de energía:", options=energy_options, horizontal=True)
        # Representación en forma de "batería" (barra vertical)
        battery_html = f"""
        <div style="display: inline-block; border: 2px solid #000; width: 40px; height: 100px; position: relative;">
          <div style="position: absolute; bottom: 0; width: 100%; height: {energy_level}%; background-color: #00ff00;"></div>
        </div>
        """
        st.markdown(battery_html, unsafe_allow_html=True)
        if st.button("✅ Registrar asistencia"):
            db.collection("attendance").document(user_code).set({
                "fecha": today_date,
                "estado_animo": feelings[selected_feeling],
                "problema_salud": health_problem,
                "energia": energy_level
            })
            st.success("Asistencia registrada correctamente.")
    
    # ------------------- Asistencia Resumen para TL -------------------
    elif menu_choice == "Asistencia" and user_code in {"ALECCION", "WORLEAD", "R2RGRAL", "FALEAD", "ICLEAD"}:
        # Si TL desea ver resumen, se puede agregar una pestaña adicional (aquí se usa "Asistencia" para fines de ejemplo)
        st.subheader("📊 Resumen de Asistencia (Gráfico)")
        # Filtrar registros según el grupo del TL
        if user_code == "ALECCION":
            team = [u for u in valid_users if u in group_namer or u in group_latam]
        elif user_code == "WORLEAD":
            team = [u for u in valid_users if u in group_wor]
        elif user_code == "R2RGRAL":
            team = [u for u in valid_users if u in group_r2r_gral]
        elif user_code == "FALEAD":
            team = [u for u in valid_users if u in group_fa]
        elif user_code == "ICLEAD":
            team = [u for u in valid_users if u in group_ic]
        else:
            team = [user_code]
        data_list = []
        for u in team:
            doc = db.collection("attendance").document(u).get()
            if doc.exists:
                info = doc.to_dict()
                energy = info.get("energia", 0)
                data_list.append({"Usuario": valid_users.get(u, u), "Energía": energy})
        if data_list:
            df = pd.DataFrame(data_list)
            st.bar_chart(df.set_index("Usuario"))
        else:
            st.info("No hay datos de asistencia para mostrar.")
    
    # ------------------- Top 3 -------------------
    elif menu_choice == "Top 3":
        st.subheader("📌 Top 3 Prioridades - Resumen")
        all_tasks = list(db.collection("top3").stream())
        tasks = []
        if user_code == "ALECCION":
            for task in all_tasks:
                data = task.to_dict()
                user_field = data.get("usuario")
                primary = user_field[0] if isinstance(user_field, list) else user_field
                if primary in group_namer or primary in group_latam:
                    tasks.append(task)
        elif user_code == "WORLEAD":
            for task in all_tasks:
                data = task.to_dict()
                primary = data.get("usuario")[0] if isinstance(data.get("usuario"), list) else data.get("usuario")
                if primary in group_wor:
                    tasks.append(task)
        elif user_code == "R2RGRAL":
            for task in all_tasks:
                data = task.to_dict()
                primary = data.get("usuario")[0] if isinstance(data.get("usuario"), list) else data.get("usuario")
                if primary in group_r2r_gral:
                    tasks.append(task)
        elif user_code == "FALEAD":
            for task in all_tasks:
                data = task.to_dict()
                primary = data.get("usuario")[0] if isinstance(data.get("usuario"), list) else data.get("usuario")
                if primary in group_fa:
                    tasks.append(task)
        elif user_code == "ICLEAD":
            for task in all_tasks:
                data = task.to_dict()
                primary = data.get("usuario")[0] if isinstance(data.get("usuario"), list) else data.get("usuario")
                if primary in group_ic:
                    tasks.append(task)
        else:
            tasks = list(db.collection("top3").where("usuario", "==", user_code).stream())
        groups = group_tasks_by_area(tasks)
        status_colors = {"Pendiente": "red", "En proceso": "orange", "Completado": "green"}
        def get_status(selected, custom):
            return custom.strip() if custom and custom.strip() != "" else selected
        for area, user_groups in groups.items():
            st.markdown(f"#### Área: {area}")
            for u, t_list in user_groups.items():
                st.markdown(f"**Usuario: {valid_users.get(u, u)}**")
                for task_data in t_list:
                    st.markdown(f"- [TOP 3] {task_data.get('descripcion','(Sin descripción)')}")
                    st.write(f"Inicio: {task_data.get('fecha_inicio','')}, Compromiso: {task_data.get('fecha_compromiso','')}, Real: {task_data.get('fecha_real','')}")
                    status_val = task_data.get('status','')
                    color = status_colors.get(status_val, "black")
                    st.markdown(f"Status: <span style='color:{color};'>{status_val}</span>", unsafe_allow_html=True)
                    new_status = st.selectbox(
                        "Editar status",
                        ["Pendiente", "En proceso", "Completado"],
                        index=(["Pendiente", "En proceso", "Completado"].index(status_val) if status_val in ["Pendiente", "En proceso", "Completado"] else 0),
                        key=f"top3_status_{task_data.get('id')}"
                    )
                    custom_status = st.text_input("Status personalizado (opcional)", key=f"top3_custom_{task_data.get('id')}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Actualizar Status", key=f"update_top3_{task_data.get('id')}"):
                            final_status = get_status(new_status, custom_status)
                            fecha_real = datetime.now().strftime("%Y-%m-%d") if final_status.lower() == "completado" else task_data.get("fecha_real", "")
                            db.collection("top3").document(task_data.get("id")).update({
                                "status": final_status,
                                "fecha_real": fecha_real
                            })
                            st.success("Status actualizado.")
                    with col2:
                        if st.button("🗑️ Eliminar", key=f"delete_top3_{task_data.get('id')}"):
                            db.collection("top3").document(task_data.get("id")).delete()
                            st.success("Tarea eliminada.")
                    st.markdown("---")
        if st.button("➕ Agregar Tarea de Top 3"):
            st.session_state.show_top3_form = True
        if st.session_state.get("show_top3_form"):
            with st.form("top3_add_form"):
                st.markdown("### Nueva Tarea - Top 3")
                selected_activity = st.selectbox("Selecciona actividad predefinida (opcional)", [""] + activity_repo)
                p = selected_activity if selected_activity != "" else st.text_input("Descripción")
                ti = st.date_input("Fecha de inicio")
                tc = st.date_input("Fecha compromiso")
                s = st.selectbox("Status", ["Pendiente", "En proceso", "Completado"], key="top3_new_status")
                custom_status = st.text_input("Status personalizado (opcional)", key="top3_new_custom")
                colaboradores = st.multiselect("Colaboradores (opcional)", options=[code for code in valid_users if code != user_code],
                                                 format_func=lambda x: f"{valid_users[x]} ({x})")
                privado = st.checkbox("Marcar como privado")
                submit_new_top3 = st.form_submit_button("Guardar tarea")
            if submit_new_top3:
                final_status = get_status(s, custom_status)
                fecha_real = datetime.now().strftime("%Y-%m-%d") if final_status.lower() == "completado" else ""
                data = {
                    "usuario": user_code if not colaboradores else [user_code] + colaboradores,
                    "descripcion": p,
                    "fecha_inicio": ti.strftime("%Y-%m-%d"),
                    "fecha_compromiso": tc.strftime("%Y-%m-%d"),
                    "fecha_real": fecha_real,
                    "status": final_status,
                    "privado": privado,
                    "timestamp": datetime.now()
                }
                db.collection("top3").add(data)
                st.success("Tarea de Top 3 guardada.")
                st.session_state.show_top3_form = False
    
    # ------------------- Action Board -------------------
    elif menu_choice == "Action Board":
        st.subheader("✅ Acciones y Seguimiento - Resumen")
        all_actions = list(db.collection("actions").stream())
        actions = []
        if user_code == "ALECCION":
            for task in all_actions:
                data = task.to_dict()
                primary = data.get("usuario")[0] if isinstance(data.get("usuario"), list) else data.get("usuario")
                if primary in group_namer or primary in group_latam:
                    actions.append(task)
        elif user_code == "WORLEAD":
            for task in all_actions:
                data = task.to_dict()
                primary = data.get("usuario")[0] if isinstance(data.get("usuario"), list) else data.get("usuario")
                if primary in group_wor:
                    actions.append(task)
        elif user_code == "R2RGRAL":
            for task in all_actions:
                data = task.to_dict()
                primary = data.get("usuario")[0] if isinstance(data.get("usuario"), list) else data.get("usuario")
                if primary in group_r2r_gral:
                    actions.append(task)
        elif user_code == "FALEAD":
            for task in all_actions:
                data = task.to_dict()
                primary = data.get("usuario")[0] if isinstance(data.get("usuario"), list) else data.get("usuario")
                if primary in group_fa:
                    actions.append(task)
        elif user_code == "ICLEAD":
            for task in all_actions:
                data = task.to_dict()
                primary = data.get("usuario")[0] if isinstance(data.get("usuario"), list) else data.get("usuario")
                if primary in group_ic:
                    actions.append(task)
        else:
            actions = list(db.collection("actions").where("usuario", "==", user_code).stream())
        groups_actions = group_tasks_by_area(actions)
        status_colors = {"Pendiente": "red", "En proceso": "orange", "Completado": "green"}
        def get_status(selected, custom):
            return custom.strip() if custom and custom.strip() != "" else selected
        for area, user_groups in groups_actions.items():
            st.markdown(f"#### Área: {area}")
            for u, acts in user_groups.items():
                st.markdown(f"**Usuario: {valid_users.get(u, u)}**")
                for act_data in acts:
                    st.markdown(f"- [Action Board] {act_data.get('accion','(Sin descripción)')}")
                    st.write(f"Inicio: {act_data.get('fecha_inicio','')}, Compromiso: {act_data.get('fecha_compromiso','')}, Real: {act_data.get('fecha_real','')}")
                    status_val = act_data.get('status','')
                    color = status_colors.get(status_val, "black")
                    st.markdown(f"Status: <span style='color:{color};'>{status_val}</span>", unsafe_allow_html=True)
                    new_status = st.selectbox(
                        "Editar status",
                        ["Pendiente", "En proceso", "Completado"],
                        index=(["Pendiente", "En proceso", "Completado"].index(status_val) if status_val in ["Pendiente", "En proceso", "Completado"] else 0),
                        key=f"action_status_{act_data.get('id')}"
                    )
                    custom_status = st.text_input("Status personalizado (opcional)", key=f"action_custom_{act_data.get('id')}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Actualizar Status", key=f"update_action_{act_data.get('id')}"):
                            final_status = get_status(new_status, custom_status)
                            fecha_real = datetime.now().strftime("%Y-%m-%d") if final_status.lower() == "completado" else act_data.get("fecha_real", "")
                            db.collection("actions").document(act_data.get("id")).update({
                                "status": final_status,
                                "fecha_real": fecha_real
                            })
                            st.success("Status actualizado.")
                    with col2:
                        if st.button("🗑️ Eliminar", key=f"delete_action_{act_data.get('id')}"):
                            db.collection("actions").document(act_data.get("id")).delete()
                            st.success("Acción eliminada.")
                    st.markdown("---")
        if st.button("➕ Agregar Acción"):
            st.session_state.show_action_form = True
        if st.session_state.get("show_action_form"):
            with st.form("action_add_form"):
                st.markdown("### Nueva Acción")
                accion = st.text_input("Descripción de la acción")
                ti = st.date_input("Fecha de inicio")
                tc = st.date_input("Fecha compromiso")
                s = st.selectbox("Status", ["Pendiente", "En proceso", "Completado"], key="action_new_status")
                custom_status = st.text_input("Status personalizado (opcional)", key="action_new_custom")
                colaboradores = st.multiselect("Colaboradores (opcional)", options=[code for code in valid_users if code != user_code],
                                                 format_func=lambda x: f"{valid_users[x]} ({x})")
                privado = st.checkbox("Marcar como privado")
                submit_new_action = st.form_submit_button("Guardar acción")
            if submit_new_action:
                final_status = custom_status.strip() if custom_status.strip() != "" else s
                fecha_real = datetime.now().strftime("%Y-%m-%d") if final_status.lower() == "completado" else ""
                data = {
                    "usuario": user_code if not colaboradores else [user_code] + colaboradores,
                    "accion": accion,
                    "fecha_inicio": ti.strftime("%Y-%m-%d"),
                    "fecha_compromiso": tc.strftime("%Y-%m-%d"),
                    "fecha_real": fecha_real,
                    "status": final_status,
                    "privado": privado,
                    "timestamp": datetime.now()
                }
                db.collection("actions").add(data)
                st.success("Acción guardada.")
                st.session_state.show_action_form = False
    
    # ------------------- Escalation -------------------
    elif menu_choice == "Escalation":
        st.subheader("⚠️ Escalation")
        escalador = user_code
        common_options = {"MLOPEZ", "GMAJORAL", "LARANDA"}
        if user_code in group_fa:
            additional = {"ABARRERA"}
        elif user_code in group_ic:
            additional = {"YAEL"}
        elif user_code in (group_namer.union(group_latam)):
            additional = {"MSANCHEZ"}
        elif user_code in group_wor:
            additional = set()
        else:
            additional = set()
        para_quien_options = sorted(list(common_options.union(additional)))
        para_quien = st.selectbox("¿Para quién?", para_quien_options, format_func=lambda x: f"{valid_users.get(x, x)} ({x})")
        with st.form("escalation_form"):
            razon = st.text_area("Razón")
            con_quien = st.multiselect("¿Con quién se tiene el tema?", options=[code for code in valid_users if code != escalador],
                                         format_func=lambda x: f"{valid_users.get(x, x)} ({x})")
            submit_escalation = st.form_submit_button("Enviar escalación")
        if submit_escalation:
            involucrados = [escalador, para_quien]
            if con_quien:
                involucrados.extend(con_quien)
            involucrados = list(set(involucrados))
            escalacion_data = {
                "escalador": escalador,
                "razon": razon,
                "para_quien": para_quien,
                "con_quien": con_quien,
                "involucrados": involucrados,
                "fecha": datetime.now().strftime("%Y-%m-%d")
            }
            db.collection("escalations").add(escalacion_data)
            st.success("Escalación registrada.")
            st.warning(f"Notificación: Se ha enviado un escalation a {valid_users.get(para_quien, para_quien)}.")
        st.markdown("### Escalaciones en las que estás involucrado")
        escalations = list(db.collection("escalations").stream())
        count = 0
        for esc in escalations:
            esc_data = esc.to_dict()
            if user_code in esc_data.get("involucrados", []):
                count += 1
                st.markdown(f"**Escalación:** {esc_data.get('razon','(Sin razón)')}")
                st.write(f"Escalador: {esc_data.get('escalador','')}, Para quién: {esc_data.get('para_quien','')}, Con quién: {esc_data.get('con_quien','')}")
                st.write(f"Fecha: {esc_data.get('fecha','')}")
                st.warning("¡Estás involucrado en esta escalación!")
                st.markdown("---")
        if count == 0:
            st.info("No tienes escalaciones asignadas.")
    
    # ------------------- Recognition -------------------
    elif menu_choice == "Recognition":
        st.subheader("🎉 Recognition")
        with st.form("recognition_form"):
            st.markdown(f"**De:** {valid_users[user_code]} ({user_code})")
            # Seleccionar destinatario de la lista de usuarios activos (excluyendo el usuario actual)
            destinatario = st.selectbox("Para:", [code for code in valid_users if code != user_code],
                                          format_func=lambda x: f"{valid_users[x]} ({x})")
            # Determinar jefe directo del destinatario
            jefe_directo = get_direct_boss(destinatario)
            st.markdown(f"**Jefe Directo:** {valid_users.get(jefe_directo, jefe_directo)} ({jefe_directo})")
            kudo_options = [
                "Great Job! – ¡Excelente trabajo!",
                "Well Done! – ¡Bien hecho!",
                "Outstanding! – ¡Sobresaliente!",
                "Keep it up! – ¡Sigue así!"
            ]
            kudo_card = st.selectbox("Kudo Card:", kudo_options)
            subject = st.text_input("Asunto:", value="Kudo Card de Daily Huddle")
            mensaje = st.text_area("Mensaje:")
            submit_recognition = st.form_submit_button("Enviar Recognition")
        if submit_recognition:
            body = f"KUDO CARD: {kudo_card}\n\n{mensaje}"
            recognition_data = {
                "usuario": user_code,
                "destinatario": destinatario,
                "jefe_directo": jefe_directo,
                "asunto": subject,
                "mensaje": body,
                "fecha": datetime.now().strftime("%Y-%m-%d")
            }
            db.collection("recognitions").add(recognition_data)
            st.success("Recognition registrada correctamente.")
            st.warning(f"Notificación: Se ha enviado un Recognition a {valid_users.get(destinatario, destinatario)}.")
    
    # ------------------- Store DBSCHENKER -------------------
    elif menu_choice == "Store DBSCHENKER":
        st.subheader("🛍️ Store DBSCHENKER")
        st.write("Productos corporativos (prototipo):")
        products = [
            {"name": "Taza DBS", "price": 10, "image": "https://via.placeholder.com/150?text=Taza+DBS"},
            {"name": "Playera DBS", "price": 20, "image": "https://via.placeholder.com/150?text=Playera+DBS"},
            {"name": "Gorra DBS", "price": 15, "image": "https://via.placeholder.com/150?text=Gorra+DBS"}
        ]
        for prod in products:
            st.image(prod["image"], width=150)
            st.markdown(f"**{prod['name']}** - {prod['price']} DB COINS")
            if st.button(f"Comprar {prod['name']}", key=f"buy_{prod['name']}"):
                st.info("Función de compra no implementada.")
            st.markdown("---")
    
    # ------------------- Wallet -------------------
    elif menu_choice == "Wallet":
        st.subheader("💰 Mi Wallet (DB COINS)")
        wallet_ref = db.collection("wallets").document(user_code)
        doc = wallet_ref.get()
        current_coins = 0
        if doc.exists:
            current_coins = doc.to_dict().get("coins", 0)
        st.write(f"**Saldo actual:** {current_coins} DB COINS")
        if user_code == "LARANDA":
            add_coins = st.number_input("Generar DB COINS:", min_value=1, step=1, value=10)
            if st.button("Generar DB COINS"):
                new_balance = current_coins + add_coins
                wallet_ref.set({"coins": new_balance})
                st.success(f"Generados {add_coins} DB COINS. Nuevo saldo: {new_balance}.")
            st.markdown("### Funciones Administrativas")
            admin_key = st.text_input("Clave Admin", type="password")
            if admin_key == "ADMIN123":
                if st.button("Resetear todas las monedas a 0"):
                    for u in valid_users:
                        db.collection("wallets").document(u).set({"coins": 0})
                target = st.selectbox("Generar monedas para el usuario:", list(valid_users.keys()), format_func=lambda x: f"{valid_users[x]} ({x})")
                amt = st.number_input("Cantidad de DB COINS a generar:", min_value=1, step=1, value=10)
                if st.button("Generar para usuario seleccionado"):
                    target_ref = db.collection("wallets").document(target)
                    doc_target = target_ref.get()
                    current = 0
                    if doc_target.exists:
                        current = doc_target.to_dict().get("coins", 0)
                    target_ref.set({"coins": current + amt})
                    st.success(f"Generados {amt} DB COINS para {valid_users[target]}.")
    
    # ------------------- Communications -------------------
    elif menu_choice == "Communications":
        st.subheader("📢 Mensajes Importantes")
        mensaje = st.text_area("📝 Escribe un mensaje o anuncio")
        if st.button("📩 Enviar mensaje"):
            db.collection("communications").document().set({
                "usuario": user_code,
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "mensaje": mensaje
            })
            st.success("Mensaje enviado.")
    
    # ------------------- Calendar -------------------
    elif menu_choice == "Calendar":
        st.subheader("📅 Calendario")
        cal_option = st.radio("Selecciona una opción", ["Crear Evento", "Ver Calendario"])
        if cal_option == "Crear Evento":
            st.markdown("### Crear Evento")
            evento = st.text_input("📌 Nombre del evento")
            start_date, end_date = st.date_input("Selecciona el rango de fechas", value=(date.today(), date.today()))
            tipo_evento = st.radio("Tipo de evento", ["Público", "Privado"])
            if st.button("✅ Agendar evento"):
                event_data = {
                    "usuario": user_code,
                    "evento": evento,
                    "fecha": start_date.strftime("%Y-%m-%d"),
                    "fecha_fin": end_date.strftime("%Y-%m-%d"),
                    "publico": True if tipo_evento == "Público" else False
                }
                db.collection("calendar").document().set(event_data)
                st.success("Evento agendado.")
        else:
            st.markdown("### Ver Calendario")
            start_date, end_date = st.date_input("Selecciona el rango de fechas para ver eventos", value=(date.today(), date.today()))
            events = []
            for doc in db.collection("calendar").stream():
                data = doc.to_dict()
                if data.get("fecha"):
                    event_date = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
                    if start_date <= event_date <= end_date:
                        title = data.get("evento", "Evento")
                        if not data.get("publico", False):
                            title += f" (Privado - {data.get('usuario','')})"
                        events.append({
                            "title": title,
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
    
    # ------------------- Roles -------------------
    elif menu_choice == "Roles":
        if user_code == "ALECCION":
            st.subheader("📝 Asignación de Roles Semanal - GL NAMER & LATAM")
            if st.button("Asignar Roles"):
                posibles = [code for code in valid_users if code not in {"ALECCION", "WORLEAD", "LARANDA", "R2RGRAL", "FALEAD", "ICLEAD"}]
                roles_asignados = random.sample(posibles, 3)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1],
                    "Coach": roles_asignados[2]
                }
                st.json(st.session_state["roles"])
        elif user_code == "WORLEAD":
            st.subheader("📝 Asignación de Roles Semanal - WOR SGBS")
            posibles = [code for code in valid_users if code not in {"WORLEAD", "ALECCION", "LARANDA", "R2RGRAL", "FALEAD", "ICLEAD"} and code in group_wor]
            if len(posibles) >= 3:
                roles_asignados = random.sample(posibles, 3)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1],
                    "Coach": roles_asignados[2]
                }
                st.json(st.session_state["roles"])
            else:
                st.error("No hay suficientes usuarios en WOR SGBS para asignar roles.")
        elif user_code == "R2RGRAL":
            st.subheader("📝 Asignación de Roles Semanal - R2R GRAL")
            posibles = [code for code in valid_users if code not in {"R2RGRAL", "ALECCION", "WORLEAD", "LARANDA", "FALEAD", "ICLEAD"} and code in group_r2r_gral]
            if len(posibles) >= 2:
                roles_asignados = random.sample(posibles, 2)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1]
                }
                st.json(st.session_state["roles"])
            else:
                st.error("No hay suficientes usuarios en R2R GRAL para asignar roles.")
        elif user_code == "FALEAD":
            st.subheader("📝 Asignación de Roles Semanal - FA")
            posibles = [code for code in valid_users if code not in {"FALEAD", "ALECCION", "WORLEAD", "LARANDA", "R2RGRAL", "ICLEAD"} and code in group_fa]
            if len(posibles) >= 2:
                roles_asignados = random.sample(posibles, 2)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1]
                }
                st.json(st.session_state["roles"])
            else:
                st.error("No hay suficientes usuarios en FA para asignar roles.")
        elif user_code == "ICLEAD":
            st.subheader("📝 Asignación de Roles Semanal - IC")
            posibles = [code for code in valid_users if code not in {"ICLEAD", "ALECCION", "WORLEAD", "LARANDA", "R2RGRAL", "FALEAD"} and code in group_ic]
            if len(posibles) >= 3:
                roles_asignados = random.sample(posibles, 3)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1],
                    "Coach": roles_asignados[2]
                }
                st.json(st.session_state["roles"])
            else:
                st.error("No hay suficientes usuarios en IC para asignar roles.")
        else:
            st.error("Acceso denegado. Esta opción es exclusiva para los TL.")
    
    # ------------------- Compliance -------------------
    elif menu_choice == "Compliance":
        if user_code in {"ALECCION", "WORLEAD", "R2RGRAL", "FALEAD", "ICLEAD"} or ("roles" in st.session_state and st.session_state["roles"].get("Coach") == user_code):
            st.subheader("📝 Compliance - Feedback")
            feedback_options = [code for code in valid_users if code != user_code]
            target_user = st.selectbox("Dar feedback a:", feedback_options, format_func=lambda x: f"{valid_users.get(x, x)} ({x})")
            feedback = st.text_area("Feedback:")
            if st.button("Enviar Feedback"):
                db.collection("compliance").add({
                    "from": user_code,
                    "to": target_user,
                    "feedback": feedback,
                    "fecha": datetime.now().strftime("%Y-%m-%d")
                })
                st.success("Feedback enviado.")
        else:
            st.error("Acceso denegado. Esta opción es exclusiva para los TL o el Coach.")
    
    # ------------------- Todas las Tareas -------------------
    elif menu_choice == "Todas las Tareas":
        st.subheader("🗂️ Todas las Tareas")
        st.markdown("### Tareas de Top 3")
        tasks_top3 = list(db.collection("top3").stream())
        if tasks_top3:
            for task in tasks_top3:
                task_data = task.to_dict()
                st.markdown(f"**[TOP 3] {task_data.get('descripcion','(Sin descripción)')}**")
                st.write(f"Inicio: {task_data.get('fecha_inicio','')}, Compromiso: {task_data.get('fecha_compromiso','')}, Real: {task_data.get('fecha_real','')}")
                st.markdown(f"**Usuario:** {task_data.get('usuario','')}")
                status = task_data.get('status', '')
                color = {"Pendiente": "red", "En proceso": "orange", "Completado": "green"}.get(status, "black")
                st.markdown(f"**Status:** <span style='color: {color};'>{status}</span>", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No hay tareas de Top 3 registradas.")
        st.markdown("### Tareas de Action Board")
        tasks_actions = list(db.collection("actions").stream())
        if tasks_actions:
            for action in tasks_actions:
                action_data = action.to_dict()
                st.markdown(f"**[Action Board] {action_data.get('accion','(Sin descripción)')}**")
                st.write(f"Inicio: {action_data.get('fecha_inicio','')}, Compromiso: {action_data.get('fecha_compromiso','')}, Real: {action_data.get('fecha_real','')}")
                st.markdown(f"**Usuario:** {action_data.get('usuario','')}")
                status = action_data.get('status', '')
                color = {"Pendiente": "red", "En proceso": "orange", "Completado": "green"}.get(status, "black")
                st.markdown(f"**Status:** <span style='color: {color};'>{status}</span>", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No hay acciones registradas.")
    
    # ------------------- Store DBSCHENKER -------------------
    elif menu_choice == "Store DBSCHENKER":
        st.subheader("🛍️ Store DBSCHENKER")
        st.write("Productos corporativos (prototipo):")
        products = [
            {"name": "Taza DBS", "price": 10, "image": "https://via.placeholder.com/150?text=Taza+DBS"},
            {"name": "Playera DBS", "price": 20, "image": "https://via.placeholder.com/150?text=Playera+DBS"},
            {"name": "Gorra DBS", "price": 15, "image": "https://via.placeholder.com/150?text=Gorra+DBS"}
        ]
        for prod in products:
            st.image(prod["image"], width=150)
            st.markdown(f"**{prod['name']}** - {prod['price']} DB COINS")
            if st.button(f"Comprar {prod['name']}", key=f"buy_{prod['name']}"):
                st.info("Función de compra no implementada.")
            st.markdown("---")
    
    # ------------------- Wallet -------------------
    elif menu_choice == "Wallet":
        st.subheader("💰 Mi Wallet (DB COINS)")
        wallet_ref = db.collection("wallets").document(user_code)
        doc = wallet_ref.get()
        current_coins = 0
        if doc.exists:
            current_coins = doc.to_dict().get("coins", 0)
        st.write(f"**Saldo actual:** {current_coins} DB COINS")
        if user_code == "LARANDA":
            add_coins = st.number_input("Generar DB COINS:", min_value=1, step=1, value=10)
            if st.button("Generar DB COINS"):
                new_balance = current_coins + add_coins
                wallet_ref.set({"coins": new_balance})
                st.success(f"Generados {add_coins} DB COINS. Nuevo saldo: {new_balance}.")
            st.markdown("### Funciones Administrativas")
            admin_key = st.text_input("Clave Admin", type="password")
            if admin_key == "ADMIN123":
                if st.button("Resetear todas las monedas a 0"):
                    for u in valid_users:
                        db.collection("wallets").document(u).set({"coins": 0})
                target = st.selectbox("Generar monedas para el usuario:", list(valid_users.keys()), format_func=lambda x: f"{valid_users[x]} ({x})")
                amt = st.number_input("Cantidad de DB COINS a generar:", min_value=1, step=1, value=10)
                if st.button("Generar para usuario seleccionado"):
                    target_ref = db.collection("wallets").document(target)
                    doc_target = target_ref.get()
                    current = 0
                    if doc_target.exists:
                        current = doc_target.to_dict().get("coins", 0)
                    target_ref.set({"coins": current + amt})
                    st.success(f"Generados {amt} DB COINS para {valid_users[target]}.")
    
    # ------------------- Communications -------------------
    elif menu_choice == "Communications":
        st.subheader("📢 Mensajes Importantes")
        mensaje = st.text_area("📝 Escribe un mensaje o anuncio")
        if st.button("📩 Enviar mensaje"):
            db.collection("communications").document().set({
                "usuario": user_code,
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "mensaje": mensaje
            })
            st.success("Mensaje enviado.")
    
    # ------------------- Calendar -------------------
    elif menu_choice == "Calendar":
        st.subheader("📅 Calendario")
        cal_option = st.radio("Selecciona una opción", ["Crear Evento", "Ver Calendario"])
        if cal_option == "Crear Evento":
            st.markdown("### Crear Evento")
            evento = st.text_input("📌 Nombre del evento")
            start_date, end_date = st.date_input("Selecciona el rango de fechas", value=(date.today(), date.today()))
            tipo_evento = st.radio("Tipo de evento", ["Público", "Privado"])
            if st.button("✅ Agendar evento"):
                event_data = {
                    "usuario": user_code,
                    "evento": evento,
                    "fecha": start_date.strftime("%Y-%m-%d"),
                    "fecha_fin": end_date.strftime("%Y-%m-%d"),
                    "publico": True if tipo_evento == "Público" else False
                }
                db.collection("calendar").document().set(event_data)
                st.success("Evento agendado.")
        else:
            st.markdown("### Ver Calendario")
            start_date, end_date = st.date_input("Selecciona el rango de fechas para ver eventos", value=(date.today(), date.today()))
            events = []
            for doc in db.collection("calendar").stream():
                data = doc.to_dict()
                if data.get("fecha"):
                    event_date = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
                    if start_date <= event_date <= end_date:
                        title = data.get("evento", "Evento")
                        if not data.get("publico", False):
                            title += f" (Privado - {data.get('usuario','')})"
                        events.append({
                            "title": title,
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
    
    # ------------------- Roles -------------------
    elif menu_choice == "Roles":
        if user_code == "ALECCION":
            st.subheader("📝 Asignación de Roles Semanal - GL NAMER & LATAM")
            if st.button("Asignar Roles"):
                posibles = [code for code in valid_users if code not in {"ALECCION", "WORLEAD", "LARANDA", "R2RGRAL", "FALEAD", "ICLEAD"}]
                roles_asignados = random.sample(posibles, 3)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1],
                    "Coach": roles_asignados[2]
                }
                st.json(st.session_state["roles"])
        elif user_code == "WORLEAD":
            st.subheader("📝 Asignación de Roles Semanal - WOR SGBS")
            posibles = [code for code in valid_users if code not in {"WORLEAD", "ALECCION", "LARANDA", "R2RGRAL", "FALEAD", "ICLEAD"} and code in group_wor]
            if len(posibles) >= 3:
                roles_asignados = random.sample(posibles, 3)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1],
                    "Coach": roles_asignados[2]
                }
                st.json(st.session_state["roles"])
            else:
                st.error("No hay suficientes usuarios en WOR SGBS para asignar roles.")
        elif user_code == "R2RGRAL":
            st.subheader("📝 Asignación de Roles Semanal - R2R GRAL")
            posibles = [code for code in valid_users if code not in {"R2RGRAL", "ALECCION", "WORLEAD", "LARANDA", "FALEAD", "ICLEAD"} and code in group_r2r_gral]
            if len(posibles) >= 2:
                roles_asignados = random.sample(posibles, 2)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1]
                }
                st.json(st.session_state["roles"])
            else:
                st.error("No hay suficientes usuarios en R2R GRAL para asignar roles.")
        elif user_code == "FALEAD":
            st.subheader("📝 Asignación de Roles Semanal - FA")
            posibles = [code for code in valid_users if code not in {"FALEAD", "ALECCION", "WORLEAD", "LARANDA", "R2RGRAL", "ICLEAD"} and code in group_fa]
            if len(posibles) >= 2:
                roles_asignados = random.sample(posibles, 2)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1]
                }
                st.json(st.session_state["roles"])
            else:
                st.error("No hay suficientes usuarios en FA para asignar roles.")
        elif user_code == "ICLEAD":
            st.subheader("📝 Asignación de Roles Semanal - IC")
            posibles = [code for code in valid_users if code not in {"ICLEAD", "ALECCION", "WORLEAD", "LARANDA", "R2RGRAL", "FALEAD"} and code in group_ic]
            if len(posibles) >= 3:
                roles_asignados = random.sample(posibles, 3)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1],
                    "Coach": roles_asignados[2]
                }
                st.json(st.session_state["roles"])
            else:
                st.error("No hay suficientes usuarios en IC para asignar roles.")
        else:
            st.error("Acceso denegado. Esta opción es exclusiva para los TL.")
    
    # ------------------- Compliance -------------------
    elif menu_choice == "Compliance":
        if user_code in {"ALECCION", "WORLEAD", "R2RGRAL", "FALEAD", "ICLEAD"} or ("roles" in st.session_state and st.session_state["roles"].get("Coach") == user_code):
            st.subheader("📝 Compliance - Feedback")
            feedback_options = [code for code in valid_users if code != user_code]
            target_user = st.selectbox("Dar feedback a:", feedback_options, format_func=lambda x: f"{valid_users.get(x, x)} ({x})")
            feedback = st.text_area("Feedback:")
            if st.button("Enviar Feedback"):
                db.collection("compliance").add({
                    "from": user_code,
                    "to": target_user,
                    "feedback": feedback,
                    "fecha": datetime.now().strftime("%Y-%m-%d")
                })
                st.success("Feedback enviado.")
        else:
            st.error("Acceso denegado. Esta opción es exclusiva para los TL o el Coach.")
    
    # ------------------- Todas las Tareas -------------------
    elif menu_choice == "Todas las Tareas":
        st.subheader("🗂️ Todas las Tareas")
        st.markdown("### Tareas de Top 3")
        tasks_top3 = list(db.collection("top3").stream())
        if tasks_top3:
            for task in tasks_top3:
                task_data = task.to_dict()
                st.markdown(f"**[TOP 3] {task_data.get('descripcion','(Sin descripción)')}**")
                st.write(f"Inicio: {task_data.get('fecha_inicio','')}, Compromiso: {task_data.get('fecha_compromiso','')}, Real: {task_data.get('fecha_real','')}")
                st.markdown(f"**Usuario:** {task_data.get('usuario','')}")
                status = task_data.get('status', '')
                color = {"Pendiente": "red", "En proceso": "orange", "Completado": "green"}.get(status, "black")
                st.markdown(f"**Status:** <span style='color: {color};'>{status}</span>", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No hay tareas de Top 3 registradas.")
        st.markdown("### Tareas de Action Board")
        tasks_actions = list(db.collection("actions").stream())
        if tasks_actions:
            for action in tasks_actions:
                action_data = action.to_dict()
                st.markdown(f"**[Action Board] {action_data.get('accion','(Sin descripción)')}**")
                st.write(f"Inicio: {action_data.get('fecha_inicio','')}, Compromiso: {action_data.get('fecha_compromiso','')}, Real: {action_data.get('fecha_real','')}")
                st.markdown(f"**Usuario:** {action_data.get('usuario','')}")
                status = action_data.get('status', '')
                color = {"Pendiente": "red", "En proceso": "orange", "Completado": "green"}.get(status, "black")
                st.markdown(f"**Status:** <span style='color: {color};'>{status}</span>", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No hay acciones registradas.")
    
    # ------------------- Store DBSCHENKER -------------------
    elif menu_choice == "Store DBSCHENKER":
        st.subheader("🛍️ Store DBSCHENKER")
        st.write("Productos corporativos (prototipo):")
        products = [
            {"name": "Taza DBS", "price": 10, "image": "https://via.placeholder.com/150?text=Taza+DBS"},
            {"name": "Playera DBS", "price": 20, "image": "https://via.placeholder.com/150?text=Playera+DBS"},
            {"name": "Gorra DBS", "price": 15, "image": "https://via.placeholder.com/150?text=Gorra+DBS"}
        ]
        for prod in products:
            st.image(prod["image"], width=150)
            st.markdown(f"**{prod['name']}** - {prod['price']} DB COINS")
            if st.button(f"Comprar {prod['name']}", key=f"buy_{prod['name']}"):
                st.info("Función de compra no implementada.")
            st.markdown("---")
    
    # ------------------- Wallet -------------------
    elif menu_choice == "Wallet":
        st.subheader("💰 Mi Wallet (DB COINS)")
        wallet_ref = db.collection("wallets").document(user_code)
        doc = wallet_ref.get()
        current_coins = 0
        if doc.exists:
            current_coins = doc.to_dict().get("coins", 0)
        st.write(f"**Saldo actual:** {current_coins} DB COINS")
        if user_code == "LARANDA":
            add_coins = st.number_input("Generar DB COINS:", min_value=1, step=1, value=10)
            if st.button("Generar DB COINS"):
                new_balance = current_coins + add_coins
                wallet_ref.set({"coins": new_balance})
                st.success(f"Generados {add_coins} DB COINS. Nuevo saldo: {new_balance}.")
            st.markdown("### Funciones Administrativas")
            admin_key = st.text_input("Clave Admin", type="password")
            if admin_key == "ADMIN123":
                if st.button("Resetear todas las monedas a 0"):
                    for u in valid_users:
                        db.collection("wallets").document(u).set({"coins": 0})
                target = st.selectbox("Generar monedas para el usuario:", list(valid_users.keys()), format_func=lambda x: f"{valid_users[x]} ({x})")
                amt = st.number_input("Cantidad de DB COINS a generar:", min_value=1, step=1, value=10)
                if st.button("Generar para usuario seleccionado"):
                    target_ref = db.collection("wallets").document(target)
                    doc_target = target_ref.get()
                    current = 0
                    if doc_target.exists:
                        current = doc_target.to_dict().get("coins", 0)
                    target_ref.set({"coins": current + amt})
                    st.success(f"Generados {amt} DB COINS para {valid_users[target]}.")
    
    # ------------------- Communications -------------------
    elif menu_choice == "Communications":
        st.subheader("📢 Mensajes Importantes")
        mensaje = st.text_area("📝 Escribe un mensaje o anuncio")
        if st.button("📩 Enviar mensaje"):
            db.collection("communications").document().set({
                "usuario": user_code,
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "mensaje": mensaje
            })
            st.success("Mensaje enviado.")
    
    # ------------------- Calendar -------------------
    elif menu_choice == "Calendar":
        st.subheader("📅 Calendario")
        cal_option = st.radio("Selecciona una opción", ["Crear Evento", "Ver Calendario"])
        if cal_option == "Crear Evento":
            st.markdown("### Crear Evento")
            evento = st.text_input("📌 Nombre del evento")
            start_date, end_date = st.date_input("Selecciona el rango de fechas", value=(date.today(), date.today()))
            tipo_evento = st.radio("Tipo de evento", ["Público", "Privado"])
            if st.button("✅ Agendar evento"):
                event_data = {
                    "usuario": user_code,
                    "evento": evento,
                    "fecha": start_date.strftime("%Y-%m-%d"),
                    "fecha_fin": end_date.strftime("%Y-%m-%d"),
                    "publico": True if tipo_evento == "Público" else False
                }
                db.collection("calendar").document().set(event_data)
                st.success("Evento agendado.")
        else:
            st.markdown("### Ver Calendario")
            start_date, end_date = st.date_input("Selecciona el rango de fechas para ver eventos", value=(date.today(), date.today()))
            events = []
            for doc in db.collection("calendar").stream():
                data = doc.to_dict()
                if data.get("fecha"):
                    event_date = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
                    if start_date <= event_date <= end_date:
                        title = data.get("evento", "Evento")
                        if not data.get("publico", False):
                            title += f" (Privado - {data.get('usuario','')})"
                        events.append({
                            "title": title,
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
    
    # ------------------- Roles -------------------
    elif menu_choice == "Roles":
        if user_code == "ALECCION":
            st.subheader("📝 Asignación de Roles Semanal - GL NAMER & LATAM")
            if st.button("Asignar Roles"):
                posibles = [code for code in valid_users if code not in {"ALECCION", "WORLEAD", "LARANDA", "R2RGRAL", "FALEAD", "ICLEAD"}]
                roles_asignados = random.sample(posibles, 3)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1],
                    "Coach": roles_asignados[2]
                }
                st.json(st.session_state["roles"])
        elif user_code == "WORLEAD":
            st.subheader("📝 Asignación de Roles Semanal - WOR SGBS")
            posibles = [code for code in valid_users if code not in {"WORLEAD", "ALECCION", "LARANDA", "R2RGRAL", "FALEAD", "ICLEAD"} and code in group_wor]
            if len(posibles) >= 3:
                roles_asignados = random.sample(posibles, 3)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1],
                    "Coach": roles_asignados[2]
                }
                st.json(st.session_state["roles"])
            else:
                st.error("No hay suficientes usuarios en WOR SGBS para asignar roles.")
        elif user_code == "R2RGRAL":
            st.subheader("📝 Asignación de Roles Semanal - R2R GRAL")
            posibles = [code for code in valid_users if code not in {"R2RGRAL", "ALECCION", "WORLEAD", "LARANDA", "FALEAD", "ICLEAD"} and code in group_r2r_gral]
            if len(posibles) >= 2:
                roles_asignados = random.sample(posibles, 2)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1]
                }
                st.json(st.session_state["roles"])
            else:
                st.error("No hay suficientes usuarios en R2R GRAL para asignar roles.")
        elif user_code == "FALEAD":
            st.subheader("📝 Asignación de Roles Semanal - FA")
            posibles = [code for code in valid_users if code not in {"FALEAD", "ALECCION", "WORLEAD", "LARANDA", "R2RGRAL", "ICLEAD"} and code in group_fa]
            if len(posibles) >= 2:
                roles_asignados = random.sample(posibles, 2)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1]
                }
                st.json(st.session_state["roles"])
            else:
                st.error("No hay suficientes usuarios en FA para asignar roles.")
        elif user_code == "ICLEAD":
            st.subheader("📝 Asignación de Roles Semanal - IC")
            posibles = [code for code in valid_users if code not in {"ICLEAD", "ALECCION", "WORLEAD", "LARANDA", "R2RGRAL", "FALEAD"} and code in group_ic]
            if len(posibles) >= 3:
                roles_asignados = random.sample(posibles, 3)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1],
                    "Coach": roles_asignados[2]
                }
                st.json(st.session_state["roles"])
            else:
                st.error("No hay suficientes usuarios en IC para asignar roles.")
        else:
            st.error("Acceso denegado. Esta opción es exclusiva para los TL.")
    
    # ------------------- Compliance -------------------
    elif menu_choice == "Compliance":
        if user_code in {"ALECCION", "WORLEAD", "R2RGRAL", "FALEAD", "ICLEAD"} or ("roles" in st.session_state and st.session_state["roles"].get("Coach") == user_code):
            st.subheader("📝 Compliance - Feedback")
            feedback_options = [code for code in valid_users if code != user_code]
            target_user = st.selectbox("Dar feedback a:", feedback_options, format_func=lambda x: f"{valid_users.get(x, x)} ({x})")
            feedback = st.text_area("Feedback:")
            if st.button("Enviar Feedback"):
                db.collection("compliance").add({
                    "from": user_code,
                    "to": target_user,
                    "feedback": feedback,
                    "fecha": datetime.now().strftime("%Y-%m-%d")
                })
                st.success("Feedback enviado.")
        else:
            st.error("Acceso denegado. Esta opción es exclusiva para los TL o el Coach.")
    
    # ------------------- Todas las Tareas -------------------
    elif menu_choice == "Todas las Tareas":
        st.subheader("🗂️ Todas las Tareas")
        st.markdown("### Tareas de Top 3")
        tasks_top3 = list(db.collection("top3").stream())
        if tasks_top3:
            for task in tasks_top3:
                task_data = task.to_dict()
                st.markdown(f"**[TOP 3] {task_data.get('descripcion','(Sin descripción)')}**")
                st.write(f"Inicio: {task_data.get('fecha_inicio','')}, Compromiso: {task_data.get('fecha_compromiso','')}, Real: {task_data.get('fecha_real','')}")
                st.markdown(f"**Usuario:** {task_data.get('usuario','')}")
                status = task_data.get('status', '')
                color = {"Pendiente": "red", "En proceso": "orange", "Completado": "green"}.get(status, "black")
                st.markdown(f"**Status:** <span style='color: {color};'>{status}</span>", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No hay tareas de Top 3 registradas.")
        st.markdown("### Tareas de Action Board")
        tasks_actions = list(db.collection("actions").stream())
        if tasks_actions:
            for action in tasks_actions:
                action_data = action.to_dict()
                st.markdown(f"**[Action Board] {action_data.get('accion','(Sin descripción)')}**")
                st.write(f"Inicio: {action_data.get('fecha_inicio','')}, Compromiso: {action_data.get('fecha_compromiso','')}, Real: {action_data.get('fecha_real','')}")
                st.markdown(f"**Usuario:** {action_data.get('usuario','')}")
                status = action_data.get('status', '')
                color = {"Pendiente": "red", "En proceso": "orange", "Completado": "green"}.get(status, "black")
                st.markdown(f"**Status:** <span style='color: {color};'>{status}</span>", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No hay acciones registradas.")
    
    # ------------------- Store DBSCHENKER -------------------
    elif menu_choice == "Store DBSCHENKER":
        st.subheader("🛍️ Store DBSCHENKER")
        st.write("Productos corporativos (prototipo):")
        products = [
            {"name": "Taza DBS", "price": 10, "image": "https://via.placeholder.com/150?text=Taza+DBS"},
            {"name": "Playera DBS", "price": 20, "image": "https://via.placeholder.com/150?text=Playera+DBS"},
            {"name": "Gorra DBS", "price": 15, "image": "https://via.placeholder.com/150?text=Gorra+DBS"}
        ]
        for prod in products:
            st.image(prod["image"], width=150)
            st.markdown(f"**{prod['name']}** - {prod['price']} DB COINS")
            if st.button(f"Comprar {prod['name']}", key=f"buy_{prod['name']}"):
                st.info("Función de compra no implementada.")
            st.markdown("---")
    
    # ------------------- Wallet -------------------
    elif menu_choice == "Wallet":
        st.subheader("💰 Mi Wallet (DB COINS)")
        wallet_ref = db.collection("wallets").document(user_code)
        doc = wallet_ref.get()
        current_coins = 0
        if doc.exists:
            current_coins = doc.to_dict().get("coins", 0)
        st.write(f"**Saldo actual:** {current_coins} DB COINS")
        if user_code == "LARANDA":
            add_coins = st.number_input("Generar DB COINS:", min_value=1, step=1, value=10)
            if st.button("Generar DB COINS"):
                new_balance = current_coins + add_coins
                wallet_ref.set({"coins": new_balance})
                st.success(f"Generados {add_coins} DB COINS. Nuevo saldo: {new_balance}.")
            st.markdown("### Funciones Administrativas")
            admin_key = st.text_input("Clave Admin", type="password")
            if admin_key == "ADMIN123":
                if st.button("Resetear todas las monedas a 0"):
                    for u in valid_users:
                        db.collection("wallets").document(u).set({"coins": 0})
                target = st.selectbox("Generar monedas para el usuario:", list(valid_users.keys()), format_func=lambda x: f"{valid_users[x]} ({x})")
                amt = st.number_input("Cantidad de DB COINS a generar:", min_value=1, step=1, value=10)
                if st.button("Generar para usuario seleccionado"):
                    target_ref = db.collection("wallets").document(target)
                    doc_target = target_ref.get()
                    current = 0
                    if doc_target.exists:
                        current = doc_target.to_dict().get("coins", 0)
                    target_ref.set({"coins": current + amt})
                    st.success(f"Generados {amt} DB COINS para {valid_users[target]}.")
    
    # ------------------- Communications -------------------
    elif menu_choice == "Communications":
        st.subheader("📢 Mensajes Importantes")
        mensaje = st.text_area("📝 Escribe un mensaje o anuncio")
        if st.button("📩 Enviar mensaje"):
            db.collection("communications").document().set({
                "usuario": user_code,
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "mensaje": mensaje
            })
            st.success("Mensaje enviado.")
    
    # ------------------- Calendar -------------------
    elif menu_choice == "Calendar":
        st.subheader("📅 Calendario")
        cal_option = st.radio("Selecciona una opción", ["Crear Evento", "Ver Calendario"])
        if cal_option == "Crear Evento":
            st.markdown("### Crear Evento")
            evento = st.text_input("📌 Nombre del evento")
            start_date, end_date = st.date_input("Selecciona el rango de fechas", value=(date.today(), date.today()))
            tipo_evento = st.radio("Tipo de evento", ["Público", "Privado"])
            if st.button("✅ Agendar evento"):
                event_data = {
                    "usuario": user_code,
                    "evento": evento,
                    "fecha": start_date.strftime("%Y-%m-%d"),
                    "fecha_fin": end_date.strftime("%Y-%m-%d"),
                    "publico": True if tipo_evento == "Público" else False
                }
                db.collection("calendar").document().set(event_data)
                st.success("Evento agendado.")
        else:
            st.markdown("### Ver Calendario")
            start_date, end_date = st.date_input("Selecciona el rango de fechas para ver eventos", value=(date.today(), date.today()))
            events = []
            for doc in db.collection("calendar").stream():
                data = doc.to_dict()
                if data.get("fecha"):
                    event_date = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
                    if start_date <= event_date <= end_date:
                        title = data.get("evento", "Evento")
                        if not data.get("publico", False):
                            title += f" (Privado - {data.get('usuario','')})"
                        events.append({
                            "title": title,
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
    
    # ------------------- Roles -------------------
    elif menu_choice == "Roles":
        if user_code == "ALECCION":
            st.subheader("📝 Asignación de Roles Semanal - GL NAMER & LATAM")
            if st.button("Asignar Roles"):
                posibles = [code for code in valid_users if code not in {"ALECCION", "WORLEAD", "LARANDA", "R2RGRAL", "FALEAD", "ICLEAD"}]
                roles_asignados = random.sample(posibles, 3)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1],
                    "Coach": roles_asignados[2]
                }
                st.json(st.session_state["roles"])
        elif user_code == "WORLEAD":
            st.subheader("📝 Asignación de Roles Semanal - WOR SGBS")
            posibles = [code for code in valid_users if code not in {"WORLEAD", "ALECCION", "LARANDA", "R2RGRAL", "FALEAD", "ICLEAD"} and code in group_wor]
            if len(posibles) >= 3:
                roles_asignados = random.sample(posibles, 3)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1],
                    "Coach": roles_asignados[2]
                }
                st.json(st.session_state["roles"])
            else:
                st.error("No hay suficientes usuarios en WOR SGBS para asignar roles.")
        elif user_code == "R2RGRAL":
            st.subheader("📝 Asignación de Roles Semanal - R2R GRAL")
            posibles = [code for code in valid_users if code not in {"R2RGRAL", "ALECCION", "WORLEAD", "LARANDA", "FALEAD", "ICLEAD"} and code in group_r2r_gral]
            if len(posibles) >= 2:
                roles_asignados = random.sample(posibles, 2)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1]
                }
                st.json(st.session_state["roles"])
            else:
                st.error("No hay suficientes usuarios en R2R GRAL para asignar roles.")
        elif user_code == "FALEAD":
            st.subheader("📝 Asignación de Roles Semanal - FA")
            posibles = [code for code in valid_users if code not in {"FALEAD", "ALECCION", "WORLEAD", "LARANDA", "R2RGRAL", "ICLEAD"} and code in group_fa]
            if len(posibles) >= 2:
                roles_asignados = random.sample(posibles, 2)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1]
                }
                st.json(st.session_state["roles"])
            else:
                st.error("No hay suficientes usuarios en FA para asignar roles.")
        elif user_code == "ICLEAD":
            st.subheader("📝 Asignación de Roles Semanal - IC")
            posibles = [code for code in valid_users if code not in {"ICLEAD", "ALECCION", "WORLEAD", "LARANDA", "R2RGRAL", "FALEAD"} and code in group_ic]
            if len(posibles) >= 3:
                roles_asignados = random.sample(posibles, 3)
                st.session_state["roles"] = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1],
                    "Coach": roles_asignados[2]
                }
                st.json(st.session_state["roles"])
            else:
                st.error("No hay suficientes usuarios en IC para asignar roles.")
        else:
            st.error("Acceso denegado. Esta opción es exclusiva para los TL.")
    
    # ------------------- Compliance -------------------
    elif menu_choice == "Compliance":
        if user_code in {"ALECCION", "WORLEAD", "R2RGRAL", "FALEAD", "ICLEAD"} or ("roles" in st.session_state and st.session_state["roles"].get("Coach") == user_code):
            st.subheader("📝 Compliance - Feedback")
            feedback_options = [code for code in valid_users if code != user_code]
            target_user = st.selectbox("Dar feedback a:", feedback_options, format_func=lambda x: f"{valid_users.get(x, x)} ({x})")
            feedback = st.text_area("Feedback:")
            if st.button("Enviar Feedback"):
                db.collection("compliance").add({
                    "from": user_code,
                    "to": target_user,
                    "feedback": feedback,
                    "fecha": datetime.now().strftime("%Y-%m-%d")
                })
                st.success("Feedback enviado.")
        else:
            st.error("Acceso denegado. Esta opción es exclusiva para los TL o el Coach.")
    
    # ------------------- Todas las Tareas -------------------
    elif menu_choice == "Todas las Tareas":
        st.subheader("🗂️ Todas las Tareas")
        st.markdown("### Tareas de Top 3")
        tasks_top3 = list(db.collection("top3").stream())
        if tasks_top3:
            for task in tasks_top3:
                task_data = task.to_dict()
                st.markdown(f"**[TOP 3] {task_data.get('descripcion','(Sin descripción)')}**")
                st.write(f"Inicio: {task_data.get('fecha_inicio','')}, Compromiso: {task_data.get('fecha_compromiso','')}, Real: {task_data.get('fecha_real','')}")
                st.markdown(f"**Usuario:** {task_data.get('usuario','')}")
                status = task_data.get('status', '')
                color = {"Pendiente": "red", "En proceso": "orange", "Completado": "green"}.get(status, "black")
                st.markdown(f"**Status:** <span style='color: {color};'>{status}</span>", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No hay tareas de Top 3 registradas.")
        st.markdown("### Tareas de Action Board")
        tasks_actions = list(db.collection("actions").stream())
        if tasks_actions:
            for action in tasks_actions:
                action_data = action.to_dict()
                st.markdown(f"**[Action Board] {action_data.get('accion','(Sin descripción)')}**")
                st.write(f"Inicio: {action_data.get('fecha_inicio','')}, Compromiso: {action_data.get('fecha_compromiso','')}, Real: {action_data.get('fecha_real','')}")
                st.markdown(f"**Usuario:** {action_data.get('usuario','')}")
                status = action_data.get('status', '')
                color = {"Pendiente": "red", "En proceso": "orange", "Completado": "green"}.get(status, "black")
                st.markdown(f"**Status:** <span style='color: {color};'>{status}</span>", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No hay acciones registradas.")
    
    # ------------------- Store DBSCHENKER -------------------
    elif menu_choice == "Store DBSCHENKER":
        st.subheader("🛍️ Store DBSCHENKER")
        st.write("Productos corporativos (prototipo):")
        products = [
            {"name": "Taza DBS", "price": 10, "image": "https://via.placeholder.com/150?text=Taza+DBS"},
            {"name": "Playera DBS", "price": 20, "image": "https://via.placeholder.com/150?text=Playera+DBS"},
            {"name": "Gorra DBS", "price": 15, "image": "https://via.placeholder.com/150?text=Gorra+DBS"}
        ]
        for prod in products:
            st.image(prod["image"], width=150)
            st.markdown(f"**{prod['name']}** - {prod['price']} DB COINS")
            if st.button(f"Comprar {prod['name']}", key=f"buy_{prod['name']}"):
                st.info("Función de compra no implementada.")
            st.markdown("---")
    
    # ------------------- Wallet -------------------
    elif menu_choice == "Wallet":
        st.subheader("💰 Mi Wallet (DB COINS)")
        wallet_ref = db.collection("wallets").document(user_code)
        doc = wallet_ref.get()
        current_coins = 0
        if doc.exists:
            current_coins = doc.to_dict().get("coins", 0)
        st.write(f"**Saldo actual:** {current_coins} DB COINS")
        if user_code == "LARANDA":
            add_coins = st.number_input("Generar DB COINS:", min_value=1, step=1, value=10)
            if st.button("Generar DB COINS"):
                new_balance = current_coins + add_coins
                wallet_ref.set({"coins": new_balance})
                st.success(f"Generados {add_coins} DB COINS. Nuevo saldo: {new_balance}.")
            st.markdown("### Funciones Administrativas")
            admin_key = st.text_input("Clave Admin", type="password")
            if admin_key == "ADMIN123":
                if st.button("Resetear todas las monedas a 0"):
                    for u in valid_users:
                        db.collection("wallets").document(u).set({"coins": 0})
                target = st.selectbox("Generar monedas para el usuario:", list(valid_users.keys()), format_func=lambda x: f"{valid_users[x]} ({x})")
                amt = st.number_input("Cantidad de DB COINS a generar:", min_value=1, step=1, value=10)
                if st.button("Generar para usuario seleccionado"):
                    target_ref = db.collection("wallets").document(target)
                    doc_target = target_ref.get()
                    current = 0
                    if doc_target.exists:
                        current = doc_target.to_dict().get("coins", 0)
                    target_ref.set({"coins": current + amt})
                    st.success(f"Generados {amt} DB COINS para {valid_users[target]}.")
    
    # ------------------- Communications -------------------
    elif menu_choice == "Communications":
        st.subheader("📢 Mensajes Importantes")
        mensaje = st.text_area("📝 Escribe un mensaje o anuncio")
        if st.button("📩 Enviar mensaje"):
            db.collection("communications").document().set({
                "usuario": user_code,
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "mensaje": mensaje
            })
            st.success("Mensaje enviado.")
    
    # ------------------- Calendar -------------------
    elif menu_choice == "Calendar":
        st.subheader("📅 Calendario")
        cal_option = st.radio("Selecciona una opción", ["Crear Evento", "Ver Calendario"])
        if cal_option == "Crear Evento":
            st.markdown("### Crear Evento")
            evento = st.text_input("📌 Nombre del evento")
            start_date, end_date = st.date_input("Selecciona el rango de fechas", value=(date.today(), date.today()))
            tipo_evento = st.radio("Tipo de evento", ["Público", "Privado"])
            if st.button("✅ Agendar evento"):
                event_data = {
                    "usuario": user_code,
                    "evento": evento,
                    "fecha": start_date.strftime("%Y-%m-%d"),
                    "fecha_fin": end_date.strftime("%Y-%m-%d"),
                    "publico": True if tipo_evento == "Público" else False
                }
                db.collection("calendar").document().set(event_data)
                st.success("Evento agendado.")
        else:
            st.markdown("### Ver Calendario")
            start_date, end_date = st.date_input("Selecciona el rango de fechas para ver eventos", value=(date.today(), date.today()))
            events = []
            for doc in db.collection("calendar").stream():
                data = doc.to_dict()
                if data.get("fecha"):
                    event_date = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
                    if start_date <= event_date <= end_date:
                        title = data.get("evento", "Evento")
                        if not data.get("publico", False):
                            title += f" (Privado - {data.get('usuario','')})"
                        events.append({
                            "title": title,
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
    
show_main_app()
