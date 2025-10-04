import requests
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Weather + AQI App", layout="wide")

st.title("🌦 Weather + 🌫 Air Quality (AQI) App")

# API Keys
WEATHER_API_KEY = "9b99c2520d9ddb36ed867de4196e0ede"
AQI_TOKEN = "45921ba67a100b54d77be47c584a195cf319645b"

# Full names for pollutants
pollutant_names = {
    "pm25": "Fine Particulate Matter (PM2.5, ≤ 2.5 µm)",
    "pm10": "Particulate Matter (PM10, ≤ 10 µm)",
    "o3": "Ozone (O₃)",
    "no2": "Nitrogen Dioxide (NO₂)",
    "so2": "Sulfur Dioxide (SO₂)",
    "co": "Carbon Monoxide (CO)",
    "t": "Temperature (°C)",
    "h": "Humidity (%)",
    "w": "Wind Speed (m/s)",
    "r": "Rainfall (mm)",
    "d": "Dew Point (°C)",
    "p": "Atmospheric Pressure (hPa)"
}

# Fallback coordinates for small cities
fallback_coords = {
    "pathankot": (32.2643, 75.6421),
}

# Sidebar menu
st.sidebar.subheader("📍 Location & Options")
city = st.sidebar.text_input("Enter City name", "Pathankot")

show_weather = st.sidebar.checkbox("Show Weather Data", value=True)
show_aqi = st.sidebar.checkbox("Show AQI Data", value=True)

if st.sidebar.button("Fetch Data"):
    
    # ---------------- WEATHER DATA ----------------
    if show_weather:
        try:
            weather_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric"
            weather_response = requests.get(weather_url)
            weather_data = weather_response.json()

            if weather_response.status_code != 200 or "list" not in weather_data:
                st.error("Weather data not found. Please check city name.")
            else:
                weather_list = []
                for entry in weather_data["list"]:
                    weather_list.append({
                        "Date & Time": datetime.fromtimestamp(entry["dt"]).strftime("%Y-%m-%d %H:%M:%S"),
                        "Temperature (°C)": entry["main"]["temp"],
                        "Feels Like (°C)": entry["main"]["feels_like"],
                        "Humidity (%)": entry["main"]["humidity"],
                        "Weather": entry["weather"][0]["description"],
                        "Wind Speed (m/s)": entry["wind"]["speed"]
                    })

                weather_df = pd.DataFrame(weather_list)
                latest_weather_update = datetime.fromtimestamp(weather_data["list"][0]["dt"]).strftime("%Y-%m-%d %H:%M:%S")

                st.subheader(f"🌦 Latest Weather Update: {latest_weather_update}")
                st.dataframe(weather_df, use_container_width=True)

        except Exception as e:
            st.error(f"Error fetching weather: {e}")

    # ---------------- AQI DATA ----------------
    if show_aqi:
        try:
            def fetch_aqi(city_name):
                aqi_url = f"https://api.waqi.info/feed/{city_name}/?token={AQI_TOKEN}"
                aqi_resp = requests.get(aqi_url).json()
                if aqi_resp.get("status") != "ok":
                    if city_name.lower() in fallback_coords:
                        lat, lon = fallback_coords[city_name.lower()]
                        aqi_url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={AQI_TOKEN}"
                        aqi_resp = requests.get(aqi_url).json()
                return aqi_resp

            aqi_data = fetch_aqi(city)

            if aqi_data.get("status") == "ok":
                city_name_aqi = aqi_data["data"]["city"]["name"]
                aqi_value = aqi_data["data"]["aqi"]
                dominant_pollutant = pollutant_names.get(aqi_data["data"].get("dominentpol", ""), "N/A")
                iaqi_data = aqi_data["data"].get("iaqi", {})

                aqi_list = []
                for k, v in iaqi_data.items():
                    aqi_list.append({
                        "Environmental Factor": pollutant_names.get(k, k.upper()),
                        "Value": v.get("v", "N/A")
                    })

                aqi_df = pd.DataFrame(aqi_list)

                st.subheader(f"🌫 Air Quality in: {city_name_aqi}")
                st.write(f"**Overall AQI:** {aqi_value}")
                st.write(f"**Dominant Pollutant:** {dominant_pollutant}")
                st.dataframe(aqi_df, use_container_width=True)

                time_info = aqi_data["data"].get("time", {})
                if "s" in time_info:
                    st.caption(f"Latest AQI Update: {time_info['s']} {time_info.get('tz', '')}")

            else:
                st.error("No AQI data found for this location.")

        except Exception as e:
            st.error(f"Error fetching AQI: {e}")
