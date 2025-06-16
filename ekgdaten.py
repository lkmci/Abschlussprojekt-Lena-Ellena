import json
import pandas as pd
import plotly.express as px

class EKGdata:
    """Klasse zur Verarbeitung und Analyse von EKG-Daten.

    Diese Klasse lädt EKG-Daten aus einer Datei, die in einem Dictionary angegeben ist,
    führt eine Downsampling-Operation durch, erkennt Spitzenwerte (Peaks),
    schätzt die Herzfrequenz und stellt die Daten graphisch dar.

    Attributes:
        id (str): Eindeutige Kennung des EKG-Datensatzes.
        date (str): Datum der Messung.
        data (str): Pfad zur Datei mit den EKG-Messwerten (CSV mit Tabulatoren).
        df (pandas.DataFrame): DataFrame mit den eingelesenen und downsampled Messwerten,
                               enthält Spalten 'Messwerte in mV' und 'Zeit in ms'.

    Methods:
        __init__(ekg_dict):
            Initialisiert die Klasse mit einem Dictionary, liest die EKG-Daten ein und downsamplet sie.
        
        load_by_id(ekg_list, ekg_id):
            Statische Methode, die aus einer Liste von EKG-Dictionaries das mit der angegebenen ID lädt.

        plot_time_series():
            Gibt eine Plotly-Figur mit der Zeitreihe der EKG-Messwerte zurück.

        find_peaks(threshold, respacing_factor):
            Findet Spitzenwerte (Peaks) im Signal über einem bestimmten Schwellenwert
            unter Verwendung eines Respacings (Downsampling).

        estimate_hr(peaks):
            Schätzt die durchschnittliche Herzfrequenz (in bpm) anhand der Zeitabstände zwischen Peaks.

        Heart_Rate(peaks):
            Gibt ein DataFrame mit den berechneten Herzfrequenzen und zugehörigen Zeitpunkten zurück.

        plot_Hear_Rate(hr_df):
            Statische Methode zur Visualisierung der Herzfrequenz als Zeitreihe."""

## Konstruktor der Klasse soll die EKG-Daten einlesen

    def __init__(self, ekg_dict):
        self.id = ekg_dict["id"]
        self.date = ekg_dict["date"]
        self.data = ekg_dict["result_link"]
        self.df = pd.read_csv(
            self.data,
            sep='\t',
            header=None,
            names=['Messwerte in mV', 'Zeit in ms'],
            skiprows=lambda i: i % 10 != 0) # ↓ Downsampling: Nur jede 10. Zeile laden

    @staticmethod
    def load_by_id(ekg_list, ekg_id):
        for ekg in ekg_list:
            if ekg["id"] == ekg_id:
                return ekg
        return None
    
    def plot_time_series(self):
        self.fig = px.line(self.df, x="Zeit in ms", y="Messwerte in mV")
        return self.fig
    
    def find_peaks(self, threshold, respacing_factor):


        # Respace the series
        series = self.df["Messwerte in mV"].iloc[::respacing_factor]
        

        # Filter the series
        series = series[series > threshold]

        peaks = []
        last = 0
        current = 0
        next = 0

        for index, row in series.items():
            last = current
            current = next
            next = row

            if last < current and current > next and current > threshold:
                peaks.append(index - respacing_factor)
                #if 0<= index <2000:
                    #peaks.append(current)
            
            self.df.loc[:, "is_peak"] = False
            self.df.loc[peaks, "is_peak"] = True
            self.df.loc[:, "is_peak"] = False
            self.df.loc[peaks, "is_peak"] = True

        return peaks
    
    
    def estimate_hr(self, peaks):
        heart_rates = []
        zeit_in_ms = self.df["Zeit in ms"]
        for i in range(len(peaks)-1):
            interval = zeit_in_ms.iloc[peaks[i+1]]-zeit_in_ms.iloc[peaks[i]]
            if interval > 0:
                bpm = 60000 / interval
                heart_rates.append(bpm)
        avg_heart_rate = sum(heart_rates) / len(heart_rates) if heart_rates else 0
        return avg_heart_rate
    
    #Herzrate als Plot
    def Heart_Rate(self, peaks):
        heart_rates = []
        times = []
        zeit_in_ms = self.df["Zeit in ms"]
        for i in range(len(peaks)-1):
            interval = zeit_in_ms.iloc[peaks[i+1]]-zeit_in_ms.iloc[peaks[i]]
            if interval > 0:
                bpm = 60000 / interval
                heart_rates.append(bpm)
                times.append(zeit_in_ms.iloc[peaks[i]])
        hr_df = pd.DataFrame({
        "Zeit in ms": times,
        "Herzfrequenz in bpm": heart_rates})
        return hr_df
    
    @staticmethod
    def plot_Hear_Rate(hr_df):
        fig = px.line(hr_df, x="Zeit in ms", y="Herzfrequenz in bpm")
        return fig
    
