import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import streamlit.components.v1 as components
import json, random

# ================================
# Lista de usuarios válidos (Código -> Nombre completo)
# ================================
valid_users = {
    "VREYES": "Reyes Escorsia Victor Manuel",
    "RCRUZ": "Cruz Madariaga Rodrigo",
    "AZENTENO": "Zenteno Perez Alejandro",
    "XGUTIERREZ": "Gutierrez Hernandez Ximena",
    "CNAPOLES": "Napoles Escalante Christopher Enrique",
    "MSANCHEZ": "Sanchez Cruz Miriam Viviana",
    "MHERNANDEZ": "Hernandez Ponce Maria Guadalupe",
    "MGARCIA": "Garcia Vazquez Mariana Aketzalli",
    "ALECCION": "Aleccion (TeamLead)"
}

# ================================
# Pantalla de Login
# ================================
if "user_code" not in st.session_state:
    st.session_state["user_code"] = None

def show_login():
    st.title("🔥 Daily Huddle - Login")
    st.write("Ingresa tu código de usuario (Ejemplo: CNAPOLES para Christopher Napoles)")
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
# App Principal
# ================================
def show_main_app():
    user_code = st.session_state["user_code"]

    # --- Imagen corporativa de portada ---
    # Se reemplaza use_column_width -> use_container_width
    st.image(
        "http://bulk-distributor.com/wp-content/uploads/2016/01/DB-Schenker-Hub-Salzburg.jpg",
        caption="DB Schenker",
        use_container_width=True
    )
    
    st.title("🔥 Daily Huddle")
    st.markdown(f"**Usuario:** {valid_users[user_code]}  ({user_code})")
    
    # ================================
    # Inicialización de Firebase
    # ================================
    try:
        firebase_config = st.secrets["firebase"]
        if not isinstance(firebase_config, dict):
            firebase_config = firebase_config.to_dict()
        
        cred = credentials.Certificate(firebase_config)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
    except Exception as e:
        st.error(f"Error al inicializar Firebase: {str(e)}")
        st.stop()

    # =========== Roles en session_state (si TL no los asignó antes) ===========
    if user_code == "ALECCION" and "roles" not in st.session_state:
        # Asignar roles de forma aleatoria y única (Timekeeper, ActionTaker, Coach)
        posibles = [code for code in valid_users if code != "ALECCION"]
        roles_asignados = random.sample(posibles, 3)
        st.session_state["roles"] = {
            "Timekeeper": roles_asignados[0],
            "ActionTaker": roles_asignados[1],
            "Coach": roles_asignados[2]
        }

    # =========== Lógica para habilitar Start Timer ===========
    can_start_timer = False
    # Es TeamLead o Timekeeper
    if user_code == "ALECCION":
        can_start_timer = True
    elif "roles" in st.session_state and st.session_state["roles"].get("Timekeeper") == user_code:
        can_start_timer = True

    if can_start_timer:
        if "timer_started" not in st.session_state:
            st.session_state.timer_started = False
        if not st.session_state.timer_started:
            if st.button("Start Timer"):
                st.session_state.timer_started = True
        if st.session_state.timer_started:
            countdown_html = """
            <div id="countdown" style="position: fixed; top: 10px; right: 10px; background-color: #f0f0f0; 
                 padding: 10px; border-radius: 5px; font-size: 18px; z-index:1000;">
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

    # =========== Diccionario de colores para status ===========
    status_colors = {
        "Pendiente": "red",
        "En proceso": "orange",
        "Completado": "green"
    }

    def get_status(selected, custom):
        return custom.strip() if custom and custom.strip() != "" else selected

    # =========== Construcción del Menú ===========
    main_menu = [
        "Asistencia",
        "Top 3",
        "Action Board",
        "Escalation",
        "Recognition",
        "Store DBSCHENKER",
        "Wallet"
    ]
    extra_menu = ["Communications", "Calendar"]

    # El TeamLead ve roles, compliance y "todas las tareas"
    # El ActionTaker también ve "todas las tareas"
    # El Coach ve "compliance"
    if user_code == "ALECCION":
        extra_menu.extend(["Todas las Tareas", "Roles", "Compliance"])
    elif "roles" in st.session_state:
        if st.session_state["roles"].get("ActionTaker") == user_code:
            extra_menu.append("Todas las Tareas")
        if st.session_state["roles"].get("Coach") == user_code:
            extra_menu.append("Compliance")

    menu_options = main_menu + extra_menu
    choice = st.sidebar.selectbox("📌 Selecciona una pestaña:", menu_options)

    # =========== 1) Asistencia ===========
    if choice == "Asistencia":
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
        
        st.write("Nivel de energía:")
        energy_options = ["Nivel 1", "Nivel 2", "Nivel 3", "Nivel 4", "Nivel 5"]
        energy_level = st.radio("Selecciona tu nivel de energía:", options=energy_options, horizontal=True)
        level_mapping = {"Nivel 1": 20, "Nivel 2": 40, "Nivel 3": 60, "Nivel 4": 80, "Nivel 5": 100}
        fill_percent = level_mapping[energy_level]
        battery_html = f"""
        <div style="display: inline-block; border: 2px solid #000; width: 40px; height: 100px; position: relative;">
          <div style="position: absolute; bottom: 0; width: 100%; height: {fill_percent}%; background-color: #00ff00;"></div>
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

    # =========== 2) Top 3 ===========
    elif choice == "Top 3":
        st.subheader("📌 Top 3 Prioridades - Resumen")
        # El ActionTaker o TeamLead ve todo, de lo contrario, solo las propias
        is_actiontaker = ("roles" in st.session_state and st.session_state["roles"].get("ActionTaker") == user_code)
        if user_code == "ALECCION" or is_actiontaker:
            tasks = list(db.collection("top3").stream())
        else:
            tasks = list(db.collection("top3").where("usuario", "==", user_code).stream())
        
        top3_container = st.empty()
        def load_top3():
            if user_code == "ALECCION" or is_actiontaker:
                _tasks = list(db.collection("top3").stream())
            else:
                _tasks = list(db.collection("top3").where("usuario","==",user_code).stream())
            top3_container.empty()
            with top3_container.container():
                st.markdown("---")
                if _tasks:
                    for task in _tasks:
                        task_id = task.id
                        task_data = task.to_dict()
                        st.markdown(f"**[TOP 3] {task_data.get('descripcion','(Sin descripción)')}**")
                        st.write(f"Inicio: {task_data.get('fecha_inicio','')} | Compromiso: {task_data.get('fecha_compromiso','')} | Real: {task_data.get('fecha_real','')}")
                        if user_code == "ALECCION" or is_actiontaker:
                            st.write(f"**Usuario:** {task_data.get('usuario','')}")
                        status_val = task_data.get('status','')
                        color = status_colors.get(status_val,"black")
                        st.markdown(f"**Status:** <span style='color:{color};'>{status_val}</span>", unsafe_allow_html=True)
                        
                        new_status = st.selectbox(
                            "Editar status",
                            ["Pendiente","En proceso","Completado"],
                            index=(["Pendiente","En proceso","Completado"].index(status_val)
                                   if status_val in ["Pendiente","En proceso","Completado"] else 0),
                            key=f"top3_{task_id}"
                        )
                        custom_status = st.text_input("Status personalizado (opcional)", key=f"top3_custom_{task_id}")
                        if st.button("Actualizar Status", key=f"update_top3_{task_id}"):
                            final_status = get_status(new_status, custom_status)
                            fecha_real = datetime.now().strftime("%Y-%m-%d") if final_status.lower()=="completado" else task_data.get("fecha_real","")
                            db.collection("top3").document(task_id).update({
                                "status": final_status,
                                "fecha_real": fecha_real
                            })
                            st.success("Status actualizado.")
                            try:
                                load_top3()
                            except:
                                pass
                        if st.button("🗑️ Eliminar", key=f"delete_top3_{task_id}"):
                            db.collection("top3").document(task_id).delete()
                            st.success("Tarea eliminada.")
                            try:
                                load_top3()
                            except:
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
                s = st.selectbox("Status", ["Pendiente","En proceso","Completado"], key="top3_new_status")
                custom_status = st.text_input("Status personalizado (opcional)", key="top3_new_custom")
                privado = st.checkbox("Marcar como privado")
                submit_new_top3 = st.form_submit_button("Guardar tarea")
            if submit_new_top3:
                final_status = get_status(s, custom_status)
                fecha_real = datetime.now().strftime("%Y-%m-%d") if final_status.lower()=="completado" else ""
                data = {
                    "usuario": user_code,
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
                try:
                    load_top3()
                except:
                    pass

    # =========== 3) Action Board ===========
    elif choice == "Action Board":
        st.subheader("✅ Acciones y Seguimiento - Resumen")
        # El ActionTaker o TeamLead ve todas; de lo contrario, solo propias
        is_actiontaker = ("roles" in st.session_state and st.session_state["roles"].get("ActionTaker") == user_code)
        if user_code == "ALECCION" or is_actiontaker:
            actions = list(db.collection("actions").stream())
        else:
            actions = list(db.collection("actions").where("usuario", "==", user_code).stream())

        action_container = st.empty()
        def load_actions():
            if user_code == "ALECCION" or is_actiontaker:
                _actions = list(db.collection("actions").stream())
            else:
                _actions = list(db.collection("actions").where("usuario","==",user_code).stream())
            action_container.empty()
            with action_container.container():
                st.markdown("---")
                if _actions:
                    for action in _actions:
                        action_id = action.id
                        act_data = action.to_dict()
                        st.markdown(f"**{act_data.get('accion','(Sin descripción)')}**")
                        st.write(f"Inicio: {act_data.get('fecha_inicio','')} | Compromiso: {act_data.get('fecha_compromiso','')} | Real: {act_data.get('fecha_real','')}")
                        if user_code == "ALECCION" or is_actiontaker:
                            st.write(f"**Usuario:** {act_data.get('usuario','')}")
                        status_val = act_data.get('status','')
                        color = status_colors.get(status_val,"black")
                        st.markdown(f"**Status:** <span style='color:{color};'>{status_val}</span>", unsafe_allow_html=True)
                        
                        new_status = st.selectbox(
                            "Editar status",
                            ["Pendiente","En proceso","Completado"],
                            index=(["Pendiente","En proceso","Completado"].index(status_val)
                                   if status_val in ["Pendiente","En proceso","Completado"] else 0),
                            key=f"action_status_{action_id}"
                        )
                        custom_status = st.text_input("Status personalizado (opcional)", key=f"action_custom_{action_id}")
                        if st.button("Actualizar Status", key=f"update_action_{action_id}"):
                            final_status = get_status(new_status, custom_status)
                            fecha_real = datetime.now().strftime("%Y-%m-%d") if final_status.lower()=="completado" else act_data.get("fecha_real","")
                            db.collection("actions").document(action_id).update({
                                "status": final_status,
                                "fecha_real": fecha_real
                            })
                            st.success("Status actualizado.")
                            try:
                                load_actions()
                            except:
                                pass
                        if st.button("🗑️ Eliminar", key=f"delete_action_{action_id}"):
                            db.collection("actions").document(action_id).delete()
                            st.success("Acción eliminada.")
                            try:
                                load_actions()
                            except:
                                pass
                        st.markdown("---")
                else:
                    st.info("No hay acciones registradas.")
        load_actions()
        if st.button("➕ Agregar Acción"):
            st.session_state.show_action_form = True
        if st.session_state.get("show_action_form"):
            with st.form("action_add_form"):
                st.markdown("### Nueva Acción")
                accion = st.text_input("Descripción de la acción")
                ti = st.date_input("Fecha de inicio")
                tc = st.date_input("Fecha compromiso")
                s = st.selectbox("Status", ["Pendiente","En proceso","Completado"], key="action_status_new")
                custom_status = st.text_input("Status personalizado (opcional)", key="action_custom_new")
                privado = st.checkbox("Marcar como privado")
                submit_new_action = st.form_submit_button("Guardar acción")
            if submit_new_action:
                final_status = get_status(s, custom_status)
                fecha_real = datetime.now().strftime("%Y-%m-%d") if final_status.lower()=="completado" else ""
                data = {
                    "usuario": user_code,
                    "accion": accion,
                    "fecha_inicio": ti.strftime("%Y-%m-%d"),
                    "fecha_compromiso": tc.strftime("%Y-%m-%d"),
                    "fecha_real": fecha_real,
                    "status": final_status,
                    "privado": privado,
                    "fecha": datetime.now().strftime("%Y-%m-%d")
                }
                db.collection("actions").add(data)
                st.success("Acción guardada.")
                st.session_state.show_action_form = False
                try:
                    load_actions()
                except:
                    pass

    # =========== 4) Escalation ===========
    elif choice == "Escalation":
        st.subheader("⚠️ Escalation")
        escalador = user_code
        with st.form("escalation_form"):
            razon = st.text_area("Razón")
            para_quien = st.selectbox("¿Para quién?", ["Miriam Sanchez", "Guillermo mayoral"])
            opciones_con = [code for code in valid_users if code != escalador]
            con_quien = st.multiselect("¿Con quién se tiene el tema?", options=opciones_con, format_func=lambda x: valid_users[x])
            submit_escalation = st.form_submit_button("Enviar escalación")
        if submit_escalation:
            mapping_para = {"Miriam Sanchez": "MSANCHEZ", "Guillermo mayoral": "GMAJORAL"}
            involucrados = [escalador, mapping_para.get(para_quien, para_quien)]
            if con_quien:
                involucrados.extend(con_quien)
            involucrados = list(set(involucrados))
            data_esc = {
                "escalador": escalador,
                "razon": razon,
                "para_quien": mapping_para.get(para_quien, para_quien),
                "con_quien": con_quien,
                "involucrados": involucrados,
                "fecha": datetime.now().strftime("%Y-%m-%d")
            }
            db.collection("escalations").add(data_esc)
            st.success("Escalación registrada.")
            st.warning(f"Los usuarios involucrados: {', '.join(involucrados)} han sido notificados.")
        
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

    # =========== 5) Recognition ===========
    elif choice == "Recognition":
        st.subheader("🎉 Recognition")
        with st.form("recognition_form"):
            destinatario = st.text_input("Email del destinatario")
            asunto = st.text_input("Asunto")
            mensaje = st.text_area("Mensaje de felicitación")
            submit_recognition = st.form_submit_button("Enviar reconocimiento")
        if submit_recognition:
            db.collection("recognitions").add({
                "usuario": user_code,
                "destinatario": destinatario,
                "asunto": asunto,
                "mensaje": mensaje,
                "fecha": datetime.now().strftime("%Y-%m-%d")
            })
            st.success("Reconocimiento enviado.")

    # =========== 6) Store DBSCHENKER ===========
    elif choice == "Store DBSCHENKER":
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

    # =========== 7) Wallet ===========
    elif choice == "Wallet":
        st.subheader("💰 Mi Wallet (DB COINS)")
        wallet_ref = db.collection("wallets").document(user_code)
        doc = wallet_ref.get()
        current_coins = 0
        if doc.exists:
            current_coins = doc.to_dict().get("coins", 0)
        st.write(f"**Saldo actual:** {current_coins} DB COINS")
        add_coins = st.number_input("Generar DB COINS:", min_value=1, step=1, value=10)
        if st.button("Generar DB COINS"):
            new_balance = current_coins + add_coins
            wallet_ref.set({"coins": new_balance})
            st.success(f"Generados {add_coins} DB COINS. Nuevo saldo: {new_balance}.")
    
    # =========== 8) Communications ===========
    elif choice == "Communications":
        st.subheader("📢 Mensajes Importantes")
        mensaje = st.text_area("📝 Escribe un mensaje o anuncio")
        if st.button("📩 Enviar mensaje"):
            db.collection("communications").document().set({
                "usuario": user_code,
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "mensaje": mensaje
            })
            st.success("Mensaje enviado.")

    # =========== 9) Calendar ===========
    elif choice == "Calendar":
        st.subheader("📅 Calendario")
        cal_option = st.radio("Selecciona una opción", ["Crear Evento", "Ver Calendario"])
        if cal_option == "Crear Evento":
            st.markdown("### Crear Evento")
            evento = st.text_input("📌 Nombre del evento")
            fecha_evento = st.date_input("📅 Selecciona la fecha")
            tipo_evento = st.radio("Tipo de evento", ["Público", "Privado"])
            if st.button("✅ Agendar evento"):
                event_data = {
                    "usuario": user_code,
                    "evento": evento,
                    "fecha": fecha_evento.strftime("%Y-%m-%d"),
                    "publico": True if tipo_evento == "Público" else False
                }
                db.collection("calendar").document().set(event_data)
                st.success("Evento agendado.")
        else:
            events_docs = db.collection("calendar").stream()
            events = []
            for doc in events_docs:
                data = doc.to_dict()
                if data.get("publico", False) or data.get("usuario", "") == user_code:
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

    # =========== 10) Roles (solo TL) ===========
    elif choice == "Roles":
        if user_code == "ALECCION":
            st.subheader("📝 Asignación de Roles Semanal (sin repetición)")
            st.write("Pulsa el botón para asignar roles de Timekeeper, ActionTaker y Coach a usuarios distintos.")
            if st.button("Asignar Roles"):
                posibles = [code for code in valid_users if code != "ALECCION"]
                # Asignar roles sin repetición
                roles_asignados = random.sample(posibles, 3)
                asignacion = {
                    "Timekeeper": roles_asignados[0],
                    "ActionTaker": roles_asignados[1],
                    "Coach": roles_asignados[2]
                }
                st.session_state["roles"] = asignacion
                st.write("Roles asignados:")
                st.json(asignacion)
        else:
            st.error("Acceso denegado. Esta opción es exclusiva para el TeamLead.")

    # =========== 11) Compliance (solo TL o Coach) ===========
    elif choice == "Compliance":
        if user_code == "ALECCION" or ("roles" in st.session_state and st.session_state["roles"].get("Coach") == user_code):
            st.subheader("📝 Compliance - Feedback")
            st.write("Selecciona a quién deseas dar feedback y escribe tu comentario.")
            feedback_options = [code for code in valid_users if code != user_code]
            target_user = st.selectbox("Dar feedback a:", feedback_options, format_func=lambda x: valid_users[x])
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
            st.error("Acceso denegado. Esta opción es exclusiva para el Coach o el TeamLead.")

# ================================
# Ejecutar la app principal
# ================================
show_main_app()

# ================================
# Lista de usuarios para referencia:
# ================================
# 1. VREYES     -> Reyes Escorsia Victor Manuel
# 2. RCRUZ      -> Cruz Madariaga Rodrigo
# 3. AZENTENO   -> Zenteno Perez Alejandro
# 4. XGUTIERREZ -> Gutierrez Hernandez Ximena
# 5. CNAPOLES   -> Napoles Escalante Christopher Enrique
# 6. MSANCHEZ   -> Sanchez Cruz Miriam Viviana
# 7. MHERNANDEZ -> Hernandez Ponce Maria Guadalupe
# 8. MGARCIA    -> Garcia Vazquez Mariana Aketzalli
# 9. ALECCION   -> Aleccion (TeamLead)
