# Weather Intelligence Dashboard

A multi-city weather monitoring dashboard built with Python and Streamlit.

## APIs Used
- **Open-Meteo Geocoding** — Converts city name to latitude/longitude
  → https://geocoding-api.open-meteo.com/v1/search
- **Open-Meteo Weather** — Fetches current weather + 7-day forecast
  → https://api.open-meteo.com/v1/forecast
- **REST Countries** — Fetches country flag, timezone, currency, population
  → https://restcountries.com/v3.1/name/{country}

## Libraries Used
- `streamlit` — Dashboard UI
- `requests` — API calls
- `plotly` — 7-day forecast chart with precipitation

## How to Run
1. Install libraries:
   pip install streamlit requests plotly
2. Run the app:
   python -m streamlit run app.py
3. Open browser at http://localhost:8501

## Features
- Search up to 5 cities at once
- Live temperature, wind speed and humidity
- Color coded temperatures
- Weather condition icons
- 7-day forecast chart with precipitation
- Country info — timezone, currency, population, region
- Dark theme UI with animations

## Challenges Faced
- API chaining — output of geocoding used as input for weather API
- Handling missing fields gracefully using .get() with defaults
- Windows encoding issues fixed using utf-8
- Styling Streamlit with custom CSS for dark theme