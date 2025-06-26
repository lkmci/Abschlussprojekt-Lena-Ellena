import streamlit as st
from read_data import load_person_data
from read_data import get_person_list
from read_data import find_person_data_by_name
from PIL import Image #paket zum anzeigen der bilder
from person import Person
from ekgdaten import EKGdata
import plotly.express as px
from datetime import date,datetime
import os
import json
import pandas as pd


st.set_page_config(
    page_title="Meine EKG-App",
    layout="wide",  # <- das aktiviert den Vollbildmodus
    initial_sidebar_state="collapsed"  # optional: Seitenleiste standardmäßig einklappen
)

# Zugangsdaten (z.B. aus sicherer Quelle, hier nur als Beispiel)
USER_CREDENTIALS = {
    "user1": "passwort"
}

# Login-Funktion
def login():
    st.title("🔐 Login")
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")
    login_btn = st.button("Login")

    if login_btn:
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state["logged_in"] = True
            st.success("Login erfolgreich!")
            st.rerun()
        else:
            st.error("Benutzername oder Passwort falsch.")

# Login-Abfrage
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()  #Stoppt die Ausführung, wenn nicht eingeloggt


tab1, tab2, tab3, tab4, tab5 = st.tabs(["Versuchsperson", "EKG-Daten","Nachrichten", "Versuchsperson anlegen", "Versuchsperson bearbeiten" ])

#Logout-Button
if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

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
    
    geburtstag = datetime.strptime(my_current_person.date_of_birth, "%d.%m.%Y").date()
    heute = date.today()
    # Alter berechnen
    alter = heute.year - geburtstag.year - ((heute.month, heute.day) < (geburtstag.month, geburtstag.day))
    st.write("Geburtsjahr: ", alter)


with tab2:
    st.write("## EKG-Daten")

    #Dropdown Liste für EKG-tests
    ekg_tests = person.get('ekg_tests', [])
    ekg_ids = [test['id'] for test in ekg_tests]
    selected_ekg_id = st.selectbox("Wähle eine EKG-Test-ID aus:", ekg_ids)
    ekg_dict = EKGdata.load_by_id(ekg_tests, selected_ekg_id)

    if ekg_dict:
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
        threshold = 340
        respacing_factor = 2
        peaks = ekg.find_peaks(threshold, respacing_factor)
        fig = ekg.plot_time_series(peaks)
        ekg.fig.update_layout(xaxis = dict(range=[slider_start_time, slider_end_time]))
        st.plotly_chart(fig, use_container_width=True)

        #Herzrate über die ges. Zeit
        threshold = 340
        respacing_factor = 2
        peaks = ekg.find_peaks(threshold, respacing_factor)
        st.write("Herzfrequenz basierend auf den Peaks in bpm: ", int(ekg.estimate_hr(peaks)))

        #Herzrate als plot
        hr_df = ekg.Heart_Rate(peaks)
        fig = EKGdata.plot_Hear_Rate(hr_df)
        fig.update_layout(xaxis = dict(range=[slider_start_time, slider_end_time])) #Plot auch in der range von dem slider
        st.plotly_chart(fig, use_container_width=True)
        
        #Herzfrequenzvariablität
        st.write("Herzfrequenzvariablität in ms: ", int(ekg.Heartratevariation(peaks)))
       
        #Vergleich bei mehreren EGK-Daten
        st.write("Wähle beliebig viele EKGs zum Vergleich aus:")

        # Multiselect erlaubt Auswahl mehrerer IDs
        selected_ekg_ids = st.multiselect("Wähle EKG-IDs:", ekg_ids)

        # Wenn mindestens eine EKG-ID ausgewählt wurde
        if selected_ekg_ids:
            ekg_stat_list = []

            for ekg_id in selected_ekg_ids:
                ekg_dict1 = EKGdata.load_by_id(ekg_tests, ekg_id)
                ekg1 = EKGdata(ekg_dict1)
                ekg_stat_list.append(EKGdata.get_ekg_stats(ekg1))

            df_vergleich = pd.DataFrame(ekg_stat_list)

            st.subheader("Vergleich mehrerer EKG-Tests")
            st.dataframe(df_vergleich)

            #HFV als Plot über die Zeit
            fig = EKGdata.plot_HFV(df_vergleich)
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("Bitte mindestens einen EKG-Test auswählen.")

        


    else:
        st.write("Keine EKG-Daten vorhanden.")


with tab3:
    if ekg_dict:
        #Anomaliererkennung
        anomalies = ekg.detect_anomalies(peaks, alter)

        if anomalies:
            for zeitpunkt, bpm in anomalies:
                st.write(f"Auffälligkeit bei {zeitpunkt:.0f} ms: {bpm:.1f} BPM")
        else:
            st.write("Keine Anomalien vorhanden.")

    else:
        st.write("Keine EKG-Daten vorhanden.")



with tab4:
    st.write("Personendaten anlegen")
    
    min_date = date(1900, 1, 1)
    max_date = date.today()

    with st.form("person_form"):
        firstname = st.text_input("Vorname")
        lastname = st.text_input("Nachname")
        date_of_birth = st.date_input("Geburtsjahr", value=max_date, min_value=min_date, max_value=max_date)
        st.write("Bitte laden Sie vor dem Speichern ein Bild der Versuchsperson hoch.")

        
        data = load_person_data()

        # IDs auslesen, falls "id" noch nicht existiert, auf 0 setzen
        existing_ids = [person.get("id", 0) for person in data]
        
        # nächste ID bestimmen
        next_id = max(existing_ids) + 1 if existing_ids else 1
        #Bild und EKG-Daten hochladen
        uploaded_file = st.file_uploader("Bild hochladen (nur JPG)", type=["jpg", "jpeg"])
        ekg_txt_file = st.file_uploader("EKG-Daten optional hochladen (als .txt)", type=["txt"])

        #Speicherbutton
        submitted = st.form_submit_button("Speichern")

        if submitted:
            if firstname and lastname and date_of_birth and uploaded_file is not None:
                

                img_dir = "uploaded_file"
                os.makedirs(img_dir, exist_ok=True)
                # Bild unter Vorname_Nachname_ID.jpg speichern
                img_path = os.path.join(img_dir, f"{firstname}_{lastname}_{next_id}.jpg")

                with open(img_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                  # Optional: EKG-Datei speichern
                ekg_dir = "data/ekg"
                os.makedirs(ekg_dir, exist_ok=True)
                ekg_tests = []

                if ekg_txt_file is not None:
                    ekg_file_path = os.path.join(ekg_dir, f"ekg_{next_id}_1.txt")
                    with open(ekg_file_path, "wb") as f:
                        f.write(ekg_txt_file.getbuffer())

                    # Beispielhafte EKG-Metadaten (anpassbar)
                    ekg_tests.append({
                        "id": f"ekg_{next_id}_1",
                        "date": str(date.today()),
                        "file_path": ekg_file_path
                    })


                new_person = {
                    "id": next_id,
                    "firstname": firstname,
                    "lastname": lastname,
                    "date_of_birth": date_of_birth.strftime("%d.%m.%Y"),
                    "picture_path": img_path,
                }

                # Alte Daten laden, neue Person anhängen und speichern
                data.append(new_person)

                # JSON-Datei speichern

                with open("data/person_db.json", "w") as f:
                    json.dump(data, f, indent=4)

                st.success(f"{firstname} {lastname} wurde erfolgreich hinzugefügt!")

                # Optional: Seite neu laden
                st.rerun()
            else:
                st.error("Bitte fülle alle Pflichtfelder aus!")


with tab5:
    st.write("Versuchsperson bearbeiten")

    #Bild bearbeiten
    uploaded_file = st.file_uploader("Bild hochladen (nur JPG)", type=["jpg", "jpeg"])
    #EKG-Daten hochladen
    uploaded_ekg = st.file_uploader("Neue EKG-Datei hochladen (TXT)", type=["txt"])
    ekg_date = date.today().strftime("%d.%m.%Y")  # Automatisches Datum



    with st.form("edit_form"):
        new_firstname = st.text_input("Vorname", value=person["firstname"])
        new_lastname = st.text_input("Nachname", value=person["lastname"])
        new_birthday = st.date_input("Geburtstag", value=geburtstag, min_value=min_date, max_value=max_date)
        
        

        submitted = st.form_submit_button("Änderungen speichern")

        if submitted:
            # Lade alle Personendaten
            data = load_person_data()

            # Finde den Index der aktuellen Person
            for idx, p in enumerate(data):
                if p["id"] == person["id"]:
                    data[idx]["firstname"] = new_firstname
                    data[idx]["lastname"] = new_lastname
                    data[idx]["date_of_birth"] = new_birthday.strftime("%d.%m.%Y")
                    
                    #Bild überspeichern
                    if uploaded_file is not None:
                        picture_path = data[idx]["picture_path"]  # alten Pfad behalten
                        with open(picture_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                     # EKG speichern
                    if uploaded_ekg is not None:
                        ekg_dir = "data/ekg_data"
                        os.makedirs(ekg_dir, exist_ok=True)
                        ekg_filename = f"{p['id']}_{ekg_date.replace('.', '-')}.txt"
                        ekg_path = os.path.join(ekg_dir, ekg_filename)

                        with open(ekg_path, "wb") as f:
                            f.write(uploaded_ekg.getbuffer())

                        new_ekg_entry = {
                            "id": len(p.get("ekg_tests", [])) + 1,
                            "date": ekg_date,
                            "file_path": ekg_path
                        }

                        if "ekg_tests" not in data[idx]:
                            data[idx]["ekg_tests"] = []

                        data[idx]["ekg_tests"].append(new_ekg_entry)
                    break

            # Änderungen speichern
            import json
            with open("data/person_db.json", "w") as f:
                json.dump(data, f, indent=4)

            st.success("Daten wurden aktualisiert.")
            st.rerun()