import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from streamlit_echarts import st_echarts
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from typing import Optional, Tuple, Dict, Any
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Environment–Disease Correlation Dashboard", layout="wide")
st.title("🌍 Environment–Disease Correlation Dashboard 🩺")

# ---------------- SECURE API KEY HANDLING ----------------
@st.cache_data(show_spinner=False)
def get_api_key():
    """Securely get API key from secrets or environment variables"""
    try:
        # Try Streamlit secrets first
        return st.secrets["OPENWEATHER_API_KEY"]
    except:
        # Try environment variable
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if api_key:
            return api_key
        else:
            # Fallback - you should replace this with your actual key
            return "9b99c2520d9ddb36ed867de4196e0ede"

api = get_api_key()

if not api or api == "your_api_key_here":
    st.error("⚠️ Please set your OpenWeatherMap API key in Streamlit secrets or environment variables")
    st.info("Add your API key to `.streamlit/secrets.toml` file or set OPENWEATHER_API_KEY environment variable")
    st.stop()

# ---------------- UTILITY FUNCTIONS ----------------
# Corrected coordinates for Indian cities
fallback_coords = {
    "pathankot": (32.2643, 75.6421),
    "jammu": (32.7266, 74.8570),        # Fixed: Correct Jammu coordinates
    "shimla": (31.1048, 77.1734),       # Fixed: More precise coordinates
    "gurdaspur": (32.0409, 75.4061),    # Fixed: More precise coordinates
    "gurugram": (28.4595, 77.0266)      # Fixed: More precise coordinates
}

@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes
def get_coordinates(city: str) -> Tuple[Optional[float], Optional[float]]:
    """Centralized coordinate fetching with proper error handling"""
    try:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api}"
        response = requests.get(geo_url, timeout=10)
        response.raise_for_status()
        
        geo_data = response.json()
        if geo_data:
            return geo_data[0]["lat"], geo_data[0]["lon"]
        elif city.lower() in fallback_coords:
            return fallback_coords[city.lower()]
        else:
            return None, None
    except requests.exceptions.RequestException as e:
        st.warning(f"API request failed for {city}: {e}")
        if city.lower() in fallback_coords:
            return fallback_coords[city.lower()]
        return None, None
    except (KeyError, IndexError, ValueError) as e:
        st.warning(f"Data parsing error for {city}: {e}")
        return None, None

# ---------------- COMPREHENSIVE AQI CALCULATION FUNCTIONS ----------------
def calculate_aqi(concentration: float, breakpoints: list) -> Optional[int]:
    """Calculate AQI based on concentration and breakpoints"""
    if concentration is None or concentration < 0:
        return None
    for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
        if bp_low <= concentration <= bp_high:
            return round(((aqi_high - aqi_low)/(bp_high - bp_low)) * (concentration - bp_low) + aqi_low)
    # If concentration exceeds all breakpoints, return max AQI
    return 500

def calculate_pm25_aqi(concentration: float) -> Optional[int]:
    """Calculate PM2.5 AQI using EPA breakpoints"""
    if concentration is None:
        return None
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

def calculate_pm10_aqi(concentration: float) -> Optional[int]:
    """Calculate PM10 AQI using EPA breakpoints"""
    if concentration is None:
        return None
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

def calculate_o3_aqi(concentration_ugm3: float) -> Optional[int]:
    """Calculate Ozone AQI (8-hour average) - concentration in µg/m³"""
    if concentration_ugm3 is None:
        return None
    
    # Convert from µg/m³ to ppb: For O3: 1 ppb = 1.96 µg/m³ at 25°C
    concentration_ppb = concentration_ugm3 / 1.96
    
    breakpoints_o3 = [
        (0, 54, 0, 50),
        (55, 70, 51, 100),
        (71, 85, 101, 150),
        (86, 105, 151, 200),
        (106, 200, 201, 300),
        (201, 404, 301, 400),
        (405, 604, 401, 500),
    ]
    return calculate_aqi(concentration_ppb, breakpoints_o3)

def calculate_no2_aqi(concentration: float) -> Optional[int]:
    """Calculate NO2 AQI (1-hour average) - concentration in µg/m³"""
    if concentration is None:
        return None
    
    # Convert from µg/m³ to ppb: NO2: 1 ppb = 1.88 µg/m³
    concentration_ppb = concentration / 1.88
    
    breakpoints_no2 = [
        (0, 53, 0, 50),
        (54, 100, 51, 100),
        (101, 360, 101, 150),
        (361, 649, 151, 200),
        (650, 1249, 201, 300),
        (1250, 1649, 301, 400),
        (1650, 2049, 401, 500),
    ]
    return calculate_aqi(concentration_ppb, breakpoints_no2)

def calculate_so2_aqi(concentration: float) -> Optional[int]:
    """Calculate SO2 AQI (1-hour average) - concentration in µg/m³"""
    if concentration is None:
        return None
    
    # Convert from µg/m³ to ppb: SO2: 1 ppb = 2.62 µg/m³
    concentration_ppb = concentration / 2.62
    
    breakpoints_so2 = [
        (0, 35, 0, 50),
        (36, 75, 51, 100),
        (76, 185, 101, 150),
        (186, 304, 151, 200),
        (305, 604, 201, 300),
        (605, 804, 301, 400),
        (805, 1004, 401, 500),
    ]
    return calculate_aqi(concentration_ppb, breakpoints_so2)

def calculate_co_aqi(concentration: float) -> Optional[int]:
    """Calculate CO AQI (8-hour average) - concentration in µg/m³"""
    if concentration is None:
        return None
    
    # Convert from µg/m³ to ppm: CO: 1 ppm = 1145 µg/m³
    concentration_ppm = concentration / 1145
    
    breakpoints_co = [
        (0.0, 4.4, 0, 50),
        (4.5, 9.4, 51, 100),
        (9.5, 12.4, 101, 150),
        (12.5, 15.4, 151, 200),
        (15.5, 30.4, 201, 300),
        (30.5, 40.4, 301, 400),
        (40.5, 50.4, 401, 500),
    ]
    return calculate_aqi(concentration_ppm, breakpoints_co)

def calculate_comprehensive_aqi(components: dict) -> dict:
    """Calculate comprehensive AQI considering all pollutants"""
    aqi_values = {}
    
    # Calculate AQI for each pollutant
    if 'pm2_5' in components and components['pm2_5'] is not None:
        aqi_values['PM2.5'] = calculate_pm25_aqi(components['pm2_5'])
    
    if 'pm10' in components and components['pm10'] is not None:
        aqi_values['PM10'] = calculate_pm10_aqi(components['pm10'])
    
    if 'o3' in components and components['o3'] is not None:
        aqi_values['O3'] = calculate_o3_aqi(components['o3'])
    
    if 'no2' in components and components['no2'] is not None:
        aqi_values['NO2'] = calculate_no2_aqi(components['no2'])
    
    if 'so2' in components and components['so2'] is not None:
        aqi_values['SO2'] = calculate_so2_aqi(components['so2'])
    
    if 'co' in components and components['co'] is not None:
        aqi_values['CO'] = calculate_co_aqi(components['co'])
    
    # Filter out None values
    valid_aqi_values = {k: v for k, v in aqi_values.items() if v is not None}
    
    if not valid_aqi_values:
        return {'overall_aqi': None, 'dominant_pollutant': None, 'individual_aqis': {}}
    
    # Overall AQI is the maximum of all pollutant AQIs
    overall_aqi = max(valid_aqi_values.values())
    dominant_pollutant = max(valid_aqi_values, key=valid_aqi_values.get)
    
    return {
        'overall_aqi': overall_aqi,
        'dominant_pollutant': dominant_pollutant,
        'individual_aqis': valid_aqi_values
    }

def get_comprehensive_aqi_data(lat: float, lon: float, api_key: str) -> dict:
    """Fetch and calculate comprehensive AQI data"""
    try:
        aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
        response = requests.get(aqi_url, timeout=10)
        response.raise_for_status()
        aqi_data = response.json()
        
        if "list" not in aqi_data or not aqi_data["list"]:
            return {'error': 'No AQI data available'}
        
        components = aqi_data["list"][0]["components"]
        aqi_result = calculate_comprehensive_aqi(components)
        
        return {
            'components': components,
            'aqi_result': aqi_result,
            'api_aqi': aqi_data["list"][0].get("main", {}).get("aqi", "N/A"),  # API's own AQI
            'timestamp': aqi_data["list"][0].get("dt", None)
        }
        
    except Exception as e:
        return {'error': f'Error fetching AQI data: {e}'}

def get_aqi_category(aqi: Optional[int]) -> Tuple[str, str]:
    """Get AQI category and color"""
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

def validate_disease_data(df: pd.DataFrame) -> bool:
    """Validate CSV data structure"""
    if df.empty:
        st.warning("Disease dataset is empty")
        return False
    
    required_columns = ["City", "Disease", "Date", "Population_Affected", 
                       "Number_of_Deaths", "Survived", "Doctors_Available", 
                       "Hospitals_Available"]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Missing required columns in CSV: {missing_columns}")
        return False
    
    return True

def create_risk_bar_chart(corr_df: pd.DataFrame, color_map: Dict[str, str]) -> Dict[str, Any]:
    """Create properly configured risk bar chart"""
    risk_values = [3 if r == "High" else 2 if r == "Moderate" else 1 for r in corr_df["Risk"]]
    risk_labels = corr_df["Risk"].tolist()
    
    # Create axis label mapping without lambda functions
    y_axis_labels = ["", "Low", "Moderate", "High"]
    
    return {
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": corr_df["Disease"].tolist()},
        "yAxis": {
            "type": "value", 
            "max": 3, 
            "min": 0,
            "interval": 1,
            "axisLabel": {
                "show": True
            }
        },
        "series": [{
            "name": "Risk Level",
            "type": "bar",
            "data": [{"value": val, "itemStyle": {"color": color_map[risk]}} 
                    for val, risk in zip(risk_values, risk_labels)],
            "label": {"show": True, "position": "top"}
        }]
    }

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

# ---------------- LOAD AND VALIDATE DATA ----------------
@st.cache_data(show_spinner=False)
def load_disease_data(file_path: str) -> Tuple[pd.DataFrame, list]:
    """Load and validate disease data"""
    try:
        disease_df = pd.read_csv(file_path)
        if validate_disease_data(disease_df):
            disease_cities = sorted(disease_df["City"].unique())
            return disease_df, disease_cities
        else:
            return pd.DataFrame(), []
    except FileNotFoundError:
        st.warning(f"Disease data file '{file_path}' not found. Some features may be limited.")
        return pd.DataFrame(), []
    except Exception as e:
        st.error(f"Error loading disease data: {e}")
        return pd.DataFrame(), []

file_path = "output_d206b0_corrected.csv"
disease_df, disease_cities = load_disease_data(file_path)

# ---------------- SIDEBAR ----------------
st.sidebar.header("📍 Location & Options")

# Add refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

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
    - 💨 **Comprehensive Air Quality Index (AQI)** with all major pollutants
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

    # Disease icons
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/4148/4148460.png", width=100, caption="Dengue")
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/1684/1684375.png", width=100, caption="Heat Stroke")
    with col3:
        st.image("https://cdn-icons-png.flaticon.com/512/3064/3064602.png", width=100, caption="Asthma")

    st.success("Use the sidebar to explore data sections like Weather, AQI, Disease, and Correlation.")
    st.stop()

# ---------------- WEATHER SECTION ----------------
if show_weather:
    try:
        lat, lon = get_coordinates(weather_aqi_city)

        if lat is None or lon is None:
            st.error(f"Could not determine coordinates for {weather_aqi_city}.")
        else:
            with st.spinner(f"Fetching weather data for {weather_aqi_city}..."):
                weather_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api}&units=metric"
                weather_response = requests.get(weather_url, timeout=10)
                weather_response.raise_for_status()
                weather_data = weather_response.json()

                if "list" not in weather_data:
                    st.error("Weather data not found.")
                else:
                    weather_list = []
                    for entry in weather_data["list"]:
                        weather_list.append({
                            "Date & Time": datetime.fromtimestamp(entry["dt"]).strftime("%Y-%m-%d %H:%M:%S"),
                            "Temperature (°C)": round(entry["main"]["temp"], 1),
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

                    # Temperature Distribution Pie Chart
                    weather_df["Temp Range"] = weather_df["Temperature (°C)"].apply(
                        lambda t: "Cold (<15°C)" if t < 15 else "Moderate (15-30°C)" if t < 30 else "Hot (>30°C)"
                    )
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

                    # Humidity Distribution Pie Chart
                    weather_df["Humidity Range"] = weather_df["Humidity (%)"].apply(
                        lambda h: "Low (<40%)" if h < 40 else "Medium (40-70%)" if h < 70 else "High (>70%)"
                    )
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

    except requests.exceptions.RequestException as e:
        st.error(f"Network error fetching weather: {e}")
    except Exception as e:
        st.error(f"Error fetching weather: {e}")

# ---------------- COMPREHENSIVE AQI SECTION ----------------
if show_aqi:
    try:
        lat, lon = get_coordinates(weather_aqi_city)

        if lat is None or lon is None:
            st.error(f"Could not get coordinates for AQI data for {weather_aqi_city}.")
        else:
            with st.spinner(f"Fetching comprehensive AQI data for {weather_aqi_city}..."):
                aqi_data = get_comprehensive_aqi_data(lat, lon, api)
                
                if 'error' in aqi_data:
                    st.error(aqi_data['error'])
                else:
                    components = aqi_data['components']
                    aqi_result = aqi_data['aqi_result']
                    api_aqi = aqi_data['api_aqi']
                    
                    st.subheader(f"🌫 Comprehensive Air Quality - {weather_aqi_city}")
                    
                    # Main AQI metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        calculated_aqi = aqi_result['overall_aqi']
                        st.metric("🧮 Calculated AQI", calculated_aqi or "N/A")
                    with col2:
                        # Convert API AQI (1-5 scale) to standard AQI scale for comparison
                        api_aqi_converted = "N/A"
                        if api_aqi != "N/A" and api_aqi is not None:
                            api_scale_map = {1: "0-50", 2: "51-100", 3: "101-150", 4: "151-200", 5: "201-300"}
                            api_aqi_converted = api_scale_map.get(api_aqi, str(api_aqi))
                        st.metric("🌐 API AQI Scale", f"{api_aqi} ({api_aqi_converted})")
                    with col3:
                        st.metric("🏆 Dominant Pollutant", aqi_result['dominant_pollutant'] or "N/A")
                    with col4:
                        if calculated_aqi:
                            category, color = get_aqi_category(calculated_aqi)
                            st.markdown(f"**Category:** <span style='color:{color}; font-weight:bold;'>{category}</span>", unsafe_allow_html=True)
                        else:
                            st.write("**Category:** Unknown")
                    
                    # Individual pollutant AQIs
                    if aqi_result['individual_aqis']:
                        st.markdown("#### 📊 Individual Pollutant AQIs")
                        pollutant_data = []
                        for pollutant, aqi_val in aqi_result['individual_aqis'].items():
                            # Get concentration from components
                            component_key = pollutant.lower().replace('.', '_')
                            concentration = components.get(component_key, 0)
                            category, _ = get_aqi_category(aqi_val)
                            
                            pollutant_data.append({
                                "Pollutant": pollutant,
                                "AQI": aqi_val,
                                "Category": category,
                                "Concentration (µg/m³)": f"{concentration:.1f}"
                            })
                        
                        pollutant_df = pd.DataFrame(pollutant_data)
                        st.dataframe(pollutant_df, use_container_width=True)
                        
                        # Individual pollutant bar chart
                        # Prepare data with colors for each AQI value
                        bar_data = []
                        for pollutant, aqi_val in aqi_result['individual_aqis'].items():
                            _, color = get_aqi_category(aqi_val)
                            bar_data.append({
                                "value": aqi_val,
                                "itemStyle": {"color": color}
                            })
                        
                        bar_chart = {
                            "tooltip": {"trigger": "axis", "formatter": "{b}: {c} AQI"},
                            "xAxis": {"type": "category", "data": list(aqi_result['individual_aqis'].keys())},
                            "yAxis": {"type": "value", "name": "AQI"},
                            "series": [{
                                "type": "bar",
                                "data": bar_data
                            }]
                        }
                        st.markdown("#### 📊 AQI by Pollutant")
                        st_echarts(options=bar_chart, height="400px")
                    
                    # All pollutant concentrations table
                    st.markdown("#### 🧪 All Pollutant Concentrations")
                    all_pollutants = []
                    pollutant_mapping = {
                        'pm2_5': 'PM2.5',
                        'pm10': 'PM10',
                        'o3': 'Ozone (O₃)',
                        'no2': 'Nitrogen Dioxide (NO₂)',
                        'so2': 'Sulfur Dioxide (SO₂)',
                        'co': 'Carbon Monoxide (CO)'
                    }
                    
                    for key, name in pollutant_mapping.items():
                        concentration = components.get(key, 0)
                        unit = "mg/m³" if key == 'co' else "µg/m³"
                        all_pollutants.append({
                            "Pollutant": name,
                            "Concentration": f"{concentration:.1f} {unit}",
                            "Raw Value": concentration
                        })
                    
                    all_pollutants_df = pd.DataFrame(all_pollutants)
                    st.dataframe(all_pollutants_df[["Pollutant", "Concentration"]], use_container_width=True)

                    # AQI Gauge
                    if calculated_aqi and calculated_aqi > 0:
                        gauge_chart = {
                            "tooltip": {"formatter": "{a} <br/>{b} : {c}"},
                            "series": [{
                                "name": "Calculated AQI",
                                "type": "gauge",
                                "min": 0,
                                "max": 500,
                                "detail": {"formatter": f"{calculated_aqi}"},
                                "data": [{"value": calculated_aqi, "name": "AQI"}],
                                "axisLine": {
                                    "lineStyle": {
                                        "color": [
                                            [0.1, "#4CAF50"],   # Good
                                            [0.2, "#FFEB3B"],   # Moderate
                                            [0.3, "#FF9800"],   # Unhealthy for Sensitive
                                            [0.4, "#F44336"],   # Unhealthy
                                            [0.6, "#9C27B0"],   # Very Unhealthy
                                            [1, "#8B0000"]      # Hazardous
                                        ]
                                    }
                                }
                            }]
                        }
                        st.markdown("#### 📟 AQI Gauge")
                        st_echarts(gauge_chart, height="350px")
                    else:
                        st.warning("AQI gauge not available - insufficient data for calculation.")

                    # AQI Comparison
                    if calculated_aqi and api_aqi != "N/A":
                        st.markdown("#### 🔍 AQI Comparison Analysis")
                        st.info(f"""
                        **Our Comprehensive Calculation**: {calculated_aqi} AQI (considers all pollutants)
                        
                        **API Simple Scale**: {api_aqi}/5 (simplified 1-5 rating)
                        
                        **Why they differ:**
                        - Our calculation uses EPA standard breakpoints for each pollutant
                        - API uses a simplified 1-5 scale 
                        - We consider the dominant pollutant (currently: {aqi_result['dominant_pollutant']})
                        - Real-time vs averaged measurements may vary
                        """)

    except requests.exceptions.RequestException as e:
        st.error(f"Network error fetching AQI data: {e}")
    except Exception as e:
        st.error(f"Error fetching comprehensive AQI data: {e}")
        if st.checkbox("Show AQI Debug Info"):
            st.exception(e)

# ---------------- DISEASE SECTION ----------------
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

                # Summary Table with safe aggregation
                total_cases = disease_data["Population_Affected"].sum()
                total_deaths = disease_data["Number_of_Deaths"].sum()
                total_survived = disease_data["Survived"].sum()
                total_doctors = disease_data["Doctors_Available"].sum()
                total_hospitals = disease_data["Hospitals_Available"].sum()

                summary = pd.DataFrame([
                    {"Factor": "Population Affected", "Value": f"{total_cases:,}"},
                    {"Factor": "Number of Deaths", "Value": f"{total_deaths:,}"},
                    {"Factor": "Survived", "Value": f"{total_survived:,}"},
                    {"Factor": "Doctors Available", "Value": f"{total_doctors:,}"},
                    {"Factor": "Hospitals Available", "Value": f"{total_hospitals:,}"}
                ])
                st.dataframe(summary, use_container_width=True)

                # Trend Graph with proper data handling
                if len(disease_data) > 1:
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
                    st.info("Insufficient data points for trend analysis.")
        else:
            st.error(f"No disease data found for {disease_city}.")
    else:
        st.error("Disease dataset not loaded. Please check the CSV file path and format.")

# ---------------- ENVIRONMENTAL & DISEASE CORRELATION ----------------
if show_correlation:
    try:
        # Disease variation over time chart for selected disease city
        if not disease_df.empty:
            city_disease_data = disease_df[disease_df["City"].str.lower() == disease_city.lower()]
            if not city_disease_data.empty:
                st.markdown(f"### 📅 Disease Variation Over Time in {disease_city}")

                # Group by Date & Disease to track population affected
                disease_trend = city_disease_data.groupby(["Date", "Disease"])["Population_Affected"].sum().reset_index()

                if not disease_trend.empty:
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
                            "data": disease_series.sort_values("Date")["Population_Affected"].tolist()
                        })

                    st_echarts(options=trend_chart, height="400px")

        # Fetch current environmental data for correlation
        st.markdown(f"### 🌍 Environmental & Disease Correlation Analysis")
        
        lat, lon = get_coordinates(weather_aqi_city)
        
        if lat is None or lon is None:
            st.error(f"Could not get coordinates for {weather_aqi_city}.")
        else:
            with st.spinner("Analyzing environmental conditions..."):
                # Get current weather data
                weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={weather_aqi_city}&appid={api}&units=metric"
                w_response = requests.get(weather_url, timeout=10)
                w_response.raise_for_status()
                w_data = w_response.json()
                
                # Extract weather parameters with safe defaults
                temp = w_data["main"]["temp"]
                humidity = w_data["main"]["humidity"]
                rain = w_data.get("rain", {}).get("1h", 0)
                pressure = w_data["main"]["pressure"]
                wind_speed = w_data.get("wind", {}).get("speed", 0)
                
                # Get temperature variability from forecast
                forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={weather_aqi_city}&appid={api}&units=metric"
                forecast_response = requests.get(forecast_url, timeout=10)
                temp_change = 0
                if forecast_response.status_code == 200:
                    forecast_data = forecast_response.json()
                    if "list" in forecast_data:
                        temps = [f["main"]["temp"] for f in forecast_data["list"][:8]]
                        if temps:
                            temp_change = max(temps) - min(temps)

                # Get comprehensive AQI data
                aqi_data = get_comprehensive_aqi_data(lat, lon, api)
                
                latest_pm25 = latest_pm10 = latest_aqi = 0
                dominant_pollutant = "None"
                
                if 'error' not in aqi_data:
                    components = aqi_data['components']
                    aqi_result = aqi_data['aqi_result']
                    
                    latest_pm25 = components.get('pm2_5', 0)
                    latest_pm10 = components.get('pm10', 0)
                    latest_aqi = aqi_result['overall_aqi'] or 0
                    dominant_pollutant = aqi_result['dominant_pollutant'] or "None"

                # Display current environmental conditions
                st.markdown(f"#### 📊 Current Environmental Conditions in {weather_aqi_city}")
                env_summary = pd.DataFrame([
                    {"Parameter": "Temperature (°C)", "Value": f"{temp:.1f}"},
                    {"Parameter": "Humidity (%)", "Value": f"{humidity}"},
                    {"Parameter": "Rainfall (mm/h)", "Value": f"{rain:.1f}"},
                    {"Parameter": "Wind Speed (m/s)", "Value": f"{wind_speed:.1f}"},
                    {"Parameter": "Pressure (hPa)", "Value": f"{pressure}"},
                    {"Parameter": "PM2.5 (µg/m³)", "Value": f"{latest_pm25:.1f}"},
                    {"Parameter": "PM10 (µg/m³)", "Value": f"{latest_pm10:.1f}"},
                    {"Parameter": "Comprehensive AQI", "Value": f"{latest_aqi}"},
                    {"Parameter": "Dominant Pollutant", "Value": dominant_pollutant},
                    {"Parameter": "Temp Variation (°C)", "Value": f"{temp_change:.1f}"}
                ])
                st.dataframe(env_summary, use_container_width=True)

                # Enhanced Disease Risk Assessment Based on Environmental Data
                correlation_results = []

                # 1. Dengue Risk Assessment (Enhanced)
                dengue_score = 0
                dengue_factors = []
                
                if 25 <= temp <= 32:
                    dengue_score += 3
                    dengue_factors.append("Optimal temperature for mosquito breeding")
                elif 20 <= temp <= 35:
                    dengue_score += 2
                    dengue_factors.append("Favorable temperature")
                elif temp > 35:
                    dengue_score += 1
                    dengue_factors.append("High temperature (reduced mosquito activity)")
                
                if humidity > 80:
                    dengue_score += 3
                    dengue_factors.append("Very high humidity (ideal for mosquitoes)")
                elif humidity > 70:
                    dengue_score += 2
                    dengue_factors.append("High humidity")
                elif humidity > 60:
                    dengue_score += 1
                    dengue_factors.append("Moderate humidity")
                
                if rain > 15:
                    dengue_score += 3
                    dengue_factors.append("Heavy rainfall (breeding sites)")
                elif rain > 5:
                    dengue_score += 2
                    dengue_factors.append("Moderate rainfall")
                elif rain > 1:
                    dengue_score += 1
                    dengue_factors.append("Light rainfall")
                
                if wind_speed < 1:
                    dengue_score += 1
                    dengue_factors.append("Low wind (stagnant conditions)")
                
                if latest_aqi > 100:
                    dengue_score += 1
                    dengue_factors.append("Poor air quality (weakened immunity)")
                
                if dengue_score >= 6:
                    dengue_risk = "High"
                elif dengue_score >= 3:
                    dengue_risk = "Moderate"
                else:
                    dengue_risk = "Low"
                
                correlation_results.append({
                    "Disease": "Dengue",
                    "Risk": dengue_risk,
                    "Score": dengue_score,
                    "Max_Score": 11,
                    "Reason": f"Score: {dengue_score}/11 - {', '.join(dengue_factors) if dengue_factors else 'No major risk factors'}"
                })

                # 2. Heat Stroke Risk Assessment (Enhanced)
                heat_score = 0
                heat_factors = []
                
                if temp > 42:
                    heat_score += 4
                    heat_factors.append("Extreme dangerous heat")
                elif temp > 38:
                    heat_score += 3
                    heat_factors.append("Very high temperature")
                elif temp > 35:
                    heat_score += 2
                    heat_factors.append("High temperature")
                elif temp > 32:
                    heat_score += 1
                    heat_factors.append("Warm temperature")
                
                if humidity > 80:
                    heat_score += 3
                    heat_factors.append("Very high humidity (reduced cooling)")
                elif humidity > 70:
                    heat_score += 2
                    heat_factors.append("High humidity")
                elif humidity > 50:
                    heat_score += 1
                    heat_factors.append("Moderate humidity")
                
                if wind_speed < 1:
                    heat_score += 2
                    heat_factors.append("Very low wind (no cooling)")
                elif wind_speed < 3:
                    heat_score += 1
                    heat_factors.append("Low wind")
                
                if latest_aqi > 150:
                    heat_score += 1
                    heat_factors.append("Poor air quality (additional stress)")
                
                # Heat index calculation (simplified)
                heat_index = temp + (0.5 * humidity/100 * temp)
                if heat_index > 40:
                    heat_score += 2
                    heat_factors.append(f"High heat index ({heat_index:.1f}°C)")
                
                if heat_score >= 7:
                    heatstroke_risk = "High"
                elif heat_score >= 3:
                    heatstroke_risk = "Moderate"
                else:
                    heatstroke_risk = "Low"
                
                correlation_results.append({
                    "Disease": "Heat Stroke",
                    "Risk": heatstroke_risk,
                    "Score": heat_score,
                    "Max_Score": 12,
                    "Reason": f"Score: {heat_score}/12 - {', '.join(heat_factors) if heat_factors else 'No major risk factors'}"
                })

                # 3. Asthma Risk Assessment (Enhanced with comprehensive AQI)
                asthma_score = 0
                asthma_factors = []
                
                if latest_aqi > 200:
                    asthma_score += 4
                    asthma_factors.append("Very unhealthy AQI")
                elif latest_aqi > 150:
                    asthma_score += 3
                    asthma_factors.append("Unhealthy AQI")
                elif latest_aqi > 100:
                    asthma_score += 2
                    asthma_factors.append("Unhealthy for sensitive groups")
                elif latest_aqi > 50:
                    asthma_score += 1
                    asthma_factors.append("Moderate AQI")
                
                if latest_pm25 > 75:
                    asthma_score += 3
                    asthma_factors.append("Very high PM2.5")
                elif latest_pm25 > 55:
                    asthma_score += 2
                    asthma_factors.append("High PM2.5")
                elif latest_pm25 > 35:
                    asthma_score += 1
                    asthma_factors.append("Elevated PM2.5")
                
                if latest_pm10 > 150:
                    asthma_score += 2
                    asthma_factors.append("Very high PM10")
                elif latest_pm10 > 100:
                    asthma_score += 1
                    asthma_factors.append("High PM10")
                
                if dominant_pollutant in ["O3", "NO2", "SO2"]:
                    asthma_score += 2
                    asthma_factors.append(f"Dominant pollutant is {dominant_pollutant}")
                
                if temp_change > 15:
                    asthma_score += 3
                    asthma_factors.append("Very high temperature variation")
                elif temp_change > 10:
                    asthma_score += 2
                    asthma_factors.append("High temperature variation")
                elif temp_change > 5:
                    asthma_score += 1
                    asthma_factors.append("Moderate temperature variation")
                
                if humidity > 85:
                    asthma_score += 2
                    asthma_factors.append("Very high humidity")
                elif humidity < 30:
                    asthma_score += 1
                    asthma_factors.append("Very low humidity (dry air)")
                
                if wind_speed > 10:
                    asthma_score += 1
                    asthma_factors.append("High wind (dust/allergens)")
                
                if asthma_score >= 8:
                    asthma_risk = "High"
                elif asthma_score >= 4:
                    asthma_risk = "Moderate"
                else:
                    asthma_risk = "Low"
                
                correlation_results.append({
                    "Disease": "Asthma",
                    "Risk": asthma_risk,
                    "Score": asthma_score,
                    "Max_Score": 18,
                    "Reason": f"Score: {asthma_score}/18 - {', '.join(asthma_factors) if asthma_factors else 'No major risk factors'}"
                })

                # 4. Respiratory Infections Risk Assessment (New)
                respiratory_score = 0
                respiratory_factors = []
                
                if latest_aqi > 150:
                    respiratory_score += 3
                    respiratory_factors.append("Poor air quality")
                elif latest_aqi > 100:
                    respiratory_score += 2
                    respiratory_factors.append("Moderate air quality")
                
                if temp < 15:
                    respiratory_score += 2
                    respiratory_factors.append("Cold temperature")
                elif temp > 35:
                    respiratory_score += 1
                    respiratory_factors.append("Hot temperature (stress)")
                
                if humidity > 80:
                    respiratory_score += 2
                    respiratory_factors.append("Very high humidity (mold/bacteria)")
                elif humidity < 30:
                    respiratory_score += 1
                    respiratory_factors.append("Very low humidity (dry airways)")
                
                if temp_change > 10:
                    respiratory_score += 2
                    respiratory_factors.append("High temperature variation")
                
                if wind_speed < 1:
                    respiratory_score += 1
                    respiratory_factors.append("Poor air circulation")
                
                if respiratory_score >= 5:
                    respiratory_risk = "High"
                elif respiratory_score >= 3:
                    respiratory_risk = "Moderate"
                else:
                    respiratory_risk = "Low"
                
                correlation_results.append({
                    "Disease": "Respiratory Infections",
                    "Risk": respiratory_risk,
                    "Score": respiratory_score,
                    "Max_Score": 10,
                    "Reason": f"Score: {respiratory_score}/10 - {', '.join(respiratory_factors) if respiratory_factors else 'No major risk factors'}"
                })

                # Display Results with Historical Context
                st.markdown(f"#### 🔬 Comprehensive Disease Risk Assessment for {weather_aqi_city}")
                
                # Add historical disease context if available for the same city
                if not disease_df.empty:
                    historical_data = disease_df[disease_df["City"].str.lower() == weather_aqi_city.lower()]
                    if not historical_data.empty:
                        st.info(f"📊 Historical disease data available for {weather_aqi_city}. Risk assessment considers current environmental conditions and historical patterns.")
                        
                        # Show recent disease trends for this city
                        recent_cases = historical_data.groupby("Disease")["Population_Affected"].sum().to_dict()
                        st.markdown("**📈 Recent Historical Cases:**")
                        for disease, cases in recent_cases.items():
                            st.write(f"• {disease}: {cases:,} cases")
                    else:
                        st.info(f"🌍 Using environmental data from {weather_aqi_city}. No historical disease data available for this specific city.")

                # Enhanced correlation results display
                corr_df = pd.DataFrame(correlation_results)
                
                # Add percentage scores
                corr_df["Risk_Percentage"] = (corr_df["Score"] / corr_df["Max_Score"] * 100).round(1)
                
                display_df = corr_df[["Disease", "Risk", "Risk_Percentage", "Reason"]].copy()
                display_df.columns = ["Disease", "Risk Level", "Risk Score (%)", "Analysis"]
                
                st.dataframe(display_df, use_container_width=True)

                # Enhanced Visualizations
                color_map = {"Low": "#4CAF50", "Moderate": "#FF9800", "High": "#F44336"}

                # Risk Level Bar Chart
                st.markdown("#### 📊 Disease Risk Levels")
                risk_chart = create_risk_bar_chart(corr_df, color_map)
                st_echarts(options=risk_chart, height="400px")

                # Risk Score Comparison
                st.markdown("#### 📈 Risk Score Comparison")
                # Prepare data with colors for each risk level
                score_data = []
                for score, risk in zip(corr_df["Risk_Percentage"], corr_df["Risk"]):
                    score_data.append({
                        "value": score,
                        "itemStyle": {"color": color_map[risk]}
                    })
                
                score_chart = {
                    "tooltip": {"trigger": "axis"},
                    "xAxis": {"type": "category", "data": corr_df["Disease"].tolist()},
                    "yAxis": {"type": "value", "name": "Risk Percentage (%)"},
                    "series": [{
                        "name": "Risk Score",
                        "type": "bar",
                        "data": score_data,
                        "label": {"show": True, "position": "top", "formatter": "{c}%"}
                    }]
                }
                st_echarts(options=score_chart, height="400px")

                # Risk Distribution Pie Chart
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
                st.markdown("#### 🥧 Overall Risk Distribution")
                st_echarts(options=pie_chart, height="350px")

                # Enhanced Radar Chart
                radar_chart = {
                    "tooltip": {},
                    "legend": {"data": ["Risk Percentage"]},
                    "radar": {
                        "indicator": [{"name": row["Disease"], "max": 100} for _, row in corr_df.iterrows()]
                    },
                    "series": [{
                        "name": "Risk Assessment",
                        "type": "radar",
                        "data": [{
                            "value": corr_df["Risk_Percentage"].tolist(),
                            "name": "Risk Percentage"
                        }]
                    }]
                }
                st.markdown("#### 🕸 Disease Risk Radar")
                st_echarts(options=radar_chart, height="400px")

                # Enhanced written summary
                st.markdown("### 📝 Detailed Environmental-Disease Correlation Summary")
                st.markdown(f"**🌍 Analysis for {weather_aqi_city}** based on current comprehensive environmental conditions:")
                
                for _, row in corr_df.iterrows():
                    risk_color = "🔴" if row['Risk'] == "High" else "🟡" if row['Risk'] == "Moderate" else "🟢"
                    percentage = row['Risk_Percentage']
                    st.write(f"{risk_color} **{row['Disease']}** → {row['Risk']} Risk ({percentage}% risk score)")
                    st.write(f"   • {row['Reason']}")
                    st.write("")

                # Enhanced health recommendations based on risk levels
                st.markdown("#### 🏥 Personalized Health Recommendations")
                high_risk_diseases = corr_df[corr_df["Risk"] == "High"]["Disease"].tolist()
                moderate_risk_diseases = corr_df[corr_df["Risk"] == "Moderate"]["Disease"].tolist()
                low_risk_diseases = corr_df[corr_df["Risk"] == "Low"]["Disease"].tolist()

                if high_risk_diseases:
                    st.error(f"🚨 **High Risk Alert**: {', '.join(high_risk_diseases)}")
                    st.markdown("**🛡️ Immediate Actions Required:**")
                    for disease in high_risk_diseases:
                        if disease == "Dengue":
                            st.markdown("""
                            **🦟 Dengue Prevention:**
                            • Remove all standing water from containers, flower pots, tires
                            • Use mosquito nets, especially during dawn and dusk
                            • Wear long-sleeved clothes and use repellents
                            • Seek immediate medical attention for fever, headache, muscle pain
                            """)
                        elif disease == "Heat Stroke":
                            st.markdown("""
                            **🌡️ Heat Stroke Prevention:**
                            • Stay indoors during 11 AM - 4 PM
                            • Drink water every 15-20 minutes, even if not thirsty
                            • Wear light-colored, loose, breathable clothing
                            • Use fans, AC, or cool showers to lower body temperature
                            • Avoid alcohol and caffeine
                            """)
                        elif disease == "Asthma":
                            st.markdown("""
                            **🫁 Asthma Management:**
                            • Limit outdoor activities, especially exercise
                            • Keep rescue inhalers easily accessible
                            • Use air purifiers and keep windows closed
                            • Consider wearing N95 masks when going outside
                            • Monitor symptoms closely and have action plan ready
                            """)
                        elif disease == "Respiratory Infections":
                            st.markdown("""
                            **🤧 Respiratory Health:**
                            • Boost immunity with proper nutrition and rest
                            • Maintain good hygiene - wash hands frequently
                            • Avoid crowded areas when possible
                            • Stay hydrated and consider humidifiers if air is dry
                            • Seek medical attention for persistent symptoms
                            """)

                if moderate_risk_diseases:
                    st.warning(f"⚠️ **Moderate Risk**: {', '.join(moderate_risk_diseases)}")
                    st.markdown("**⚡ Preventive Measures:**")
                    st.write("• Monitor symptoms and environmental conditions closely")
                    st.write("• Take standard preventive measures for these conditions")
                    st.write("• Stay informed about changing weather and air quality")
                    st.write("• Have emergency plans and medications ready")

                if low_risk_diseases:
                    st.success(f"✅ **Low Risk**: {', '.join(low_risk_diseases)}")
                    st.write("• Continue normal activities with basic precautions")
                    st.write("• Maintain healthy lifestyle and hygiene practices")

                # Environmental trend analysis
                st.markdown("#### 📈 Environmental Trend Impact")
                if temp_change > 10:
                    st.warning(f"🌡️ **High Temperature Variation**: {temp_change:.1f}°C change expected - increases respiratory stress")
                if latest_aqi > 150:
                    st.error(f"🏭 **Poor Air Quality**: AQI {latest_aqi} - major health concern for all groups")
                elif latest_aqi > 100:
                    st.warning(f"🌫️ **Moderate Air Quality**: AQI {latest_aqi} - sensitive groups should be cautious")
                if dominant_pollutant != "None":
                    st.info(f"💨 **Dominant Pollutant**: {dominant_pollutant} - primary air quality concern")

                st.markdown("---")
                st.info("💡 **Disclaimer**: This risk assessment is based on real-time environmental data and established scientific correlations. For medical decisions, always consult qualified healthcare professionals. Individual health conditions, age, and other factors significantly affect actual risk levels.")

    except requests.exceptions.RequestException as e:
        st.error(f"Network error during correlation analysis: {e}")
    except Exception as e:
        st.error(f"Error in correlation analysis: {e}")
        if st.checkbox("Show Debug Info"):
            st.exception(e)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 14px;'>
        🌍 Enhanced Environmental Disease Risk Dashboard | 
        Comprehensive AQI Calculation with All Major Pollutants | 
        Data from OpenWeatherMap API | 
        <a href='https://openweathermap.org/' target='_blank'>API Documentation</a>
    </div>
    """, 
    unsafe_allow_html=True
)