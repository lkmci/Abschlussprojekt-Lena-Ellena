import json

def load_person_data():
    """Lädt Personendaten aus der JSON-Datei 'data/person_db.json' und gibt sie als Python-Objekt zurück.

    Returns:
        dict: Die geladenen Personendaten aus der JSON-Datei."""
    file = open("data/person_db.json")
    person_data = json.load(file)
    return person_data

def get_person_list(person_data):

    """Eine Funktion die das dict mit den geladenen Personendaten nimmt und es als Namensliste wiedergibt"""
    list_of_names = []

    for eintrag in person_data:
        list_of_names.append(eintrag["lastname"] + ", " +  eintrag["firstname"])
    return list_of_names

def find_person_data_by_name(suchstring):
    """ Eine Funktion der Nachname, Vorname als ein String übergeben wird
    und die die Person als Dictionary zurück gibt"""

    person_data = load_person_data()
    if suchstring == "None":
        return {}

    two_names = suchstring.split(", ")
    vorname = two_names[1]
    nachname = two_names[0]

    for eintrag in person_data:
        if (eintrag["lastname"] == nachname and eintrag["firstname"] == vorname):
            return eintrag
    else:
        return {}