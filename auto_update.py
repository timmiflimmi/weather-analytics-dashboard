import schedule
import time
import logging
import os
from datetime import datetime, timedelta
from src.data_collector import WeatherDataCollector
import json

class WeatherAutoUpdater:
    def __init__(self, update_interval_hours=3, log_file='logs/weather_auto_update.log'):
        self.collector = WeatherDataCollector()
        self.update_interval = update_interval_hours
        self.log_file = log_file
        self.setup_logging()
        self.stats_file = 'data/update_stats.json'
        
    def setup_logging(self):
        """Richtet Logging ein"""
        # Logs-Ordner erstellen falls nicht vorhanden
        os.makedirs('logs', exist_ok=True)
        
        # Logging konfigurieren
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()  # Auch in Konsole ausgeben
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_stats(self):
        """Lädt Update-Statistiken"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            else:
                return {
                    'total_updates': 0,
                    'successful_updates': 0,
                    'failed_updates': 0,
                    'last_update': None,
                    'last_error': None,
                    'uptime_start': datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Statistiken: {e}")
            return self.load_stats()  # Fallback zu leeren Stats
    
    def save_stats(self, stats):
        """Speichert Update-Statistiken"""
        try:
            os.makedirs('data', exist_ok=True)
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Statistiken: {e}")
    
    def update_weather_data(self):
        """Aktualisiert Wetterdaten und protokolliert Ergebnis"""
        stats = self.load_stats()
        stats['total_updates'] += 1
        
        try:
            self.logger.info("🌤️ Starte automatisches Wetter-Update...")
            
            # Aktuelle Daten sammeln (ohne Forecast um API-Calls zu sparen)
            success = self.collector.collect_and_save(include_forecast=False)
            
            if success:
                stats['successful_updates'] += 1
                stats['last_update'] = datetime.now().isoformat()
                self.logger.info("✅ Wetter-Update erfolgreich abgeschlossen")
                
                # Datenbank-Status loggen
                self.log_database_status()
                
            else:
                stats['failed_updates'] += 1
                stats['last_error'] = f"Update fehlgeschlagen: {datetime.now().isoformat()}"
                self.logger.warning("⚠️ Wetter-Update fehlgeschlagen")
                
        except Exception as e:
            stats['failed_updates'] += 1
            stats['last_error'] = f"Exception: {str(e)} - {datetime.now().isoformat()}"
            self.logger.error(f"❌ Fehler beim Wetter-Update: {e}")
            
        finally:
            self.save_stats(stats)
    
    def log_database_status(self):
        """Loggt den aktuellen Status der Datenbank"""
        try:
            import pandas as pd
            
            if os.path.exists('data/weather_data.csv'):
                df = pd.read_csv('data/weather_data.csv')
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                total_entries = len(df)
                date_range = f"{df['date'].min()} bis {df['date'].max()}"
                latest_temp = df.iloc[-1]['temperature']
                latest_weather = df.iloc[-1]['weather_main']
                
                self.logger.info(f"📊 Datenbank-Status: {total_entries} Einträge, {date_range}")
                self.logger.info(f"🌡️ Aktuelle Werte: {latest_temp}°C, {latest_weather}")
                
            else:
                self.logger.warning("❌ Keine Wetterdaten-Datei gefunden")
                
        except Exception as e:
            self.logger.error(f"Fehler beim Loggen des DB-Status: {e}")
    
    def weekly_forecast_update(self):
        """Wöchentliches Update mit kompletten Forecast-Daten"""
        try:
            self.logger.info("📅 Starte wöchentliches Forecast-Update...")
            success = self.collector.collect_and_save(include_forecast=True)
            
            if success:
                self.logger.info("✅ Wöchentliches Forecast-Update erfolgreich")
            else:
                self.logger.warning("⚠️ Wöchentliches Forecast-Update fehlgeschlagen")
                
        except Exception as e:
            self.logger.error(f"❌ Fehler beim wöchentlichen Update: {e}")
    
    def cleanup_old_data(self, days_to_keep=30):
        """Entfernt alte Daten (älter als X Tage)"""
        try:
            import pandas as pd
            
            if not os.path.exists('data/weather_data.csv'):
                return
                
            df = pd.read_csv('data/weather_data.csv')
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            initial_count = len(df)
            
            # Nur neuere Daten behalten
            df_cleaned = df[df['timestamp'] >= cutoff_date]
            
            if len(df_cleaned) < initial_count:
                df_cleaned.to_csv('data/weather_data.csv', index=False)
                removed_count = initial_count - len(df_cleaned)
                self.logger.info(f"🧹 {removed_count} alte Einträge entfernt (älter als {days_to_keep} Tage)")
            else:
                self.logger.info("🧹 Keine alten Daten zum Entfernen gefunden")
                
        except Exception as e:
            self.logger.error(f"Fehler beim Cleanup: {e}")
    
    def print_status(self):
        """Zeigt aktuellen Status und Statistiken"""
        stats = self.load_stats()
        
        print("\n" + "="*50)
        print("🌤️  WEATHER AUTO-UPDATER STATUS")
        print("="*50)
        print(f"🕐 Update-Intervall: Alle {self.update_interval} Stunden")
        print(f"📊 Total Updates: {stats['total_updates']}")
        print(f"✅ Erfolgreich: {stats['successful_updates']}")
        print(f"❌ Fehlgeschlagen: {stats['failed_updates']}")
        
        if stats['last_update']:
            last_update = datetime.fromisoformat(stats['last_update'])
            print(f"🕐 Letztes Update: {last_update.strftime('%d.%m.%Y %H:%M:%S')}")
        
        if stats['last_error']:
            print(f"⚠️  Letzter Fehler: {stats['last_error']}")
        
        uptime_start = datetime.fromisoformat(stats['uptime_start'])
        uptime = datetime.now() - uptime_start
        print(f"⏱️  Laufzeit: {uptime.days} Tage, {uptime.seconds//3600} Stunden")
        
        # Nächstes geplantes Update
        next_run = schedule.next_run()
        if next_run:
            print(f"⏰ Nächstes Update: {next_run.strftime('%d.%m.%Y %H:%M:%S')}")
        
        print("="*50)
    
    def setup_schedule(self):
        """Richtet den Update-Schedule ein"""
        # Hauptupdate alle X Stunden
        schedule.every(self.update_interval).hours.do(self.update_weather_data)
        
        # Wöchentliches Forecast-Update
        schedule.every().sunday.at("06:00").do(self.weekly_forecast_update)
        
        # Tägliche Bereinigung alter Daten
        schedule.every().day.at("02:00").do(lambda: self.cleanup_old_data(30))
        
        # Status-Log alle 12 Stunden
        schedule.every(12).hours.do(self.print_status)
        
        self.logger.info(f"⏰ Schedule eingerichtet: Updates alle {self.update_interval} Stunden")
    
    def run_continuously(self):
        """Startet den kontinuierlichen Update-Service"""
        self.logger.info("🚀 Weather Auto-Updater gestartet!")
        self.print_status()
        
        # Erstes Update sofort ausführen
        self.logger.info("🌤️ Führe erstes Update aus...")
        self.update_weather_data()
        
        # Schedule einrichten
        self.setup_schedule()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Prüfe jede Minute auf geplante Jobs
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Auto-Updater gestoppt durch Benutzer")
        except Exception as e:
            self.logger.error(f"💥 Unerwarteter Fehler: {e}")
            # Nach Fehler 5 Minuten warten und weitermachen
            time.sleep(300)
            self.run_continuously()
    
    def run_once(self):
        """Führt ein einzelnes Update aus (für Tests)"""
        self.logger.info("🔄 Einmaliges Update...")
        self.update_weather_data()
        self.print_status()

def main():
    """Hauptfunktion mit Kommandozeilen-Optionen"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "once":
            # Einmaliges Update
            updater = WeatherAutoUpdater()
            updater.run_once()
            return
        elif sys.argv[1] == "status":
            # Nur Status anzeigen
            updater = WeatherAutoUpdater()
            updater.print_status()
            return
        elif sys.argv[1].isdigit():
            # Custom Intervall in Stunden
            interval = int(sys.argv[1])
            updater = WeatherAutoUpdater(update_interval_hours=interval)
        else:
            print("Usage: python auto_update.py [once|status|<hours>]")
            print("  once    - Führt ein einzelnes Update aus")
            print("  status  - Zeigt nur den Status an")
            print("  <hours> - Setzt Update-Intervall in Stunden")
            return
    else:
        # Standard: alle 3 Stunden
        updater = WeatherAutoUpdater(update_interval_hours=3)
    
    # Kontinuierlichen Service starten
    updater.run_continuously()

if __name__ == "__main__":
    main()