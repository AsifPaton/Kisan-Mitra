import streamlit as st
import pandas as pd
import random

# -----------------------------
# Sample Data (Normally fetched from DB/APIs)
# -----------------------------
crop_base_cost = {
    "Wheat": {"seed": 500, "fertilizer": 800, "labor": 1200, "water": 300, "transport": 200},
    "Rice": {"seed": 700, "fertilizer": 1000, "labor": 1500, "water": 500, "transport": 300},
    "Maize": {"seed": 400, "fertilizer": 700, "labor": 1000, "water": 250, "transport": 150},
    "Cotton": {"seed": 600, "fertilizer": 900, "labor": 1300, "water": 400, "transport": 250},
    "Sugarcane": {"seed": 800, "fertilizer": 1200, "labor": 2000, "water": 700, "transport": 400},
}

historical_prices = {
    "Wheat": [2000, 2100, 1900, 2050, 2200],
    "Rice": [3000, 3100, 2800, 2950, 3200],
    "Maize": [1800, 1900, 1750, 1850, 2000],
    "Cotton": [3500, 3600, 3400, 3700, 3800],
    "Sugarcane": [4000, 4200, 3900, 4100, 4300],
}

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("FarmWise Crop Cost & Profit Calculator")

crop = st.selectbox("Select Crop", list(crop_base_cost.keys()))
land_area = st.number_input("Enter Land Area", min_value=0.1, step=0.1)
unit = st.selectbox("Select Unit", ["Acre", "Hectare"])
soil_type = st.selectbox("Soil Type", ["Sandy", "Loamy", "Clayey", "Alluvial"])
season = st.selectbox("Season", ["Rabi", "Kharif", "Zaid"])
location = st.text_input("Location (City/District)")

# -----------------------------
# Cost Calculation
# -----------------------------
def calculate_total_cost(crop, land_area, unit):
    # Convert land area to acres for calculation if needed
    if unit == "Hectare":
        land_area = land_area * 2.47105
    
    cost_data = crop_base_cost[crop]
    total_cost = (cost_data["seed"] + cost_data["fertilizer"] + cost_data["labor"] + 
                  cost_data["water"] + cost_data["transport"]) * land_area
    return total_cost

# -----------------------------
# AI-Based Price Prediction (Simple Randomized Trend Example)
# -----------------------------
def predict_price(crop):
    # Simple predictive logic: take last price + small random variation
    last_prices = historical_prices[crop]
    predicted_price = last_prices[-1] * (1 + random.uniform(-0.05, 0.1))
    return round(predicted_price, 2)

# -----------------------------
# Calculation & Output
# -----------------------------
if st.button("Calculate Profit"):
    total_cost = calculate_total_cost(crop, land_area, unit)
    predicted_price_per_unit = predict_price(crop)
    expected_revenue = predicted_price_per_unit * land_area
    profit = expected_revenue - total_cost
    
    st.success(f"Total Cost: ₹{total_cost:.2f}")
    st.success(f"Predicted Price per Unit: ₹{predicted_price_per_unit}")
    st.success(f"Expected Revenue: ₹{expected_revenue:.2f}")
    st.success(f"Expected Profit: ₹{profit:.2f}")
    
    if profit < 0:
        st.warning("Profit is negative! Consider reducing costs or changing crop.")
    else:
        st.info("Profit is positive! Crop choice seems profitable.")
