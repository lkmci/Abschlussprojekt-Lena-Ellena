# Abschlussprojekt-Lena-Ellena

# 🧬 EKG-Analyse-Tool mit Streamlit

Dies ist eine interaktive Webanwendung zur Verwaltung und Visualisierung von EKG-Daten und Proband:innen-Informationen. Die App wurde mit [Streamlit](https://streamlit.io/) entwickelt und erlaubt es, medizinische Testdaten effizient auszuwerten.

---
## Funktionen
🔐 Login-System zur Zugriffsbeschränkung
👤 Verwaltung von Versuchspersonen inkl. Bild und Geburtsdatum
📈 Analyse und Visualisierung von EKG-Daten
    - Herzfrequenz
    - Herzfrequenzvariabilität (HRV)
    - Anomalieerkennung
📊 Vergleich mehrerer EKG-Datensätze
📝 Hinzufügen und Bearbeiten von Versuchspersonen und deren EKG-Daten

---
## Installation

Voraussetzung: 
- Python 3
- virtuelle Umgebung mit pdm install 
- Streamlit-App starten mit streamlit run main.py

---
## Zugangsdaten (Testzweck)
USER_CREDENTIALS = {
    "user1": "passwort"
}
 Tabs im Überblick

 ---
 ## Überblick der Tabs
1. Versuchsperson
- Auswahl einer gespeicherten Person
- Anzeige von Bild, Name, Alter

2. EKG-Daten
- Auswahl und Visualisierung von EKG-Daten
- Anzeige von Herzfrequenz, HRV, Anomalien
- Vergleich mehrerer EKGs

3. Nachrichten
- Auflistung der erkannten Anomalien für eine Person

4. Versuchsperson anlegen
- Eingabe von Name, Geburtsdatum
- Hochladen eines Bilds und optional EKG-Dateien

5. Versuchsperson bearbeiten
- Änderung von Personendaten
- Hochladen neuer Bilder oder EKGs

---
## Kontakt 
Bei Fragen oder Anregungen wenden Sie sich bitte an Lena Kurzthaler (kl4213@mci4me.at) oder an Ellena Hehle (he4116@mci4me.at). 