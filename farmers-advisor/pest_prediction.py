import streamlit as st
import pandas as pd

# ----- Load full pest database -----
# You can expand this CSV with all Indian crops and pests
# For demo, we create a sample DataFrame
data = {
    "Crop": ["Wheat", "Wheat", "Rice", "Rice", "Tomato", "Tomato"],
    "Pest": ["Aphids", "Rust", "Brown Planthopper", "Rice Blast", "Leaf Miner", "Late Blight"],
    "Season": ["Rabi", "Rabi", "Kharif", "Kharif", "Kharif", "Rabi"],
    "TempMin": [15, 10, 25, 20, 20, 18],
    "TempMax": [25, 22, 32, 28, 30, 25],
    "HumidityMin": [50, 70, 70, 80, 60, 80],
    "HumidityMax": [80, 90, 90, 100, 90, 100],
    "SoilType": ["Loamy", "Loamy", "Clayey", "Clayey", "Sandy", "Sandy"],
    "Prevention": [
        "Use neem oil or ladybugs.",
        "Apply fungicides and rotate crops.",
        "Maintain water levels; use resistant varieties.",
        "Use fungicides; avoid dense planting.",
        "Use yellow sticky traps and neem oil.",
        "Remove infected leaves; use fungicides."
    ]
}

pest_df = pd.DataFrame(data)

# ----- Streamlit Interface -----
st.title("🌾 Pest Prediction System (Data-driven)")
st.write("Predict likely pests for your crops based on complete pest data and environmental conditions.")

# User Inputs
crop = st.selectbox("Select Crop", pest_df["Crop"].unique())
soil = st.selectbox("Select Soil Type", ["Sandy", "Loamy", "Clayey", "Silty"])
season = st.selectbox("Select Season", ["Kharif", "Rabi", "Zaid"])
temperature = st.number_input("Current Temperature (°C)", 0, 50, 25)
humidity = st.number_input("Current Humidity (%)", 0, 100, 70)
land_area = st.number_input("Land Area (in acres)", 0.1, 1000.0, 1.0)

# Prediction
if st.button("Predict Pests"):
    filtered = pest_df[
        (pest_df["Crop"] == crop) &
        (pest_df["Season"] == season) &
        (pest_df["SoilType"] == soil) &
        (pest_df["TempMin"] <= temperature) &
        (pest_df["TempMax"] >= temperature) &
        (pest_df["HumidityMin"] <= humidity) &
        (pest_df["HumidityMax"] >= humidity)
    ]

    if not filtered.empty:
        st.success(f"Likely pests for {crop}:")
        for idx, row in filtered.iterrows():
            st.write(f"**{row['Pest']}** ➤ Prevention: {row['Prevention']}")
    else:
        st.info("No major pests predicted for these conditions. Monitor regularly.")

# Footer
st.write("---")
st.write("Prediction based on full pest database for Indian crops. Expand the database for more accuracy.")
