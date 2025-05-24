# 🌤️ Weather Analytics Dashboard

> **A comprehensive real-time weather analytics platform with interactive visualizations and automated data collection**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-red.svg)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.15+-green.svg)](https://plotly.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📊 Project Overview

This project is a full-stack weather analytics solution that automatically collects, processes, and visualizes meteorological data from Hamburg, Germany. Built with modern Python technologies, it features a responsive web dashboard, automated data pipeline, and comprehensive analytics capabilities.

### 🎯 Key Features

- **🌡️ Real-time Weather Monitoring** - Live temperature, humidity, pressure, and wind data
- **📈 Interactive Visualizations** - 5 dynamic charts with zoom, pan, and hover capabilities
- **🔄 Automated Data Collection** - Scheduled updates every 3 hours with error handling
- **📱 Responsive Web Dashboard** - Beautiful Streamlit interface optimized for all devices
- **💾 Data Export & Management** - CSV downloads and automated data cleanup
- **📊 Advanced Analytics** - Trend analysis, correlation plots, and statistical insights
- **🛡️ Error Handling & Logging** - Comprehensive logging and recovery mechanisms

## 🚀 Live Demo

<!-- Add screenshots here -->
### Dashboard Screenshots

**Main Dashboard View**
```
[Add screenshot of main dashboard here]
```

**Temperature Timeline**
```
[Add screenshot of temperature chart here]
```

**Weather Distribution**
```
[Add screenshot of weather pie chart here]
```

## 🛠️ Tech Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | Python 3.11+, Pandas, Requests |
| **Frontend** | Streamlit, Plotly, HTML/CSS |
| **Data Viz** | Plotly Express, Matplotlib, Seaborn |
| **APIs** | OpenWeatherMap API |
| **Automation** | Schedule, Logging |
| **Data Storage** | CSV, JSON |

## 📋 Prerequisites

- Python 3.11 or higher
- OpenWeatherMap API key (free tier available)
- Git (for cloning)

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/timmiflimmi/weather-analytics-dashboard.git
cd weather-analytics-dashboard
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Environment

1. Get your free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` with your API key:
   ```env
   WEATHER_API_KEY=your_actual_api_key_here
   CITY_NAME=Hamburg
   COUNTRY_CODE=DE
   ```

### 4. Collect Initial Data

```bash
python src/data_collector.py
```

### 5. Launch Dashboard

```bash
streamlit run streamlit_app.py
```

Visit `http://localhost:8501` to see your dashboard! 🎉

## 📁 Project Structure

```
weather-analytics-dashboard/
├── 📄 streamlit_app.py          # Main dashboard application
├── 🤖 auto_update.py            # Automated data collection
├── 📋 requirements.txt          # Python dependencies
├── 📖 README.md                 # Project documentation
├── 🔧 .env.example              # Environment template
├── 🚫 .gitignore               # Git ignore rules
├── 📂 src/
│   ├── 🌤️  data_collector.py   # Weather data collection
│   ├── 📊 visualizer.py        # Chart generation
│   └── 🧪 weather_test.py      # API testing
├── 📂 data/
│   ├── 📈 weather_data.csv     # Historical weather data
│   └── 📊 update_stats.json    # Update statistics
├── 📂 logs/
│   └── 📝 weather_auto_update.log  # Automation logs
└── 📂 notebooks/               # Jupyter notebooks (future)
```

## 🎮 Usage Examples

### Manual Data Collection
```bash
# Collect current + 5-day forecast data
python src/data_collector.py

# Test API connection
python src/weather_test.py
```

### Automated Updates
```bash
# Run once for testing
python auto_update.py once

# Check status and statistics
python auto_update.py status

# Run continuously (every 3 hours)
python auto_update.py

# Custom interval (every 2 hours)
python auto_update.py 2
```

### Data Visualization
```bash
# Generate static charts
python src/visualizer.py

# Launch interactive dashboard
streamlit run streamlit_app.py
```

## 📊 Dashboard Features

### Interactive Charts

1. **🌡️ Temperature Timeline**
   - Real-time temperature tracking
   - Feels-like temperature overlay
   - Daily min/max ranges

2. **☁️ Weather Distribution**
   - Pie chart of weather conditions
   - Percentage breakdown
   - Interactive filtering

3. **💧 Humidity vs Temperature**
   - Correlation analysis
   - Wind speed bubble sizing
   - Weather type color coding

4. **🧭 Wind Compass**
   - Polar plot visualization
   - Direction and speed mapping
   - Temperature color overlay

5. **📊 Atmospheric Conditions**
   - Pressure trends
   - Humidity patterns
   - Multi-axis visualization

### Dashboard Controls

- **🔄 Live Data Refresh** - Manual and automatic updates
- **📅 Date Range Filtering** - Custom time period selection
- **💾 Data Export** - CSV download functionality
- **📊 Real-time Metrics** - Current weather statistics
- **📱 Responsive Design** - Mobile and desktop optimized

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WEATHER_API_KEY` | OpenWeatherMap API key | Required |
| `CITY_NAME` | Target city for weather data | Hamburg |
| `COUNTRY_CODE` | ISO country code | DE |

### Customization Options

- **Update Frequency**: Modify `auto_update.py` intervals
- **Data Retention**: Adjust cleanup periods
- **Dashboard Layout**: Customize `streamlit_app.py` components
- **Chart Styling**: Modify Plotly themes and colors

## 📈 Performance & Scalability

- **API Efficiency**: Optimized calls to respect rate limits
- **Data Storage**: Efficient CSV handling with pandas
- **Memory Usage**: Streaming data processing
- **Caching**: Streamlit built-in caching for performance

## 🐛 Troubleshooting

### Common Issues

**API Key Issues**
```bash
# Verify API key setup
python src/weather_test.py
```

**Missing Dependencies**
```bash
# Reinstall requirements
pip install -r requirements.txt --upgrade
```

**Dashboard Not Loading**
```bash
# Check Streamlit installation
python -m streamlit run streamlit_app.py
```

### Log Files

Check logs for detailed error information:
- `logs/weather_auto_update.log` - Automation logs
- Streamlit console output - Dashboard errors

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenWeatherMap** - Weather data API
- **Streamlit** - Dashboard framework
- **Plotly** - Interactive visualizations
- **Python Community** - Amazing libraries and tools

## 📧 Contact

[@timmiflimmi](https://github.com/timmiflimmi)

Project Link: [https://github.com/timmiflimmi/weather-analytics-dashboard](https://github.com/timmiflimmi/weather-analytics-dashboard)

---

⭐ **Star this repository if you found it helpful!** ⭐