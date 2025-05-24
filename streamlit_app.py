import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta
import time
from src.data_collector import WeatherDataCollector
from src.visualizer import WeatherVisualizer

# Streamlit Page Config
st.set_page_config(
    page_title="Weather Analytics Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS für besseres Design
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
        margin: 1rem 0;
    }
    .sidebar-info {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitWeatherDashboard:
    def __init__(self):
        self.csv_file = 'data/weather_data.csv'
        self.collector = WeatherDataCollector()
        self.visualizer = WeatherVisualizer()
        
    def load_data(self):
        """Lädt Wetterdaten und zeigt Status"""
        try:
            if os.path.exists(self.csv_file):
                df = pd.read_csv(self.csv_file)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['date'] = pd.to_datetime(df['date'])
                return df
            else:
                st.error("❌ Keine Wetterdaten gefunden!")
                return None
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Daten: {e}")
            return None
    
    def create_sidebar(self, df):
        """Erstellt die Sidebar mit Kontrollen und Infos"""
        st.sidebar.markdown("## 🎛️ Dashboard Kontrollen")
        
        # Data Refresh Button
        if st.sidebar.button("🔄 Daten aktualisieren", type="primary"):
            with st.spinner("Sammle neue Wetterdaten..."):
                success = self.collector.collect_and_save(include_forecast=True)
                if success:
                    st.sidebar.success("✅ Daten erfolgreich aktualisiert!")
                    st.rerun()
                else:
                    st.sidebar.error("❌ Fehler beim Aktualisieren")
        
        # Auto-Refresh
        st.sidebar.markdown("### ⏰ Auto-Refresh")
        auto_refresh = st.sidebar.checkbox("Auto-Refresh aktivieren", value=False)
        if auto_refresh:
            refresh_interval = st.sidebar.selectbox(
                "Intervall (Minuten)",
                [5, 10, 15, 30, 60],
                index=2
            )
            st.sidebar.info(f"🔄 Dashboard aktualisiert sich alle {refresh_interval} Minuten")
            # Auto-refresh mit Streamlit
            time.sleep(refresh_interval * 60)
            st.rerun()
        
        # Data Summary
        if df is not None:
            st.sidebar.markdown("### 📊 Daten-Übersicht")
            st.sidebar.markdown(f"""
            <div class="sidebar-info">
                <strong>📅 Datenpunkte:</strong> {len(df)}<br>
                <strong>📅 Zeitraum:</strong> {df['date'].min().strftime('%d.%m')} - {df['date'].max().strftime('%d.%m')}<br>
                <strong>🌡️ Temp-Bereich:</strong> {df['temperature'].min():.1f}°C - {df['temperature'].max():.1f}°C<br>
                <strong>💧 ⌀ Luftfeuchtigkeit:</strong> {df['humidity'].mean():.0f}%<br>
                <strong>☁️ Hauptwetter:</strong> {df['weather_main'].mode().iloc[0]}
            </div>
            """, unsafe_allow_html=True)
        
        # Filter Controls
        st.sidebar.markdown("### 🎯 Filter")
        date_range = st.sidebar.date_input(
            "Datum-Bereich",
            value=(df['date'].min().date(), df['date'].max().date()) if df is not None else (datetime.now().date(), datetime.now().date()),
            min_value=df['date'].min().date() if df is not None else datetime.now().date(),
            max_value=df['date'].max().date() if df is not None else datetime.now().date()
        )
        
        # Download Data
        st.sidebar.markdown("### 💾 Daten Export")
        if df is not None:
            csv = df.to_csv(index=False)
            st.sidebar.download_button(
                label="📥 CSV herunterladen",
                data=csv,
                file_name=f"weather_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        return date_range
    
    def create_metrics_row(self, df):
        """Erstellt die obere Metriken-Zeile"""
        if df is None:
            return
            
        # Aktuelle Werte (neuester Datenpunkt)
        latest = df.iloc[-1]
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="🌡️ Aktuelle Temperatur",
                value=f"{latest['temperature']:.1f}°C",
                delta=f"{latest['feels_like'] - latest['temperature']:.1f}°C gefühlt"
            )
        
        with col2:
            st.metric(
                label="💧 Luftfeuchtigkeit",
                value=f"{latest['humidity']:.0f}%",
                delta=f"{df['humidity'].mean() - latest['humidity']:.0f}% vs ⌀"
            )
        
        with col3:
            st.metric(
                label="💨 Windgeschwindigkeit",
                value=f"{latest['wind_speed']:.1f} m/s",
                delta=f"{latest['wind_direction']:.0f}° Richtung"
            )
        
        with col4:
            st.metric(
                label="☁️ Bewölkung",
                value=f"{latest['cloudiness']:.0f}%",
                delta=f"{latest['visibility']:.1f}km Sicht"
            )
        
        with col5:
            st.metric(
                label="📊 Wetter",
                value=latest['weather_main'],
                delta=latest['weather_description']
            )
    
    def create_temperature_chart(self, df):
        """Temperatur-Verlauf Chart"""
        fig = go.Figure()
        
        # Temperatur-Linie
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['temperature'],
            mode='lines+markers',
            name='Temperatur',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=4),
            hovertemplate='<b>%{x}</b><br>Temperatur: %{y:.1f}°C<extra></extra>'
        ))
        
        # Gefühlte Temperatur
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['feels_like'],
            mode='lines',
            name='Gefühlte Temperatur',
            line=dict(color='#4ECDC4', width=2, dash='dash'),
            hovertemplate='<b>%{x}</b><br>Gefühlt: %{y:.1f}°C<extra></extra>'
        ))
        
        # Min/Max Bereich
        daily_stats = df.groupby(df['timestamp'].dt.date).agg({
            'temperature': ['min', 'max']
        }).round(1)
        daily_stats.columns = ['temp_min', 'temp_max']
        daily_stats = daily_stats.reset_index()
        
        fig.add_trace(go.Scatter(
            x=daily_stats['timestamp'],
            y=daily_stats['temp_max'],
            fill=None,
            mode='lines',
            line_color='rgba(0,0,0,0)',
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_stats['timestamp'],
            y=daily_stats['temp_min'],
            fill='tonexty',
            mode='lines',
            line_color='rgba(0,0,0,0)',
            name='Tägliche Spanne',
            fillcolor='rgba(255, 107, 107, 0.2)'
        ))
        
        fig.update_layout(
            title='🌡️ Temperatur-Verlauf über Zeit',
            xaxis_title='Datum & Zeit',
            yaxis_title='Temperatur (°C)',
            hovermode='x unified',
            template='plotly_white',
            height=500,
            showlegend=True
        )
        
        return fig
    
    def create_weather_pie(self, df):
        """Wetterarten-Verteilung"""
        weather_counts = df['weather_main'].value_counts()
        
        colors = ['#3498DB', '#E74C3C', '#F39C12', '#2ECC71', '#9B59B6', '#1ABC9C', '#E67E22']
        
        fig = go.Figure(data=[go.Pie(
            labels=weather_counts.index,
            values=weather_counts.values,
            hole=0.4,
            textinfo='label+percent+value',
            textposition='outside',
            marker_colors=colors[:len(weather_counts)],
            hovertemplate='<b>%{label}</b><br>Anzahl: %{value}<br>Anteil: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title='☁️ Wetterarten-Verteilung',
            height=400,
            template='plotly_white',
            showlegend=False
        )
        
        return fig
    
    def create_humidity_scatter(self, df):
        """Luftfeuchtigkeit vs Temperatur"""
        fig = px.scatter(
            df,
            x='temperature',
            y='humidity',
            color='weather_main',
            size='wind_speed',
            hover_data=['timestamp', 'weather_description', 'pressure'],
            title='💧 Luftfeuchtigkeit vs. Temperatur',
            labels={
                'temperature': 'Temperatur (°C)',
                'humidity': 'Luftfeuchtigkeit (%)',
                'weather_main': 'Wetter',
                'wind_speed': 'Windgeschwindigkeit (m/s)'
            },
            template='plotly_white',
            height=500,
            color_discrete_sequence=['#3498DB', '#E74C3C', '#F39C12', '#2ECC71', '#9B59B6']
        )
        
        return fig
    
    def create_wind_polar(self, df):
        """Wind-Richtung und -Geschwindigkeit"""
        wind_data = df[df['wind_speed'] > 0].copy()
        
        if len(wind_data) == 0:
            st.info("ℹ️ Keine Winddaten verfügbar")
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=wind_data['wind_speed'],
            theta=wind_data['wind_direction'],
            mode='markers',
            marker=dict(
                size=wind_data['wind_speed'] * 5,
                color=wind_data['temperature'],
                colorscale='RdYlBu_r',
                colorbar=dict(title="Temperatur (°C)"),
                opacity=0.8,
                line=dict(width=1, color='white')
            ),
            text=wind_data['timestamp'].dt.strftime('%d.%m %H:%M'),
            hovertemplate='<b>%{text}</b><br>Wind: %{r:.1f} m/s<br>Richtung: %{theta}°<extra></extra>'
        ))
        
        fig.update_layout(
            title='🧭 Wind-Richtung und -Geschwindigkeit',
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, wind_data['wind_speed'].max() * 1.2],
                    title="Geschwindigkeit (m/s)"
                ),
                angularaxis=dict(
                    direction='clockwise',
                    rotation=90,
                    tickmode='array',
                    tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
                    ticktext=['N', 'NO', 'O', 'SO', 'S', 'SW', 'W', 'NW']
                )
            ),
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def create_pressure_humidity_time(self, df):
        """Luftdruck und Luftfeuchtigkeit über Zeit"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('📊 Luftdruck (hPa)', '💧 Luftfeuchtigkeit (%)'),
            vertical_spacing=0.1
        )
        
        # Luftdruck
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['pressure'],
                mode='lines+markers',
                name='Luftdruck',
                line=dict(color='#9B59B6', width=2),
                marker=dict(size=3)
            ),
            row=1, col=1
        )
        
        # Luftfeuchtigkeit
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['humidity'],
                mode='lines+markers',
                name='Luftfeuchtigkeit',
                line=dict(color='#3498DB', width=2),
                marker=dict(size=3),
                fill='tonexty',
                fillcolor='rgba(52, 152, 219, 0.1)'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            template='plotly_white',
            showlegend=False,
            title_text="🌪️ Atmosphärische Bedingungen"
        )
        
        return fig
    
    def run_dashboard(self):
        """Hauptfunktion für das Dashboard"""
        # Header
        st.markdown('<h1 class="main-header">🌤️ Weather Analytics Dashboard</h1>', unsafe_allow_html=True)
        st.markdown("### Interaktive Wetteranalyse für Hamburg")
        
        # Load Data
        df = self.load_data()
        
        # Sidebar
        date_range = self.create_sidebar(df)
        
        if df is None:
            st.error("❌ Keine Daten verfügbar. Führe zuerst `python src/data_collector.py` aus.")
            if st.button("🚀 Erste Daten sammeln", type="primary"):
                with st.spinner("Sammle Wetterdaten..."):
                    success = self.collector.collect_and_save(include_forecast=True)
                    if success:
                        st.success("✅ Daten erfolgreich gesammelt!")
                        st.rerun()
            return
        
        # Filter data by date range
        if len(date_range) == 2:
            start_date, end_date = date_range
            df_filtered = df[
                (df['date'].dt.date >= start_date) & 
                (df['date'].dt.date <= end_date)
            ]
        else:
            df_filtered = df
        
        # Metrics Row
        self.create_metrics_row(df_filtered)
        
        st.markdown("---")
        
        # Charts Layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Temperatur Chart
            temp_fig = self.create_temperature_chart(df_filtered)
            st.plotly_chart(temp_fig, use_container_width=True)
        
        with col2:
            # Wetterarten Pie Chart
            weather_fig = self.create_weather_pie(df_filtered)
            st.plotly_chart(weather_fig, use_container_width=True)
        
        # Second Row
        col3, col4 = st.columns(2)
        
        with col3:
            # Humidity vs Temperature
            humidity_fig = self.create_humidity_scatter(df_filtered)
            st.plotly_chart(humidity_fig, use_container_width=True)
        
        with col4:
            # Wind Polar
            wind_fig = self.create_wind_polar(df_filtered)
            if wind_fig:
                st.plotly_chart(wind_fig, use_container_width=True)
        
        # Third Row - Full Width
        pressure_fig = self.create_pressure_humidity_time(df_filtered)
        st.plotly_chart(pressure_fig, use_container_width=True)
        
        # Data Table (expandable)
        with st.expander("📋 Rohdaten anzeigen"):
            st.dataframe(
                df_filtered.sort_values('timestamp', ascending=False),
                use_container_width=True,
                height=400
            )
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #7f8c8d; padding: 2rem 0;'>
            🌤️ Weather Analytics Dashboard | Powered by OpenWeatherMap API<br>
            📊 Daten werden alle paar Stunden automatisch aktualisiert
        </div>
        """, unsafe_allow_html=True)

# Streamlit App Entry Point
def main():
    dashboard = StreamlitWeatherDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()