import requests
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

# .env Datei laden
load_dotenv()

class WeatherDataCollector:
    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.city = os.getenv('CITY_NAME', 'Hamburg')
        self.country = os.getenv('COUNTRY_CODE', 'DE')
        self.csv_file = 'data/weather_data.csv'
        
    def get_current_weather(self):
        """Holt aktuelle Wetterdaten von der API"""
        url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city},{self.country}&appid={self.api_key}&units=metric"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API-Fehler: {e}")
            return None
    
    def get_forecast_data(self):
        """Holt 5-Tage Vorhersagedaten (alle 3 Stunden)"""
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={self.city},{self.country}&appid={self.api_key}&units=metric"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Forecast API-Fehler: {e}")
            return None
    
    def extract_weather_data(self, raw_data, data_type='current'):
        """Extrahiert wichtige Daten aus der API-Antwort"""
        if not raw_data:
            return None
        
        if data_type == 'current':
            return {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': datetime.now().strftime('%H:%M:%S'),
                'city': raw_data['name'],
                'temperature': raw_data['main']['temp'],
                'feels_like': raw_data['main']['feels_like'],
                'temp_min': raw_data['main']['temp_min'],
                'temp_max': raw_data['main']['temp_max'],
                'humidity': raw_data['main']['humidity'],
                'pressure': raw_data['main']['pressure'],
                'weather_main': raw_data['weather'][0]['main'],
                'weather_description': raw_data['weather'][0]['description'],
                'wind_speed': raw_data.get('wind', {}).get('speed', 0),
                'wind_direction': raw_data.get('wind', {}).get('deg', 0),
                'cloudiness': raw_data.get('clouds', {}).get('all', 0),
                'visibility': raw_data.get('visibility', 0) / 1000,  # in km
                'sunrise': datetime.fromtimestamp(raw_data['sys']['sunrise']).strftime('%H:%M:%S'),
                'sunset': datetime.fromtimestamp(raw_data['sys']['sunset']).strftime('%H:%M:%S'),
                'data_type': 'current'
            }
        elif data_type == 'forecast':
            # Für Forecast-Daten (einzelner Eintrag aus der Liste)
            forecast_time = datetime.fromtimestamp(raw_data['dt'])
            return {
                'timestamp': forecast_time.strftime('%Y-%m-%d %H:%M:%S'),
                'date': forecast_time.strftime('%Y-%m-%d'),
                'time': forecast_time.strftime('%H:%M:%S'),
                'city': self.city,
                'temperature': raw_data['main']['temp'],
                'feels_like': raw_data['main']['feels_like'],
                'temp_min': raw_data['main']['temp_min'],
                'temp_max': raw_data['main']['temp_max'],
                'humidity': raw_data['main']['humidity'],
                'pressure': raw_data['main']['pressure'],
                'weather_main': raw_data['weather'][0]['main'],
                'weather_description': raw_data['weather'][0]['description'],
                'wind_speed': raw_data.get('wind', {}).get('speed', 0),
                'wind_direction': raw_data.get('wind', {}).get('deg', 0),
                'cloudiness': raw_data.get('clouds', {}).get('all', 0),
                'visibility': raw_data.get('visibility', 10) / 1000 if raw_data.get('visibility') else 10,  # in km
                'sunrise': '06:00:00',  # Forecast hat keine Sonnenzeiten
                'sunset': '20:00:00',
                'data_type': 'forecast'
            }
    
    def save_to_csv(self, weather_data):
        """Speichert Wetterdaten in CSV-Datei"""
        if not weather_data:
            return False
            
        # DataFrame erstellen
        df_new = pd.DataFrame([weather_data])
        
        # Prüfen ob CSV schon existiert
        if os.path.exists(self.csv_file):
            # Bestehende Daten laden
            df_existing = pd.read_csv(self.csv_file)
            
            # Duplikate vermeiden (gleicher Tag und gleiche Stunde)
            today_hour = datetime.now().strftime('%Y-%m-%d %H')
            existing_timestamps = df_existing['timestamp'].str[:13]  # Bis zur Stunde
            
            if today_hour not in existing_timestamps.values:
                # Neue Daten anhängen
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                df_combined.to_csv(self.csv_file, index=False)
                print(f"✅ Neue Daten gespeichert: {weather_data['temperature']}°C")
                return True
            else:
                print(f"ℹ️  Daten für diese Stunde bereits vorhanden")
                return False
        else:
            # Erste Daten speichern
            df_new.to_csv(self.csv_file, index=False)
            print(f"✅ CSV-Datei erstellt und erste Daten gespeichert: {weather_data['temperature']}°C")
            return True
    
    def collect_and_save(self, include_forecast=True):
        """Hauptfunktion: Daten holen und speichern"""
        print(f"🌤️  Sammle Wetterdaten für {self.city}...")
        
        all_data = []
        
        # 1. Aktuelle Daten holen
        raw_current = self.get_current_weather()
        if raw_current:
            current_data = self.extract_weather_data(raw_current, 'current')
            if current_data:
                all_data.append(current_data)
                print(f"✅ Aktuelle Daten: {current_data['temperature']}°C")
        
        # 2. Forecast-Daten holen (optional)
        if include_forecast:
            raw_forecast = self.get_forecast_data()
            if raw_forecast and 'list' in raw_forecast:
                print(f"📊 Verarbeite {len(raw_forecast['list'])} Forecast-Punkte...")
                
                for forecast_item in raw_forecast['list']:
                    forecast_data = self.extract_weather_data(forecast_item, 'forecast')
                    if forecast_data:
                        all_data.append(forecast_data)
                
                print(f"✅ {len(raw_forecast['list'])} Forecast-Datenpunkte hinzugefügt")
        
        # 3. Alle Daten speichern
        if all_data:
            self.save_multiple_to_csv(all_data)
            print(f"💾 Insgesamt {len(all_data)} Datenpunkte verarbeitet")
        
        return len(all_data) > 0
    
    def save_multiple_to_csv(self, weather_data_list):
        """Speichert mehrere Wetterdaten-Einträge in CSV"""
        if not weather_data_list:
            return False
        
        # DataFrame aus allen Daten erstellen
        df_new = pd.DataFrame(weather_data_list)
        
        # Prüfen ob CSV schon existiert
        if os.path.exists(self.csv_file):
            # Bestehende Daten laden
            df_existing = pd.read_csv(self.csv_file)
            
            # Duplikate anhand von timestamp vermeiden
            existing_timestamps = set(df_existing['timestamp'].values)
            
            # Nur neue Timestamps hinzufügen
            df_filtered = df_new[~df_new['timestamp'].isin(existing_timestamps)]
            
            if len(df_filtered) > 0:
                # Neue Daten anhängen
                df_combined = pd.concat([df_existing, df_filtered], ignore_index=True)
                df_combined = df_combined.sort_values('timestamp').reset_index(drop=True)
                df_combined.to_csv(self.csv_file, index=False)
                print(f"✅ {len(df_filtered)} neue Einträge hinzugefügt")
                return True
            else:
                print(f"ℹ️  Alle Daten bereits vorhanden (keine Duplikate)")
                return False
        else:
            # Erste Daten speichern
            df_new = df_new.sort_values('timestamp').reset_index(drop=True)
            df_new.to_csv(self.csv_file, index=False)
            print(f"✅ CSV-Datei erstellt mit {len(df_new)} Einträgen")
            return True
    
    def show_data_summary(self):
        """Zeigt Zusammenfassung der gesammelten Daten"""
        if not os.path.exists(self.csv_file):
            print("❌ Noch keine Daten gesammelt!")
            return
            
        df = pd.read_csv(self.csv_file)
        print(f"\n📊 Datensammlung Übersicht:")
        print(f"📅 Anzahl Einträge: {len(df)}")
        print(f"📅 Zeitraum: {df['date'].min()} bis {df['date'].max()}")
        print(f"🌡️  Temperatur-Bereich: {df['temperature'].min():.1f}°C - {df['temperature'].max():.1f}°C")
        print(f"💧  Durchschnittliche Luftfeuchtigkeit: {df['humidity'].mean():.1f}%")
        print(f"📊  Häufigste Wetterlage: {df['weather_main'].mode().iloc[0]}")
        
        # Aufschlüsselung nach Datentyp
        if 'data_type' in df.columns:
            data_types = df['data_type'].value_counts()
            print(f"📈  Datentypen: {dict(data_types)}")

def main():
    """Hauptfunktion"""
    collector = WeatherDataCollector()
    
    # Daten sammeln (mit Forecast)
    print("🚀 Sammle aktuelle + Forecast-Daten...")
    collector.collect_and_save(include_forecast=True)
    
    # Übersicht anzeigen
    collector.show_data_summary()

if __name__ == "__main__":
    main()