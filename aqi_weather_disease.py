import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Weather + AQI + Disease Data", layout="wide")
st.title("🌦 Weather + 🌫 AQI + 🩺 Disease Data Dashboard")

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
    "jammu": (32.2643, 75.6421),
    "shimla": (30.6952, 76.8542),
    "gurdaspur": (31.620132, 74.876091),
    "gurugram": (28.64, 77.22)
    
}

# ---------------- SIDEBAR ----------------
st.sidebar.header("📍 Location & Options")

# Disease data CSV
file_path = "output_d206b0_corrected.csv"
try:
    disease_df = pd.read_csv(file_path)
    cities = sorted(disease_df["City"].unique())
except FileNotFoundError:
    disease_df = pd.DataFrame()
    cities = []

# Location input
city = st.sidebar.text_input("Enter City name", "Pathankot")

# Checkboxes for sections
show_weather = st.sidebar.checkbox("Show Weather Data", value=True)
show_aqi = st.sidebar.checkbox("Show AQI Data", value=True)
show_disease = st.sidebar.checkbox("Show Disease Data", value=True)

# Button
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

    # ---------------- DISEASE DATA ----------------
    if show_disease:
        if disease_df.empty:
            st.error("No disease dataset found.")
        else:
            city_data = disease_df[disease_df["City"].str.lower() == city.lower()]

            if not city_data.empty:
                total_cases = city_data["Population_Affected"].sum()
                total_deaths = city_data["Number_of_Deaths"].sum()
                total_survived = city_data["Survived"].sum()
                total_doctors = city_data["Doctors_Available"].sum()
                total_hospitals = city_data["Hospitals_Available"].sum()

                st.subheader(f"🩺 Disease Data for: {city}")
                st.write(f"**Total Population Affected:** {total_cases}")
                st.write(f"**Total Deaths:** {total_deaths}")
                st.write(f"**Total Survived:** {total_survived}")
                st.write(f"**Total Doctors Available:** {total_doctors}")
                st.write(f"**Total Hospitals Available:** {total_hospitals}")

                table_rows = [
                    {"Factor": "Population Affected", "Value": total_cases},
                    {"Factor": "Number of Deaths", "Value": total_deaths},
                    {"Factor": "Survived", "Value": total_survived},
                    {"Factor": "Doctors Available", "Value": total_doctors},
                    {"Factor": "Hospitals Available", "Value": total_hospitals}
                ]
                df_summary = pd.DataFrame(table_rows)
                st.dataframe(df_summary, use_container_width=True)

                st.markdown("### 📅 Detailed Monthly Disease Data")
                st.dataframe(city_data, use_container_width=True)

            else:
                st.error("No disease data found for this city.")
