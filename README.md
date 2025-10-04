🌍 Environment–Disease Correlation Dashboard 🩺

A Streamlit-based interactive dashboard that analyzes the relationship between environmental conditions (weather & air quality) and disease outbreaks (like Dengue, Heat Stroke, Asthma, and Respiratory Infections).

The app integrates real-time data from the OpenWeatherMap API
 with historical disease datasets to provide risk assessments, correlations, and visual insights.

🚀 Features

✅ Weather Forecasts

Real-time weather data (temperature, humidity, rainfall, wind, pressure).

Interactive charts for temperature & humidity trends.

✅ Comprehensive AQI (Air Quality Index)

Pollutant-wise AQI for PM2.5, PM10, O₃, NO₂, SO₂, CO.

Custom AQI calculation using EPA breakpoints.

Gauge charts, pollutant comparisons, and category-based insights.

✅ Disease Data Visualization

Historical disease cases across Indian cities.

Trends over time with deaths, recoveries, and healthcare resource availability.

✅ Environmental–Disease Correlation

AI-driven risk scoring for Dengue, Heat Stroke, Asthma, Respiratory Infections.

Interactive risk-level charts (bar, radar, pie).

Personalized health recommendations based on conditions.

🛠️ Installation
1. Clone the Repository
git clone https://github.com/varun72004/Disease-Environment-correlation-
cd env-disease-dashboard

2. Create & Activate Virtual Environment (Optional but Recommended)
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows


requirements.txt should include:

streamlit
pandas
requests
matplotlib
seaborn
numpy
streamlit-echarts

🔑 Setup API Key

The app requires an OpenWeatherMap API Key.

You can set it in either of the following ways:

Option 1: Streamlit Secrets

Create a file: .streamlit/secrets.toml

OPENWEATHER_API_KEY = "9b99c2520d9ddb36ed867de4196e0ede"

Option 2: Environment Variable
export OPENWEATHER_API_KEY="9b99c2520d9ddb36ed867de4196e0ede"   # Linux/Mac
setx OPENWEATHER_API_KEY "9b99c2520d9ddb36ed867de4196e0ede"     # Windows

▶️ Run the Application
streamlit run proj.py


📊 Data

Weather & AQI: Real-time data fetched from OpenWeatherMap.

Disease Data: CSV file (output_d206b0_corrected.csv) containing columns:

| City | Disease | Date | Population_Affected | Number_of_Deaths | Survived | Doctors_Available | Hospitals_Available |


⚠️ Disclaimer

This dashboard provides data-driven insights for research and awareness. It is not a medical diagnostic tool.
For health concerns, always consult qualified healthcare professionals.

👨‍💻 Author

Developed by Varun ✨

📧 Contact: your-varunsharma1234566@gmail.com

🔗 GitHub: your-varun72004
