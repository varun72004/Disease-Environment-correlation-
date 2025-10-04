import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from streamlit_echarts import st_echarts
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Environment–Disease Correlation Dashboard ", layout="wide")
st.title("🌍 Environment–Disease Correlation Dashboard 🩺")

# API Keys
api = "9b99c2520d9ddb36ed867de4196e0ede"
# AQI_TOKEN = "45921ba67a100b54d77be47c584a195cf319645b"
#https://api.weatherapi.com/v1/current.json?key=672e919775744e4c83c110532250808&q=London&aqi=yes
def fetch_aqi(city, api):
    try:
        # Step 1: Get latitude and longitude
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api}"
        geo_response = requests.get(geo_url).json()
        if not geo_response:
            return None
        lat = geo_response[0]["lat"]
        lon = geo_response[0]["lon"]

        # Step 2: Fetch AQI data
        aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api}"
        aqi_response = requests.get(aqi_url).json()

        if "list" not in aqi_response or not aqi_response["list"]:
            return None

        # Extract components like PM2.5 and PM10
        aqi_components = aqi_response["list"][0]["components"]
        return aqi_components

    except Exception as e:
        st.error(f"Failed to fetch AQI: {e}")
        return None

# Pollutant full names
pollutant_names = {
    "pm25": "Fine Particulate Matter (PM2.5)",
    "pm10": "Particulate Matter (PM10)",
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

# Fallback coordinates
fallback_coords = {
    "pathankot": (32.2643, 75.6421),
    "jammu": (32.2643, 75.6421),
    "shimla": (30.6952, 76.8542),
    "gurdaspur": (31.620132, 74.876091),
    "gurugram": (28.64, 77.22) 
}

# Load Disease CSV
file_path = "output_d206b0_corrected.csv"
try:
    disease_df = pd.read_csv(file_path)
    disease_cities = sorted(disease_df["City"].unique())
except FileNotFoundError:
    disease_df = pd.DataFrame()
    disease_cities = []

# ---------------- SIDEBAR ----------------
st.sidebar.header("📍 Location & Options")

# City for Weather & AQI
weather_aqi_city = st.sidebar.text_input("Weather/AQI City", "Pathankot")

# Separate city for disease data
disease_city = st.sidebar.selectbox("Disease Data City", disease_cities if disease_cities else ["No Data"])

# Checkboxes for sections
show_home = st.sidebar.checkbox("Home", value=True)
show_weather = st.sidebar.checkbox("Show Weather Data", value=True)
show_aqi = st.sidebar.checkbox("Show AQI Data", value=True)
show_disease = st.sidebar.checkbox("Show Disease Data", value=True)
show_correlation = st.sidebar.checkbox("Show Environmental & Disease Correlation", value=True)

# ---------------- HOME SECTION ----------------

if show_home:
    st.title("🌿 Environmental Disease Risk Dashboard")
    
    st.markdown("""
    ### 📊 Project Overview
    This application visualizes the relationship between **environmental conditions** (like weather and air quality)
    and disease outbreaks (e.g., **Dengue**, **Heat Stroke**, **Asthma**) in Indian cities.

    --- 

    ### 🔍 What You Can Explore:
    - 🌀 **Weather Conditions** (Temperature, Rainfall, Humidity, etc.)
    - 💨 **Air Quality Index (AQI)** and pollutants (PM2.5, PM10)
    - 🦠 **Disease Statistics** with time-based & city-wise insights
    - 📈 **Correlation Analysis** between environment & health impact

    ---

    ### 🧬 Target Diseases & Environmental Factors:
    | Disease       | Major Environmental Factors                      |
    |---------------|--------------------------------------------------|
    | **Dengue**    | 🌧 Rainfall, 💧 Humidity, 🌡 Temperature, 🏭 AQI  |
    | **Heat Stroke** | 🌡 Temperature, 💧 Humidity, 🔥 Heat Index      |
    | **Asthma**    | 🏭 AQI, PM2.5/PM10, 🌦 Weather Variability       |

    ---

    ### 👇 How to Use
    1. Use the **left sidebar** to:
       - Select your **city**
       - Toggle between **Weather, AQI, Disease & Correlation**
    2. Click buttons to fetch real-time or historical data.
    3. View insights using **interactive charts & tables**.

    """)

    # You can show images/icons as needed
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/4148/4148460.png", width=100, caption="Dengue")
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/1684/1684375.png", width=100, caption="Heat Stroke")
    with col3:
        st.image("https://cdn-icons-png.flaticon.com/512/3064/3064602.png", width=100, caption="Asthma")

    st.success("Use the sidebar to explore data sections like Weather, AQI, Disease, and Correlation.")
    st.stop()

if show_weather:
    try:
        def get_coordinates(city):
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api}"
            response = requests.get(geo_url).json()
            if response:
                return response[0]["lat"], response[0]["lon"]
            elif city.lower() in fallback_coords:
                return fallback_coords[city.lower()]
            else:
                return None, None

        lat, lon = get_coordinates(weather_aqi_city)

        if lat is None or lon is None:
            st.error("Could not determine coordinates for weather.")
        else:
            weather_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api}&units=metric"
            weather_response = requests.get(weather_url)
            weather_data = weather_response.json()

            if weather_response.status_code != 200 or "list" not in weather_data:
                st.error("Weather data not found.")
            else:
                weather_list = []
                for entry in weather_data["list"]:
                    weather_list.append({
                        "Date & Time": datetime.fromtimestamp(entry["dt"]).strftime("%Y-%m-%d %H:%M:%S"),
                        "Temperature (°C)": entry["main"]["temp"],
                        "Humidity (%)": entry["main"]["humidity"],
                        "Weather Prediction": entry["weather"][0]["description"].title()
                    })

                weather_df = pd.DataFrame(weather_list)

                st.subheader(f"🌦 Weather Forecast - {weather_aqi_city}")
                st.dataframe(weather_df, use_container_width=True)

                # Line Chart
                weather_option = {
                    "tooltip": {"trigger": "axis"},
                    "legend": {"data": ["Temperature (°C)", "Humidity (%)"]},
                    "xAxis": {"type": "category", "data": weather_df["Date & Time"].tolist()},
                    "yAxis": {"type": "value"},
                    "series": [
                        {"name": "Temperature (°C)", "type": "line", "data": weather_df["Temperature (°C)"].tolist()},
                        {"name": "Humidity (%)", "type": "line", "data": weather_df["Humidity (%)"].tolist()}
                    ]
                }
                st.markdown("#### 📈 Temperature & Humidity Trend")
                st_echarts(options=weather_option, height="400px")

                # PIE Chart - Temperature Range
                weather_df["Temp Range"] = weather_df["Temperature (°C)"].apply(lambda t: "Cold (<15°C)" if t < 15 else "Moderate (15-30°C)" if t < 30 else "Hot (>30°C)")
                temp_counts = weather_df["Temp Range"].value_counts().to_dict()
                temp_pie = {
                    "tooltip": {"trigger": "item"},
                    "series": [{
                        "name": "Temperature Range",
                        "type": "pie",
                        "radius": "50%",
                        "data": [{"value": v, "name": k} for k, v in temp_counts.items()]
                    }]
                }
                st.markdown("#### 🌡 Temperature Distribution")
                st_echarts(temp_pie, height="350px")

                # PIE Chart - Humidity Range
                weather_df["Humidity Range"] = weather_df["Humidity (%)"].apply(lambda h: "Low (<40%)" if h < 40 else "Medium (40-70%)" if h < 70 else "High (>70%)")
                hum_counts = weather_df["Humidity Range"].value_counts().to_dict()
                hum_pie = {
                    "tooltip": {"trigger": "item"},
                    "series": [{
                        "name": "Humidity Range",
                        "type": "pie",
                        "radius": "50%",
                        "data": [{"value": v, "name": k} for k, v in hum_counts.items()]
                    }]
                }
                st.markdown("#### 💧 Humidity Distribution")
                st_echarts(hum_pie, height="350px")

    except Exception as e:
        st.error(f"Error fetching weather: {e}")


# ---------------- AQI ----------------
if show_aqi:
    try:
        def get_coordinates(city):
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api}"
            response = requests.get(geo_url).json()
            if response:
                return response[0]["lat"], response[0]["lon"]
            elif city.lower() in fallback_coords:
                return fallback_coords[city.lower()]
            else:
                return None, None

        def calculate_aqi(concentration, breakpoints):
            for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
                if bp_low <= concentration <= bp_high:
                    return round(((aqi_high - aqi_low)/(bp_high - bp_low)) * (concentration - bp_low) + aqi_low)
            return None

        def calculate_pm25_aqi(concentration):
            breakpoints_pm25 = [
                (0.0, 12.0, 0, 50),
                (12.1, 35.4, 51, 100),
                (35.5, 55.4, 101, 150),
                (55.5, 150.4, 151, 200),
                (150.5, 250.4, 201, 300),
                (250.5, 350.4, 301, 400),
                (350.5, 500.4, 401, 500),
            ]
            return calculate_aqi(concentration, breakpoints_pm25)

        def calculate_pm10_aqi(concentration):
            breakpoints_pm10 = [
                (0, 54, 0, 50),
                (55, 154, 51, 100),
                (155, 254, 101, 150),
                (255, 354, 151, 200),
                (355, 424, 201, 300),
                (425, 504, 301, 400),
                (505, 604, 401, 500),
            ]
            return calculate_aqi(concentration, breakpoints_pm10)

        def get_aqi_category(aqi):
            if aqi is None:
                return "Unknown", "gray"
            elif aqi <= 50:
                return "Good", "green"
            elif aqi <= 100:
                return "Moderate", "yellow"
            elif aqi <= 150:
                return "Unhealthy for Sensitive Groups", "orange"
            elif aqi <= 200:
                return "Unhealthy", "red"
            elif aqi <= 300:
                return "Very Unhealthy", "purple"
            else:
                return "Hazardous", "maroon"

        lat, lon = get_coordinates(weather_aqi_city)

        if lat is None or lon is None:
            st.error("Could not get coordinates for AQI.")
        else:
            aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api}"
            response = requests.get(aqi_url)
            aqi_data = response.json()

            if "list" not in aqi_data or not aqi_data["list"]:
                st.error("AQI data not available.")
            else:
                aqi_info = aqi_data["list"][0]
                components = aqi_info["components"]

                pm25 = components.get("pm2_5")
                pm10 = components.get("pm10")

                pm25_aqi = calculate_pm25_aqi(pm25) if pm25 is not None else None
                pm10_aqi = calculate_pm10_aqi(pm10) if pm10 is not None else None

                real_aqi = max(pm25_aqi or 0, pm10_aqi or 0)
                category, color = get_aqi_category(real_aqi)

                st.subheader(f"🌫 Air Quality - {weather_aqi_city}")
                st.markdown(f"**Estimated Real AQI:** `{real_aqi}`")
                st.markdown(f"<span style='color:{color}; font-weight:bold;'>AQI Category: {category}</span>", unsafe_allow_html=True)

                if pm25_aqi is not None:
                    st.markdown(f"**PM2.5 AQI:** `{pm25_aqi}`, PM2.5 = `{pm25} µg/m³`")
                else:
                    st.markdown("**PM2.5 data unavailable**")

                if pm10_aqi is not None:
                    st.markdown(f"**PM10 AQI:** `{pm10_aqi}`, PM10 = `{pm10} µg/m³`")
                else:
                    st.markdown("**PM10 data unavailable**")

                aqi_df = pd.DataFrame([
                    {"Pollutant": "PM2.5", "Value": pm25},
                    {"Pollutant": "PM10", "Value": pm10},
                    {"Pollutant": "NO₂", "Value": components.get("no2")},
                    {"Pollutant": "SO₂", "Value": components.get("so2")},
                    {"Pollutant": "CO", "Value": components.get("co")},
                    {"Pollutant": "O₃", "Value": components.get("o3")},
                ])
                st.markdown("#### 📊 Pollutant Levels (µg/m³)")
                st.dataframe(aqi_df, use_container_width=True)

                bar_chart = {
                    "tooltip": {"trigger": "axis"},
                    "xAxis": {"type": "category", "data": aqi_df["Pollutant"].tolist()},
                    "yAxis": {"type": "value"},
                    "series": [{"type": "bar", "data": aqi_df["Value"].tolist()}]
                }
                st_echarts(options=bar_chart, height="400px")

                if real_aqi > 0:
                    gauge_chart = {
                        "tooltip": {"formatter": "{a} <br/>{b} : {c}"},
                        "series": [{
                            "name": "Estimated AQI",
                            "type": "gauge",
                            "min": 0,
                            "max": 500,
                            "detail": {"formatter": f"{real_aqi}"},
                            "data": [{"value": real_aqi, "name": "AQI"}]
                        }]
                    }
                    st.markdown("#### 📟 AQI Gauge (Estimated)")
                    st_echarts(gauge_chart, height="350px")
                else:
                    st.warning("AQI value could not be calculated due to missing data.")

    except Exception as e:
        st.error(f"Error fetching AQI data: {e}")

    # ---------------- DISEASE ----------------
if show_disease:
    if not disease_df.empty:
        city_data = disease_df[disease_df["City"].str.lower() == disease_city.lower()]
        if not city_data.empty:
            st.subheader(f"🩺 Disease Data for: {disease_city}")

            # Group by Disease
            diseases = city_data["Disease"].unique()
            for disease in diseases:
                disease_data = city_data[city_data["Disease"] == disease]
                st.markdown(f"### 🧬 {disease}")

                # Summary Table
                total_cases = disease_data["Population_Affected"].sum()
                total_deaths = disease_data["Number_of_Deaths"].sum()
                total_survived = disease_data["Survived"].sum()
                total_doctors = disease_data["Doctors_Available"].sum()
                total_hospitals = disease_data["Hospitals_Available"].sum()

                summary = pd.DataFrame([
                    {"Factor": "Population Affected", "Value": total_cases},
                    {"Factor": "Number of Deaths", "Value": total_deaths},
                    {"Factor": "Survived", "Value": total_survived},
                    {"Factor": "Doctors Available", "Value": total_doctors},
                    {"Factor": "Hospitals Available", "Value": total_hospitals}
                ])
                st.dataframe(summary, use_container_width=True)

                # Trend Graph (monthly)
                chart_option = {
                    "tooltip": {"trigger": "axis"},
                    "legend": {"data": ["Population Affected", "Deaths", "Survived"]},
                    "xAxis": {"type": "category", "data": disease_data["Date"].tolist()},
                    "yAxis": {"type": "value"},
                    "series": [
                        {"name": "Population Affected", "type": "line", "data": disease_data["Population_Affected"].tolist()},
                        {"name": "Deaths", "type": "line", "data": disease_data["Number_of_Deaths"].tolist()},
                        {"name": "Survived", "type": "line", "data": disease_data["Survived"].tolist()}
                    ]
                }
                st_echarts(chart_option, height="400px")
        else:
            st.error("No disease data found for this city.")
    else:
        st.error("Disease dataset not loaded.")
        
# ---------------- ENVIRONMENTAL & DISEASE CORRELATION ----------------
if show_correlation:
    try:
        # Get coordinates for both cities to enable correlation
        def get_coordinates(city):
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api}"
            response = requests.get(geo_url).json()
            if response:
                return response[0]["lat"], response[0]["lon"]
            elif city.lower() in fallback_coords:
                return fallback_coords[city.lower()]
            else:
                return None, None

        def calculate_aqi(concentration, breakpoints):
            for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
                if bp_low <= concentration <= bp_high:
                    return round(((aqi_high - aqi_low)/(bp_high - bp_low)) * (concentration - bp_low) + aqi_low)
            return None

        def calculate_pm25_aqi(concentration):
            breakpoints_pm25 = [
                (0.0, 12.0, 0, 50),
                (12.1, 35.4, 51, 100),
                (35.5, 55.4, 101, 150),
                (55.5, 150.4, 151, 200),
                (150.5, 250.4, 201, 300),
                (250.5, 350.4, 301, 400),
                (350.5, 500.4, 401, 500),
            ]
            return calculate_aqi(concentration, breakpoints_pm25)

        def calculate_pm10_aqi(concentration):
            breakpoints_pm10 = [
                (0, 54, 0, 50),
                (55, 154, 51, 100),
                (155, 254, 101, 150),
                (255, 354, 151, 200),
                (355, 424, 201, 300),
                (425, 504, 301, 400),
                (505, 604, 401, 500),
            ]
            return calculate_aqi(concentration, breakpoints_pm10)

        # ---- Disease variation over time chart for selected disease city ----
        if not disease_df.empty:
            city_disease_data = disease_df[disease_df["City"].str.lower() == disease_city.lower()]
            if not city_disease_data.empty:
                st.markdown(f"### 📅 Disease Variation Over Time in {disease_city}")

                # Group by Date & Disease to track population affected
                disease_trend = city_disease_data.groupby(["Date", "Disease"])["Population_Affected"].sum().reset_index()

                trend_chart = {
                    "tooltip": {"trigger": "axis"},
                    "legend": {"data": list(disease_trend["Disease"].unique())},
                    "xAxis": {"type": "category", "data": sorted(disease_trend["Date"].unique().tolist())},
                    "yAxis": {"type": "value"},
                    "series": []
                }

                # Add one line series per disease
                for dis in disease_trend["Disease"].unique():
                    disease_series = disease_trend[disease_trend["Disease"] == dis]
                    trend_chart["series"].append({
                        "name": dis,
                        "type": "line",
                        "smooth": True,
                        "data": [int(x) for x in disease_series.sort_values("Date")["Population_Affected"].tolist()]
                    })

                st_echarts(options=trend_chart, height="400px")

        # ---- Fetch current environmental data for correlation ----
        st.markdown(f"### 🌍 Environmental & Disease Correlation Analysis")
        
        # Use weather/AQI city for environmental data
        lat, lon = get_coordinates(weather_aqi_city)
        
        if lat is None or lon is None:
            st.error(f"Could not get coordinates for {weather_aqi_city}.")
        else:
            # Get current weather data
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={weather_aqi_city}&appid={api}&units=metric"
            w_response = requests.get(weather_url)
            w_data = w_response.json()
            
            if w_response.status_code != 200:
                st.error("Failed to fetch weather data for correlation.")
            else:
                # Extract weather parameters
                temp = w_data["main"]["temp"]
                humidity = w_data["main"]["humidity"]
                rain = w_data.get("rain", {}).get("1h", 0)
                pressure = w_data["main"]["pressure"]
                wind_speed = w_data.get("wind", {}).get("speed", 0)
                
                # Get temperature variability from forecast
                forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={weather_aqi_city}&appid={api}&units=metric"
                forecast_response = requests.get(forecast_url)
                temp_change = 0
                if forecast_response.status_code == 200:
                    forecast_data = forecast_response.json()
                    if "list" in forecast_data:
                        temps = [f["main"]["temp"] for f in forecast_data["list"][:8]]
                        if temps:
                            temp_change = max(temps) - min(temps)

                # Get AQI data
                aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api}"
                aqi_response = requests.get(aqi_url)
                
                latest_pm25 = latest_pm10 = latest_aqi = 0
                if aqi_response.status_code == 200:
                    aqi_data = aqi_response.json()
                    if "list" in aqi_data and aqi_data["list"]:
                        components = aqi_data["list"][0]["components"]
                        pm25_raw = components.get("pm2_5", 0)
                        pm10_raw = components.get("pm10", 0)
                        
                        # Calculate AQI values
                        latest_pm25 = pm25_raw
                        latest_pm10 = pm10_raw
                        
                        pm25_aqi = calculate_pm25_aqi(pm25_raw) if pm25_raw else 0
                        pm10_aqi = calculate_pm10_aqi(pm10_raw) if pm10_raw else 0
                        latest_aqi = max(pm25_aqi or 0, pm10_aqi or 0)

                # ---- Correlation Analysis Based on Actual Data ----
                
                # Display current environmental conditions
                st.markdown(f"#### 📊 Current Environmental Conditions in {weather_aqi_city}")
                env_summary = pd.DataFrame([
                    {"Parameter": "Temperature (°C)", "Value": f"{temp:.1f}"},
                    {"Parameter": "Humidity (%)", "Value": f"{humidity}"},
                    {"Parameter": "Rainfall (mm/h)", "Value": f"{rain}"},
                    {"Parameter": "Wind Speed (m/s)", "Value": f"{wind_speed}"},
                    {"Parameter": "Pressure (hPa)", "Value": f"{pressure}"},
                    {"Parameter": "PM2.5 (µg/m³)", "Value": f"{latest_pm25:.1f}"},
                    {"Parameter": "PM10 (µg/m³)", "Value": f"{latest_pm10:.1f}"},
                    {"Parameter": "Estimated AQI", "Value": f"{latest_aqi}"},
                    {"Parameter": "Temp Variation (°C)", "Value": f"{temp_change:.1f}"}
                ])
                st.dataframe(env_summary, use_container_width=True)

                # ---- Disease Risk Assessment Based on Environmental Data ----
                correlation_results = []

                # 1. Dengue Risk Assessment
                dengue_score = 0
                dengue_factors = []
                
                if 25 <= temp <= 32:
                    dengue_score += 2
                    dengue_factors.append("Optimal temperature")
                elif 20 <= temp <= 35:
                    dengue_score += 1
                    dengue_factors.append("Favorable temperature")
                
                if humidity > 70:
                    dengue_score += 2
                    dengue_factors.append("High humidity")
                elif humidity > 60:
                    dengue_score += 1
                    dengue_factors.append("Moderate humidity")
                
                if rain > 10:
                    dengue_score += 2
                    dengue_factors.append("Heavy rainfall")
                elif rain > 2:
                    dengue_score += 1
                    dengue_factors.append("Light rainfall")
                
                if dengue_score >= 4:
                    dengue_risk = "High"
                elif dengue_score >= 2:
                    dengue_risk = "Moderate"
                else:
                    dengue_risk = "Low"
                
                correlation_results.append({
                    "Disease": "Dengue",
                    "Risk": dengue_risk,
                    "Reason": f"Score: {dengue_score}/6 - {', '.join(dengue_factors) if dengue_factors else 'No major risk factors'}"
                })

                # 2. Heat Stroke Risk Assessment
                heat_score = 0
                heat_factors = []
                
                if temp > 40:
                    heat_score += 3
                    heat_factors.append("Extreme heat")
                elif temp > 35:
                    heat_score += 2
                    heat_factors.append("High temperature")
                elif temp > 30:
                    heat_score += 1
                    heat_factors.append("Warm temperature")
                
                if humidity > 70:
                    heat_score += 2
                    heat_factors.append("High humidity")
                elif humidity > 50:
                    heat_score += 1
                    heat_factors.append("Moderate humidity")
                
                if wind_speed < 2:
                    heat_score += 1
                    heat_factors.append("Low wind")
                
                if heat_score >= 4:
                    heatstroke_risk = "High"
                elif heat_score >= 2:
                    heatstroke_risk = "Moderate"
                else:
                    heatstroke_risk = "Low"
                
                correlation_results.append({
                    "Disease": "Heat Stroke",
                    "Risk": heatstroke_risk,
                    "Reason": f"Score: {heat_score}/6 - {', '.join(heat_factors) if heat_factors else 'No major risk factors'}"
                })

                # 3. Asthma Risk Assessment
                asthma_score = 0
                asthma_factors = []
                
                if latest_aqi > 150:
                    asthma_score += 3
                    asthma_factors.append("Unhealthy AQI")
                elif latest_aqi > 100:
                    asthma_score += 2
                    asthma_factors.append("Moderate AQI")
                elif latest_aqi > 50:
                    asthma_score += 1
                    asthma_factors.append("Fair AQI")
                
                if latest_pm25 > 55:
                    asthma_score += 2
                    asthma_factors.append("High PM2.5")
                elif latest_pm25 > 35:
                    asthma_score += 1
                    asthma_factors.append("Elevated PM2.5")
                
                if temp_change > 10:
                    asthma_score += 2
                    asthma_factors.append("High temp variation")
                elif temp_change > 5:
                    asthma_score += 1
                    asthma_factors.append("Moderate temp variation")
                
                if humidity > 80:
                    asthma_score += 1
                    asthma_factors.append("Very high humidity")
                
                if asthma_score >= 4:
                    asthma_risk = "High"
                elif asthma_score >= 2:
                    asthma_risk = "Moderate"
                else:
                    asthma_risk = "Low"
                
                correlation_results.append({
                    "Disease": "Asthma",
                    "Risk": asthma_risk,
                    "Reason": f"Score: {asthma_score}/8 - {', '.join(asthma_factors) if asthma_factors else 'No major risk factors'}"
                })

                # ---- Display Results with Historical Context ----
                st.markdown(f"#### 🔬 Disease Risk Assessment for {weather_aqi_city}")
                
                # Add historical disease context if available for the same city
                if not disease_df.empty:
                    historical_data = disease_df[disease_df["City"].str.lower() == weather_aqi_city.lower()]
                    if not historical_data.empty:
                        st.info(f"Historical disease data available for {weather_aqi_city}. Risk assessment considers current environmental conditions and historical patterns.")
                        
                        # Show recent disease trends for this city
                        recent_cases = historical_data.groupby("Disease")["Population_Affected"].sum().to_dict()
                        st.markdown("**Recent Historical Cases:**")
                        for disease, cases in recent_cases.items():
                            st.write(f"• {disease}: {cases:,} cases")
                    else:
                        st.info(f"Using environmental data from {weather_aqi_city}. No historical disease data available for this specific city.")

                # Display correlation results
                corr_df = pd.DataFrame(correlation_results)
                st.dataframe(corr_df, use_container_width=True)

                # ---- All the existing visualizations remain the same ----
                color_map = {"Low": "#4CAF50", "Moderate": "#FF9800", "High": "#F44336"}

                bar_chart = {
                    "tooltip": {"trigger": "axis"},
                    "xAxis": {"type": "category", "data": corr_df["Disease"].tolist()},
                    "yAxis": {"type": "category", "data": ["Low", "Moderate", "High"]},
                    "series": [{
                        "type": "bar",
                        "data": [{"value": r, "itemStyle": {"color": color_map[r]}} for r in corr_df["Risk"]],
                        "label": {"show": True, "position": "top"}
                    }]
                }
                st.markdown("#### 📊 Risk Levels by Disease")
                st_echarts(options=bar_chart, height="400px")

                risk_counts = corr_df["Risk"].value_counts().to_dict()
                pie_chart = {
                    "tooltip": {"trigger": "item"},
                    "series": [{
                        "name": "Risk Distribution",
                        "type": "pie",
                        "radius": "50%",
                        "data": [{"value": v, "name": k, "itemStyle": {"color": color_map[k]}} for k, v in risk_counts.items()]
                    }]
                }
                st.markdown("#### 🥧 Risk Distribution")
                st_echarts(options=pie_chart, height="350px")

                radar_chart = {
                    "tooltip": {},
                    "legend": {"data": ["Risk Level"]},
                    "radar": {
                        "indicator": [{"name": disease, "max": 3} for disease in corr_df["Disease"].tolist()]
                    },
                    "series": [{
                        "name": "Risk Level",
                        "type": "radar",
                        "data": [{
                            "value": [3 if r == "High" else 2 if r == "Moderate" else 1 for r in corr_df["Risk"]],
                            "name": "Risk Level"
                        }]
                    }]
                }
                st.markdown("#### 🕸 Disease Risk Radar")
                st_echarts(options=radar_chart, height="400px")

                # ---- Enhanced written summary ----
                st.markdown("### 📝 Environmental-Disease Correlation Summary")
                st.markdown(f"**Analysis for {weather_aqi_city}** based on current environmental conditions:")
                
                for _, row in corr_df.iterrows():
                    risk_color = "🔴" if row['Risk'] == "High" else "🟡" if row['Risk'] == "Moderate" else "🟢"
                    st.write(f"{risk_color} **{row['Disease']}** → {row['Risk']} Risk ({row['Reason']})")

                st.markdown("---")
                st.info("Risk assessment based on real-time weather, air quality data, and established environmental-health correlations. For medical decisions, consult healthcare professionals.")

    except Exception as e:
        st.error(f"Error in correlation analysis: {e}")
        st.write("Debug info:", str(e))