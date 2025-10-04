import requests
import streamlit as st
import pandas as pd
from datetime import datetime

st.header("Weather App")
API_KEY = "9b99c2520d9ddb36ed867de4196e0ede"

city = st.text_input("Enter City name")

if st.button("Check Weather"):
    try:
        api_address = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(api_address)
        data = response.json()

        if response.status_code != 200 or "list" not in data:
            st.error("City not found or API error.")
        else:
            # Extract weather forecast data
            weather_list = []
            for entry in data["list"]:
                weather_list.append({
                    "Date & Time": datetime.fromtimestamp(entry["dt"]).strftime("%Y-%m-%d %H:%M:%S"),
                    "Temperature (°C)": entry["main"]["temp"],
                    "Feels Like (°C)": entry["main"]["feels_like"],
                    "Humidity (%)": entry["main"]["humidity"],
                    "Weather": entry["weather"][0]["description"],
                    "Wind Speed (m/s)": entry["wind"]["speed"]
                })

            df = pd.DataFrame(weather_list)

            # Show latest updated time from API
            latest_update = datetime.fromtimestamp(data["list"][0]["dt"]).strftime("%Y-%m-%d %H:%M:%S")
            st.subheader(f"Latest Updated Time: {latest_update}")

            # Display table
            st.dataframe(df)

    except Exception as e:
        st.error(f"Error: {e}")
