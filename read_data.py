import json

def load_person_data():
    """A Function that knows where the person database is and returns a dictionary with the persons
    Eine Funktion die weis, wo die Personendaten sind und ein dictionary """
    file = open("data/person_db.json")
    person_data = json.load(file)
    return person_data

def get_person_list(person_data):

    """A Function that takes the persons-dictionary and returns a list auf all person names"""
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