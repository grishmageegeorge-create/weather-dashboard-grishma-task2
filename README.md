# 🌦️ Weather Intelligence Dashboard

A multi-city weather monitoring dashboard built with Python and Streamlit, 
powered by async HTTP requests for fast simultaneous data fetching.

## APIs Used
- **Open-Meteo Geocoding** — Converts city name to latitude/longitude
  → https://geocoding-api.open-meteo.com/v1/search
- **Open-Meteo Weather** — Fetches current weather + 7-day forecast
  → https://api.open-meteo.com/v1/forecast
- **REST Countries** — Fetches country flag, timezone, currency, population
  → https://restcountries.com/v3.1/name/{country}

## Libraries Used
- `streamlit` — Dashboard UI
- `httpx` — Async HTTP requests
- `asyncio` — Async flow handling for simultaneous API calls
- `plotly` — 7-day forecast chart with precipitation

## How to Run
1. Install libraries:
   pip install streamlit httpx plotly
2. Run the app:
   python -m streamlit run weather_dashboard.py
3. Open browser at http://localhost:8501

## Features
- Async powered — all cities fetched simultaneously
- Search up to 5 cities at once
- Live temperature, wind speed and humidity
- Color coded temperatures
- Weather condition icons
- 7-day forecast chart with precipitation bars
- Country info — timezone, currency, population, region
- Dark theme UI with animations and hover effects

## Async Flow
All API calls use httpx AsyncClient with asyncio.gather() — 
meaning all 5 cities fetch data simultaneously instead of one by one.
This mirrors real-world engineering where performance matters!

## Challenges Faced
- API chaining — output of geocoding used as input for weather API
- Handling missing fields gracefully using .get() with defaults
- Implementing async flows using httpx and asyncio.gather()
- Custom dark theme CSS injected into Streamlit
- Windows encoding issues fixed using utf-8