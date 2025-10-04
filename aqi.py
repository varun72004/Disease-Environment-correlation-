import requests
import streamlit as st
import pandas as pd

st.header("Air Quality Index (AQI) App")

API_TOKEN = "45921ba67a100b54d77be47c584a195cf319645b"

# Full names for pollutants & parameters
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

# Fallback coordinates for smaller cities like Pathankot
fallback_coords = {
    "pathankot": (32.2643, 75.6421),
    "gurdaspur": (31.620132, 74.876091) 
}

city = st.text_input("Enter City name ")

if st.button("Check AQI"):

    def fetch_aqi(city_name):
        """Try city name first; if not found, use coordinates."""
        url = f"https://api.waqi.info/feed/{city_name}/?token={API_TOKEN}"
        resp = requests.get(url).json()

        if resp.get("status") != "ok":
            if city_name.lower() in fallback_coords:
                lat, lon = fallback_coords[city_name.lower()]
                url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={API_TOKEN}"
                resp = requests.get(url).json()
        return resp

    # Get AQI data
    data = fetch_aqi(city)

    if data.get("status") == "ok":
        city_name = data["data"]["city"]["name"]
        aqi = data["data"]["aqi"]
        dominant_pollutant = pollutant_names.get(data["data"].get("dominentpol", ""), "N/A")
        iaqi_data = data["data"].get("iaqi", {})

        # Prepare table data
        table_rows = []
        for k, v in iaqi_data.items():
            table_rows.append({
                "Environmental Factor": pollutant_names.get(k, k.upper()),
                "Value": v.get("v", "N/A")
            })

        df = pd.DataFrame(table_rows)

        # Show title & main AQI
        st.subheader(f"AQI Data for: {city_name}")
        st.write(f"**Overall AQI:** {aqi}")
        st.write(f"**Dominant Pollutant:** {dominant_pollutant}")

        # Show table 
        st.dataframe(df, use_container_width=True)

        # Show last updated time
        time_info = data["data"].get("time", {})
        if "s" in time_info:
            st.markdown(f"**Latest Updated Time:** {time_info['s']} {time_info.get('tz', '')}")

    else:
        st.error("AQI data for this location is not avilable on website.")
