import streamlit as st
from read_data import load_person_data
from read_data import get_person_list
from read_data import find_person_data_by_name
from PIL import Image #paket zum anzeigen der bilder

tab1, tab2 = st.tabs(["Versuchsperson", "EKG-Daten"])

with tab1:
    st.write("## Versuchsperson")
    person_data = load_person_data()
    person_names = get_person_list(person_data)

    st.write("# Versuchsperson auswählen")

    # Session State wird leer angelegt, solange er noch nicht existiert
    if 'current_user' not in st.session_state:
        st.session_state.current_user = 'None'

    # Dieses Mal speichern wir die Auswahl als Session State
    st.session_state.current_user = st.selectbox(
        'Versuchsperson',
        options = person_names, key="sbVersuchsperson")

    st.write("Der Name ist: ", st.session_state.current_user) 

    person = find_person_data_by_name(st.session_state.current_user)

    # Anzeigen eines Bilds mit Caption
    image = Image.open(person["picture_path"])
    st.image(image, caption=st.session_state.current_user)

with tab2:
    st.write("## EKG-Daten")