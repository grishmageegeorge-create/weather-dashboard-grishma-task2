import streamlit as st
import httpx
import asyncio
import plotly.graph_objects as go
import time

# ─────────────────────────────
# PAGE CONFIG
# ─────────────────────────────
st.set_page_config(
    page_title="Weather Intelligence Dashboard",
    page_icon="🌦️",
    layout="wide"
)

# ─────────────────────────────
# CUSTOM CSS
# ─────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        min-height: 100vh;
    }

    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 2rem; }

    .main-title {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00c6ff, #0072ff, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }

    .main-subtitle {
        color: rgba(255,255,255,0.5);
        font-size: 1.1rem;
        margin-top: 5px;
    }

    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.08) !important;
        color: black !important;
        border: 1.5px solid rgba(0,198,255,0.4) !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        font-size: 1rem !important;
        caret-color: white !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: rgba(255,255,255,0.35) !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00c6ff !important;
        box-shadow: 0 0 0 3px rgba(0,198,255,0.15) !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #00c6ff, #0072ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 14px 30px !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        width: 100% !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0,114,255,0.4) !important;
    }

    .city-header {
        background: linear-gradient(135deg, rgba(0,198,255,0.12), rgba(168,85,247,0.08));
        border: 1px solid rgba(0,198,255,0.25);
        border-radius: 20px;
        padding: 20px 25px;
        margin: 20px 0 15px 0;
        animation: fadeInDown 0.5s ease;
    }

    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-15px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(15px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .city-name {
        font-size: 1.8rem;
        font-weight: 800;
        color: white;
        margin: 0;
    }

    .condition-badge {
        background: rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.85rem;
        color: rgba(255,255,255,0.8);
        display: inline-block;
        margin-left: 10px;
    }

    .metric-card {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 18px;
        padding: 22px;
        text-align: center;
        animation: fadeInUp 0.6s ease;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        background: rgba(255,255,255,0.1);
    }
    .metric-emoji { font-size: 2rem; }
    .metric-label {
        color: rgba(255,255,255,0.5);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 6px 0;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
    }

    .country-bar {
        background: rgba(255,255,255,0.04);
        border-left: 3px solid #a855f7;
        border-radius: 10px;
        padding: 12px 20px;
        color: rgba(255,255,255,0.75);
        font-size: 0.9rem;
        margin: 12px 0;
        animation: fadeInUp 0.7s ease;
    }

    .custom-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0,198,255,0.3), transparent);
        margin: 25px 0;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────
# ASYNC HELPER FUNCTIONS
# ─────────────────────────────

async def fetch_coordinates(client, city):
    """Geocoding API — converts city name to lat/lon"""
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        r = await client.get(url, timeout=10)
        data = r.json()
        if "results" not in data:
            return city, None
        res = data["results"][0]
        return city, {
            "city": res["name"],
            "country": res.get("country", ""),
            "lat": res["latitude"],
            "lon": res["longitude"]
        }
    except:
        return city, None


async def fetch_weather(client, lat, lon):
    """Weather API — fetches current weather + 7 day forecast"""
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,windspeed_10m,relativehumidity_2m,weathercode"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode"
            f"&timezone=auto&forecast_days=7"
        )
        r = await client.get(url, timeout=10)
        return r.json()
    except:
        return {}


async def fetch_country(client, country_name):
    """REST Countries API — fetches country info"""
    try:
        url = f"https://restcountries.com/v3.1/name/{country_name}"
        r = await client.get(url, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()[0]
        currencies = data.get("currencies", {})
        currency = list(currencies.keys())[0] if currencies else "N/A"
        return {
            "flag": data.get("flag", "🌍"),
            "timezone": data.get("timezones", ["N/A"])[0],
            "currency": currency,
            "full_name": data.get("name", {}).get("official", country_name),
            "population": f"{data.get('population', 0):,}",
            "region": data.get("region", "N/A")
        }
    except:
        return None


async def fetch_all_cities(cities):
    """
    MAIN ASYNC FUNCTION — fetches ALL cities simultaneously!
    This is the async flow Mebin mentioned 😊
    """
    async with httpx.AsyncClient() as client:

        # Step 1 — Get coordinates for ALL cities at the same time
        coord_tasks = [fetch_coordinates(client, city) for city in cities]
        coord_results = await asyncio.gather(*coord_tasks)

        # Step 2 — Get weather + country for ALL cities at the same time
        weather_tasks = []
        country_tasks = []

        for city_name, coords in coord_results:
            if coords:
                weather_tasks.append(fetch_weather(client, coords["lat"], coords["lon"]))
                country_tasks.append(fetch_country(client, coords["country"]))
            else:
                weather_tasks.append(asyncio.sleep(0))
                country_tasks.append(asyncio.sleep(0))

        weather_results = await asyncio.gather(*weather_tasks)
        country_results = await asyncio.gather(*country_tasks)

        return coord_results, weather_results, country_results


# ─────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────
def get_weather_icon(code):
    if code == 0:            return "☀️", "Clear Sky"
    elif code in [1, 2]:     return "⛅", "Partly Cloudy"
    elif code == 3:          return "☁️", "Overcast"
    elif code in [45, 48]:   return "🌫️", "Foggy"
    elif code in [51,53,55]: return "🌦️", "Drizzle"
    elif code in [61,63,65]: return "🌧️", "Rainy"
    elif code in [71,73,75]: return "❄️", "Snowy"
    elif code in [80,81,82]: return "🌨️", "Showers"
    elif code in [95,96,99]: return "⛈️", "Thunderstorm"
    else:                    return "🌤️", "Variable"


def get_temp_color(temp):
    if temp <= 0:    return "#00bfff"
    elif temp <= 10: return "#4fc3f7"
    elif temp <= 20: return "#81c784"
    elif temp <= 30: return "#ffb74d"
    else:            return "#ef5350"


def render_city(coords, weather, country):
    """Renders one city's weather card on the dashboard"""
    current  = weather.get("current", {})
    daily    = weather.get("daily", {})

    temp     = current.get("temperature_2m", "N/A")
    wind     = current.get("windspeed_10m", "N/A")
    humidity = current.get("relativehumidity_2m", "N/A")
    code     = current.get("weathercode", 0)

    icon, condition = get_weather_icon(code)
    temp_color = get_temp_color(temp if isinstance(temp, (int, float)) else 20)
    flag = country["flag"] if country else "🌍"

    # City header
    st.markdown(f"""
    <div class='city-header'>
        <span class='city-name'>{flag} {coords['city']}, {coords['country']}</span>
        <span class='condition-badge'>{icon} {condition}</span>
    </div>
    """, unsafe_allow_html=True)

    # Metric cards
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-emoji'>🌡️</div>
            <div class='metric-label'>Temperature</div>
            <div class='metric-value' style='color:{temp_color};'>{temp}°C</div>
        </div>""", unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-emoji'>💨</div>
            <div class='metric-label'>Wind Speed</div>
            <div class='metric-value' style='color:#00c6ff;'>{wind} km/h</div>
        </div>""", unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-emoji'>💧</div>
            <div class='metric-label'>Humidity</div>
            <div class='metric-value' style='color:#81c784;'>{humidity}%</div>
        </div>""", unsafe_allow_html=True)

    # Country info
    if country:
        st.markdown(f"""
        <div class='country-bar'>
            🌍 <b>{country['full_name']}</b> &nbsp;·&nbsp;
            🕐 <b>Timezone:</b> {country['timezone']} &nbsp;·&nbsp;
            💰 <b>Currency:</b> {country['currency']} &nbsp;·&nbsp;
            👥 <b>Population:</b> {country['population']} &nbsp;·&nbsp;
            🗺️ <b>Region:</b> {country['region']}
        </div>
        """, unsafe_allow_html=True)

    # 7 day forecast chart
    if daily and "temperature_2m_max" in daily:
        dates         = daily["time"]
        max_temps     = daily["temperature_2m_max"]
        min_temps     = daily["temperature_2m_min"]
        precipitation = daily.get("precipitation_sum", [0]*7)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=dates + dates[::-1],
            y=max_temps + min_temps[::-1],
            fill="toself",
            fillcolor="rgba(0,198,255,0.08)",
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=False,
            hoverinfo="skip"
        ))

        fig.add_trace(go.Scatter(
            x=dates, y=max_temps,
            name="Max Temp",
            mode="lines+markers+text",
            line=dict(color="#ef5350", width=3),
            marker=dict(size=10, color="#ef5350",
                        line=dict(color="white", width=2)),
            text=[f"{t}°" for t in max_temps],
            textposition="top center",
            textfont=dict(color="white", size=11)
        ))

        fig.add_trace(go.Scatter(
            x=dates, y=min_temps,
            name="Min Temp",
            mode="lines+markers+text",
            line=dict(color="#00bfff", width=3),
            marker=dict(size=10, color="#00bfff",
                        line=dict(color="white", width=2)),
            text=[f"{t}°" for t in min_temps],
            textposition="bottom center",
            textfont=dict(color="white", size=11)
        ))

        fig.add_trace(go.Bar(
            x=dates, y=precipitation,
            name="Rain (mm)",
            marker=dict(
                color="rgba(129,199,132,0.4)",
                line=dict(color="rgba(129,199,132,0.8)", width=1)
            ),
            yaxis="y2"
        ))

        fig.update_layout(
            title=dict(
                text=f"📅 7-Day Forecast · {coords['city']}",
                font=dict(color="white", size=15),
                x=0
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.02)",
            font=dict(color="rgba(255,255,255,0.7)"),
            legend=dict(
                bgcolor="rgba(255,255,255,0.05)",
                bordercolor="rgba(255,255,255,0.1)",
                borderwidth=1,
                font=dict(color="white")
            ),
            xaxis=dict(
                gridcolor="rgba(255,255,255,0.06)",
                color="rgba(255,255,255,0.6)",
                tickformat="%b %d"
            ),
            yaxis=dict(
                title="Temperature (°C)",
                gridcolor="rgba(255,255,255,0.06)",
                color="rgba(255,255,255,0.6)"
            ),
            yaxis2=dict(
                title="Rain (mm)",
                overlaying="y",
                side="right",
                color="rgba(129,199,132,0.7)",
                showgrid=False
            ),
            hovermode="x unified",
            height=420,
            margin=dict(l=10, r=10, t=50, b=10)
        )

        st.plotly_chart(fig, width="stretch")

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)


# ─────────────────────────────
# STREAMLIT UI
# ─────────────────────────────
st.markdown("<p class='main-title'>🌦️ Weather Intelligence Dashboard</p>", unsafe_allow_html=True)
st.markdown("<p class='main-subtitle'>Real-time weather · 7-day forecasts · Country insights · Up to 5 cities · Async powered ⚡</p>", unsafe_allow_html=True)
st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])
with col1:
    cities_input = st.text_input(
        "cities",
        placeholder="🔍  Type cities e.g.  Kochi, Mumbai, Tokyo, Paris, New York",
        label_visibility="collapsed"
    )
with col2:
    search = st.button("Search 🚀")

if search:
    if not cities_input.strip():
        st.warning("⚠️ Please enter at least one city name!")
    else:
        cities = [c.strip() for c in cities_input.split(",")][:5]

        with st.spinner(f"⚡ Fetching weather for {len(cities)} cities simultaneously..."):
            coord_results, weather_results, country_results = asyncio.run(
                fetch_all_cities(cities)
            )

        for i, (city_name, coords) in enumerate(coord_results):
            if not coords:
                st.error(f"❌ '{city_name}' not found! Try a more specific name.")
                continue

            weather = weather_results[i]
            country = country_results[i]

            if not isinstance(weather, dict) or not weather:
                st.error(f"❌ Could not fetch weather for {city_name}")
                continue

            render_city(coords, weather, country)