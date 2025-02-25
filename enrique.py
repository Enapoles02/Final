import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import streamlit.components.v1 as components
import json, random

# ================================
# Verificar que la clave "firebase" exista en st.secrets
# ================================
def load_firebase_config():
    try:
        firebase_config = st.secrets["firebase"]
        # Mostrar la configuración en la app para verificar
        st.write("Firebase config recibida desde st.secrets['firebase']:")
        st.json(firebase_config)
        return firebase_config
    except KeyError:
        st.error("No se encontró la clave 'firebase' en st.secrets. "
                 "Asegúrate de haber definido [firebase] en secrets.toml o en Streamlit Cloud.")
        st.stop()
    except Exception as e:
        st.error(f"Ocurrió un error al leer la config de Firebase: {e}")
        st.stop()

def init_firebase():
    firebase_config = load_firebase_config()
    # Convertir a dict en caso de que no lo sea
    if not isinstance(firebase_config, dict):
        firebase_config = firebase_config.to_dict()
    try:
        cred = credentials.Certificate(firebase_config)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        st.success("Firebase se inicializó correctamente.")
        return db
    except Exception as e:
        st.error(f"Error al inicializar Firebase: {e}")
        st.stop()

def main():
    st.title("Verificar Config de Firebase")
    # Inicializar Firebase
    db = init_firebase()

    st.write("Si ves este mensaje, significa que Firebase se inicializó y se recibió la configuración correctamente.")

    # Aquí podrías probar una operación sencilla en Firestore
    if st.button("Probar Firestore (Leer colecciones)"):
        try:
            collections = db.collections()
            col_names = [c.id for c in collections]
            st.write("Colecciones encontradas en Firestore:", col_names)
        except Exception as e:
            st.error(f"Error al leer colecciones: {e}")

if __name__ == "__main__":
    main()
