import json
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from scipy.signal import find_peaks

class EKGdata:

## Konstruktor der Klasse soll die EKG-Daten einlesen

    def __init__(self, ekg_dict):
        self.id = ekg_dict["id"]
        self.date = ekg_dict["date"]
        self.data = ekg_dict["result_link"]
        self.df = pd.read_csv(
            self.data,
            sep='\t',
            header=None,
            names=['Messwerte in mV', 'Zeit in ms'])
            #skiprows=lambda i: i % 10 != 0) # ↓ Downsampling: Nur jede 10. Zeile laden

    @staticmethod
    def load_by_id(ekg_list, ekg_id):
        """Lädt ein EKG-Objekt aus einer Liste anhand der EKG-ID.

            Input:
            ekg_list (list): Liste von EKG-Dictionaries.
            ekg_id (int or str): Gesuchte EKG-ID.

            Output:
            dict or None: EKG-Dictionary mit passender ID oder None, falls nicht gefunden."""
        for ekg in ekg_list:
            if ekg["id"] == int(ekg_id):
                return ekg
        return None
    
    def plot_time_series(self,peaks, anomalies=None):
        """Zeichnet die Zeitreihe der Messwerte mit Peaks und optionalen Anomalien als farbige Bereiche.

            Input:
            peaks und anomalien für die Dastellung

            Output:
            Plot mit Zeitreihe, Peaks und Anomalien-Hervorhebung."""
        peak_times = self.df.loc[peaks, "Zeit in ms"].tolist()
        peak_values = self.df.loc[peaks, "Messwerte in mV"].tolist()

        self.fig = px.line(self.df, x="Zeit in ms", y="Messwerte in mV")
        self.fig.add_trace(go.Scatter(
            x=peak_times,
            y=peak_values,
            mode='markers',
            marker=dict(color='red', size=8),
            name='Peaks'))
        zeit_start = self.df["Zeit in ms"][0]
        self.fig.update_layout(xaxis=dict(range=[zeit_start, (zeit_start+30000)]))
        if anomalies:
            anomalies_times = [a[0] for a in anomalies]
            for t in anomalies_times:
                self.fig.add_vrect(
                    x0 = t-100,
                    x1=t +100,
                    fillcolor="orange",
                    opacity=0.3,
                    layer="below",
                    line_width=0)
        return self.fig
    
    def find_peaks(self, distance=200, height=340):
        """Findet Peaks im EKG-Signal basierend auf Abstand, Höhe und Prominenz.

            Input:
            distance (int, optional): Minimale Distanz zwischen Peaks.
            height (int, optional): Minimale Höhe der Peaks.

            Output:gibt die Indizes der gefundenen Peaks wieder"""
        signal = self.df['Messwerte in mV']
        peaks, _ = find_peaks(signal, distance=distance, height=height, prominence=30)
        self.peaks = peaks
        return peaks
    
    
    def estimate_hr(self, peaks):
        """Schätzt die durchschnittliche Herzfrequenz (BPM) aus den Peaks.

            Input:
            peaks: Indizes der Peaks.

            Output:
            Durchschnittliche Herzfrequenz in bpm."""
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
        """Erzeugt ein DataFrame mit Herzfrequenzwerten und zugehörigen Zeitpunkten basierend auf Peaks.

            Input:
            peaks: Indizes der Peaks.

            Output:
            DataFrame mit Spalten "Zeit in ms" und "Herzfrequenz in bpm"."""
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
        """Erstellt einen Linienplot der Herzfrequenz über die Zeit.

            Inputs:
            hr_df : DataFrame mit Herzfrequenzwerten und Zeitpunkten.

            Output:
            Plot des Herzfrequenzverlaufs."""
        fig = px.line(hr_df, x="Zeit in ms", y="Herzfrequenz in bpm")
        return fig
    
    @staticmethod
    def Heartratevariation(peaks, zeit_in_ms):
        """Berechnet die Herzfrequenzvariabilität (RMSSD) aus den RR-Intervallen.

            Input:
            peaks: Indizes der Peaks.
            zeit_in_ms: Zeitpunkte der Messungen.

            Output:
            RMSSD-Wert (ms) als Maß der Herzfrequenzvariabilität."""
        rr_intervals = np.diff(zeit_in_ms.iloc[peaks])
        rmssd = np.sqrt(np.mean(np.square(np.diff(rr_intervals))))
        return rmssd

    def detect_anomalies(self, peaks, alter, min_hr=40):
        """Erkennt Anomalien basierend auf Herzfrequenzgrenzen (min/max bpm).

            Input:
            peaks: Indizes der Peaks.
            alter: Alter der Person für max Herzfrequenzberechnung.
            min_hr: Minimale Herzfrequenz.

            Output:
            Liste von (Zeitpunkt, bpm) für erkannte Anomalien."""

        max_hr = 220 - alter
        anomalies = []
        zeit_in_ms = self.df["Zeit in ms"]

        for i in range(len(peaks) - 1):
            interval = zeit_in_ms.iloc[peaks[i+1]] - zeit_in_ms.iloc[peaks[i]]
            if interval > 0:
                bpm = 60000/interval
                
                if bpm < min_hr or bpm > max_hr:
                    zeitpunkt = (zeit_in_ms.iloc[peaks[i+1]] + zeit_in_ms.iloc[peaks[i]])/2
                    anomalies.append((zeitpunkt, bpm))

        return anomalies
    
    # Kennzahlen extrahieren
    def get_ekg_stats(ekg_obj):
        """Extrahiert Kennzahlen aus einem EKG-Objekt um sie zu vergleichen.

            Input:
            ekg_obj: Instanz mit Methoden find_peaks, estimate_hr, Heartratevariation.

            Output:
            Dictionary mit Datum, EKG-ID, Testlänge, durchschnittlicher Herzfrequenz und Herzfrequenzvariablität."""
        peaks = ekg_obj.find_peaks()
        length_min = len(ekg_obj.df["Zeit in ms"]) / 60000
        avg_hr = ekg_obj.estimate_hr(peaks)
        hrv = ekg_obj.Heartratevariation(peaks, ekg_obj.df["Zeit in ms"])
        return {
            "Datum": ekg_obj.date,
            "EKG-ID": ekg_obj.id,
            "Testlänge (min)": round(length_min, 2),
            "Ø Herzfrequenz (bpm)": int(avg_hr),
            "HRV (ms)": int(hrv)}
    
    #Plot der durchschnittlichen Herzfrequenz mit Datum
    def plot_HFV(df_vergleich):
        """Erstellt einen Plot der Herzfrequenzvariabilität (HRV) über die Zeit.

            Input:
            df_vergleich: DataFrame mit Spalten "Datum" und "HRV (ms)".

            Output:
            Plot des HRV-Verlaufs bei mehreren EKG-Daten."""
        # Stelle sicher, dass Datum als Typ datetime erkannt wird, da in unserem Falls als String ausgegeben
        df_vergleich["Datum"] = pd.to_datetime(df_vergleich["Datum"])

        # Erstelle den Plot
        fig =  fig = px.line(
            df_vergleich,
            x="Datum",
            y="HRV (ms)",
            markers=True,
            title="Herzfrequenzvariabilität (HRV) über Zeit",
            labels={
                "Datum": "Testdatum",
                "HRV (ms)": "Herzfrequenzvariabilität (ms)"})
        # Punkte
        fig.add_trace(go.Scatter(
            x=df_vergleich["Datum"],
            y=df_vergleich["HRV (ms)"],
            mode ='markers',
            marker=dict(color='red', size=8),
            name="HFV-Werte"))
        #Nur die Testdaten als Ticks anzeigen
        fig.update_xaxes(
            tickformat="%d.%m.%Y",
            tickmode='array',
            tickvals=df_vergleich["Datum"])
        return fig
       

if __name__ == "__main__":
    print('Ja')
    file = open("data/person_db.json")
    person_data = json.load(file)
    ekg_dict = person_data[0]["ekg_tests"][0]
    ekg = EKGdata(ekg_dict)
    peaks = ekg.find_peaks(340, 2)
    avg_hr = ekg.estimate_hr(peaks)
    print(avg_hr)
    #fig = ekg.plot_time_series()
    #fig.show()
    rr_int = ekg.Heartratevariation(peaks)
    print(rr_int)
