import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

class WeatherVisualizer:
    def __init__(self, csv_file='data/weather_data.csv'):
        self.csv_file = csv_file
        self.df = None
        self.load_data()
        
    def load_data(self):
        """Lädt Wetterdaten aus CSV"""
        if not os.path.exists(self.csv_file):
            print("❌ Keine Wetterdaten gefunden! Führe zuerst data_collector.py aus.")
            return False
            
        self.df = pd.read_csv(self.csv_file)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.df['date'] = pd.to_datetime(self.df['date'])
        
        print(f"✅ {len(self.df)} Datenpunkte geladen")
        return True
    
    def create_temperature_timeline(self):
        """Interaktive Temperatur-Timeline mit Plotly"""
        if self.df is None:
            return None
            
        fig = go.Figure()
        
        # Temperatur-Linie
        fig.add_trace(go.Scatter(
            x=self.df['timestamp'],
            y=self.df['temperature'],
            mode='lines+markers',
            name='Temperatur',
            line=dict(color='#ff6b6b', width=3),
            marker=dict(size=6),
            hovertemplate='<b>%{x}</b><br>Temperatur: %{y:.1f}°C<extra></extra>'
        ))
        
        # Gefühlte Temperatur
        fig.add_trace(go.Scatter(
            x=self.df['timestamp'],
            y=self.df['feels_like'],
            mode='lines',
            name='Gefühlte Temperatur',
            line=dict(color='#ffa726', width=2, dash='dash'),
            hovertemplate='<b>%{x}</b><br>Gefühlt: %{y:.1f}°C<extra></extra>'
        ))
        
        fig.update_layout(
            title='🌡️ Temperatur-Verlauf über Zeit',
            xaxis_title='Datum & Zeit',
            yaxis_title='Temperatur (°C)',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def create_weather_distribution(self):
        """Wetterarten-Verteilung als Donut-Chart"""
        if self.df is None:
            return None
            
        weather_counts = self.df['weather_main'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=weather_counts.index,
            values=weather_counts.values,
            hole=0.4,
            textinfo='label+percent',
            marker_colors=['#3498db', '#e74c3c', '#f39c12', '#2ecc71', '#9b59b6']
        )])
        
        fig.update_layout(
            title='☁️ Wetterarten-Verteilung',
            height=400,
            template='plotly_white'
        )
        
        return fig
    
    def create_humidity_temperature_scatter(self):
        """Luftfeuchtigkeit vs. Temperatur Scatter Plot"""
        if self.df is None:
            return None
            
        fig = px.scatter(
            self.df,
            x='temperature',
            y='humidity',
            color='weather_main',
            size='wind_speed',
            hover_data=['timestamp', 'weather_description'],
            title='💧 Luftfeuchtigkeit vs. Temperatur',
            labels={
                'temperature': 'Temperatur (°C)',
                'humidity': 'Luftfeuchtigkeit (%)',
                'weather_main': 'Wetter'
            },
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def create_daily_temperature_range(self):
        """Tägliche Min/Max Temperaturen"""
        if self.df is None:
            return None
            
        # Tägliche Statistiken berechnen
        daily_stats = self.df.groupby('date').agg({
            'temperature': ['min', 'max', 'mean'],
            'humidity': 'mean',
            'weather_main': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else x.iloc[0]
        }).round(1)
        
        daily_stats.columns = ['temp_min', 'temp_max', 'temp_mean', 'humidity_mean', 'weather_mode']
        daily_stats = daily_stats.reset_index()
        
        fig = go.Figure()
        
        # Min-Max Bereich als Füllung
        fig.add_trace(go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['temp_max'],
            fill=None,
            mode='lines',
            line_color='rgba(0,0,0,0)',
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['temp_min'],
            fill='tonexty',
            mode='lines',
            line_color='rgba(0,0,0,0)',
            name='Min-Max Bereich',
            fillcolor='rgba(255, 107, 107, 0.3)'
        ))
        
        # Durchschnittstemperatur
        fig.add_trace(go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['temp_mean'],
            mode='lines+markers',
            name='Durchschnitt',
            line=dict(color='#ff6b6b', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='📊 Tägliche Temperatur-Bereiche',
            xaxis_title='Datum',
            yaxis_title='Temperatur (°C)',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_wind_compass(self):
        """Wind-Richtung und -Geschwindigkeit als Polar Plot"""
        if self.df is None:
            return None
            
        # Nur Daten mit Wind > 0
        wind_data = self.df[self.df['wind_speed'] > 0].copy()
        
        if len(wind_data) == 0:
            print("ℹ️  Keine Winddaten verfügbar")
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=wind_data['wind_speed'],
            theta=wind_data['wind_direction'],
            mode='markers',
            marker=dict(
                size=wind_data['wind_speed'] * 3,
                color=wind_data['temperature'],
                colorscale='RdYlBu_r',
                colorbar=dict(title="Temperatur (°C)"),
                opacity=0.7
            ),
            text=wind_data['timestamp'].dt.strftime('%d.%m %H:%M'),
            hovertemplate='<b>%{text}</b><br>Wind: %{r:.1f} m/s<br>Richtung: %{theta}°<extra></extra>'
        ))
        
        fig.update_layout(
            title='🧭 Wind-Richtung und -Geschwindigkeit',
            polar=dict(
                radialaxis=dict(visible=True, range=[0, wind_data['wind_speed'].max() * 1.1]),
                angularaxis=dict(direction='clockwise', rotation=90)
            ),
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def create_dashboard(self, save_html=True):
        """Erstellt ein komplettes Dashboard mit allen Charts"""
        if self.df is None:
            print("❌ Keine Daten verfügbar!")
            return
            
        print("🎨 Erstelle interaktives Dashboard...")
        
        # Alle Charts erstellen
        temp_timeline = self.create_temperature_timeline()
        weather_dist = self.create_weather_distribution()
        humidity_scatter = self.create_humidity_temperature_scatter()
        daily_range = self.create_daily_temperature_range()
        wind_compass = self.create_wind_compass()
        
        # Charts anzeigen
        if temp_timeline:
            temp_timeline.show()
        if weather_dist:
            weather_dist.show()
        if humidity_scatter:
            humidity_scatter.show()
        if daily_range:
            daily_range.show()
        if wind_compass:
            wind_compass.show()
        
        # Als HTML speichern (optional)
        if save_html:
            dashboard_html = self.create_html_dashboard()
            with open('weather_dashboard.html', 'w', encoding='utf-8') as f:
                f.write(dashboard_html)
            print("💾 Dashboard als 'weather_dashboard.html' gespeichert")
    
    def create_html_dashboard(self):
        """Erstellt HTML-Code für ein komplettes Dashboard"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Weather Analytics Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .header { text-align: center; color: #2c3e50; margin-bottom: 30px; }
                .chart-container { background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
                .stat-card { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .stat-value { font-size: 2em; font-weight: bold; color: #3498db; }
                .stat-label { color: #7f8c8d; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌤️ Weather Analytics Dashboard</h1>
                <p>Interaktive Wetteranalyse für Hamburg</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value" id="total-points">--</div>
                    <div class="stat-label">Datenpunkte</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="temp-range">--</div>
                    <div class="stat-label">Temperatur-Spanne</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="avg-humidity">--</div>
                    <div class="stat-label">⌀ Luftfeuchtigkeit</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="main-weather">--</div>
                    <div class="stat-label">Hauptwetter</div>
                </div>
            </div>
            
            <div class="chart-container">
                <div id="temperature-timeline"></div>
            </div>
            
            <div class="chart-container">
                <div id="weather-distribution"></div>
            </div>
            
            <div class="chart-container">
                <div id="humidity-scatter"></div>
            </div>
            
            <script>
                // Hier würden die Plotly-Charts eingefügt werden
                // Das wäre ein komplexeres HTML-Template
                document.getElementById('total-points').textContent = 'Dashboard bereit!';
            </script>
        </body>
        </html>
        """
    
    def print_data_insights(self):
        """Zeigt interessante Daten-Insights"""
        if self.df is None:
            return
            
        print("\n🔍 Wetter-Insights:")
        print(f"📊 Datenpunkte: {len(self.df)}")
        print(f"🌡️  Temperatur: {self.df['temperature'].min():.1f}°C - {self.df['temperature'].max():.1f}°C")
        print(f"💧  Luftfeuchtigkeit: {self.df['humidity'].min():.0f}% - {self.df['humidity'].max():.0f}%")
        print(f"💨  Max. Windgeschwindigkeit: {self.df['wind_speed'].max():.1f} m/s")
        print(f"☁️  Häufigste Wetterlage: {self.df['weather_main'].mode().iloc[0]}")
        
        # Temperatur-Trends
        temp_trend = self.df['temperature'].diff().mean()
        trend_text = "steigend" if temp_trend > 0 else "fallend" if temp_trend < 0 else "stabil"
        print(f"📈  Temperatur-Trend: {trend_text} ({temp_trend:.2f}°C/Stunde)")

def main():
    """Hauptfunktion"""
    print("🎨 Weather Visualizer gestartet...")
    
    visualizer = WeatherVisualizer()
    
    if visualizer.df is not None:
        # Data Insights
        visualizer.print_data_insights()
        
        # Dashboard erstellen
        visualizer.create_dashboard(save_html=True)
        
        print("\n✅ Alle Charts wurden angezeigt!")
        print("💡 Tipp: Charts sind interaktiv - zoomen, schwenken, hover!")
    else:
        print("❌ Keine Daten gefunden. Führe zuerst 'python src/data_collector.py' aus.")

if __name__ == "__main__":
    main()