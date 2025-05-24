import requests
import os
from dotenv import load_dotenv

# .env Datei laden
load_dotenv()

# API-Key aus .env holen
API_KEY = os.getenv('WEATHER_API_KEY')
CITY = os.getenv('CITY_NAME', 'Hamburg')
COUNTRY = os.getenv('COUNTRY_CODE', 'DE')

def test_weather_api():
    """Testet die OpenWeatherMap API"""
    
    # API URL zusammenbauen
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY},{COUNTRY}&appid={API_KEY}&units=metric"
    
    try:
        # API Call
        response = requests.get(url)
        response.raise_for_status()  # Fehler werfen falls Status nicht OK
        
        # JSON Daten
        data = response.json()
        
        # Ausgabe
        print(f"🌤️  Wetter in {data['name']}:")
        print(f"🌡️  Temperatur: {data['main']['temp']}°C")
        print(f"🌡️  Gefühlt: {data['main']['feels_like']}°C")
        print(f"💧  Luftfeuchtigkeit: {data['main']['humidity']}%")
        print(f"📊  Beschreibung: {data['weather'][0]['description']}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API-Fehler: {e}")
        return None

if __name__ == "__main__":
    test_weather_api()