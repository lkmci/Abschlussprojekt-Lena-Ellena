import json

class Person:
    
    @staticmethod
    def load_person_data():
        """Lädt die Personendaten aus der JSON-Datei 'data/person_db.json' und gibt sie als Liste von Dictionaries zurück.
        Returns:
            list: Liste von Personen-Dictionaries."""
        file = open("data/person_db.json")
        person_data = json.load(file)
        return person_data

    @staticmethod
    def get_person_list(person_data):
        """Gibt eine Liste aller Personen-Namen in der Form "Nachname, Vorname" zurück.
        Args:
            person_data (list): Liste von Personen-Dictionaries.
        Returns:
            list: Liste von Strings mit Namen im Format "Nachname, Vorname"."""
        list_of_names = []

        for eintrag in person_data:
            list_of_names.append(eintrag["lastname"] + ", " +  eintrag["firstname"])
        return list_of_names
    
    @staticmethod
    def find_person_data_by_name(suchstring):
        """ Eine Funktion der Nachname, Vorname als ein String übergeben wird
        und die die Person als Dictionary zurück gibt"""

        person_data = Person.load_person_data()
        #print(suchstring)
        if suchstring == "None":
            return {}

        two_names = suchstring.split(", ")
        vorname = two_names[1]
        nachname = two_names[0]

        for eintrag in person_data:
            print(eintrag)
            if (eintrag["lastname"] == nachname and eintrag["firstname"] == vorname):
                print()

                return eintrag
        else:
            return {}
        

    def __init__(self, person_dict) -> None:
        self.date_of_birth = person_dict["date_of_birth"]
        self.firstname = person_dict["firstname"]
        self.lastname = person_dict["lastname"]
        self.picture_path = person_dict["picture_path"]
        self.id = person_dict["id"]