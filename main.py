import streamlit as st
from read_data import load_person_data
from read_data import get_person_list
from read_data import find_person_data_by_name
from PIL import Image #paket zum anzeigen der bilder
from person import Person
from ekgdaten import EKGdata


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

    #Versuchspersondaten
    my_current_person = Person(person)
    st.write("Name: ", my_current_person.firstname, my_current_person.lastname)
    st.write("Geburtsjahr: ", my_current_person.date_of_birth)


with tab2:
    st.write("## EKG-Daten")

    #Dropdown Liste für EKG-tests
    ekg_tests = person.get('ekg_tests', [])
    ekg_ids = [test['id'] for test in ekg_tests]
    selected_ekg_id = st.selectbox("Wähle eine EKG-Test-ID aus:", ekg_ids)
    ekg_dict = EKGdata.load_by_id(ekg_tests, selected_ekg_id)
    ekg = EKGdata(ekg_dict)

    #EKGtest daten
    st.write("EKG-Test Datum: ", ekg.date)
    zeit_ekg = len(ekg.df["Zeit in ms"])/60000 # in min
    st.write("EKG-Test Länge in min: ", format(zeit_ekg, ".2f"))


    #Zeitstrahl für plot
    start_ekg = ekg.df["Zeit in ms"][0]
    selected_range = st.slider("Zeitbereich in ms wählen:", 0, 50000, (start_ekg,(start_ekg+10000)))
    slider_start_time = selected_range[0]
    slider_end_time = selected_range[1]

    #plot der EKG-Daten
    fig = ekg.plot_time_series()
    ekg.fig.update_layout(xaxis = dict(range=[slider_start_time, slider_end_time]))
    st.plotly_chart(fig, use_container_width=True)

    #Herzrate über die ges. Zeit
    threshold = 340
    respacing_factor = 2
    peaks = ekg.find_peaks(threshold, respacing_factor)
    st.write("Herzfrequenz basierend auf den Peaks in bpm: ", int(ekg.estimate_hr(peaks)))

    #Herzrate als plot

