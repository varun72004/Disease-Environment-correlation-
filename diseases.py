import streamlit as st
import pandas as pd

st.header("Environmental Disease Data App")

file_path = "output_d206b0_corrected.csv"

df = pd.read_csv(file_path)


cities = sorted(df["City"].unique())
city = st.selectbox("Select City", cities)

if st.button("Show Disease Data"):

    
    city_data = df[df["City"].str.lower() == city.lower()]

    if not city_data.empty:
        
        total_cases = city_data["Population_Affected"].sum()
        total_deaths = city_data["Number_of_Deaths"].sum()
        total_survived = city_data["Survived"].sum()
        total_doctors = city_data["Doctors_Available"].sum()
        total_hospitals = city_data["Hospitals_Available"].sum()

        
        st.subheader(f"Disease Data for: {city}")
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

        
        st.markdown("### Detailed Monthly Data")
        st.dataframe(city_data, use_container_width=True)

    else:
        st.error("No disease data found for this city.")
