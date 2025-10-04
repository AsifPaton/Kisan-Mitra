# dashboard.py
import streamlit as st

# ---------------- STYLING ----------------
def add_styles():
    st.markdown("""
        <style>
        body {
            background-color: #f9f9f9;
        }
        .main {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            color: #2E7D32;
        }
        .stButton>button {
            background: #2E7D32;
            color: white;
            border-radius: 10px;
            height: 3em;
            width: 100%;
        }
        .stButton>button:hover {
            background: #1B5E20;
        }
        </style>
    """, unsafe_allow_html=True)

# ---------------- APP MODULES ----------------
def crop_prediction():
    st.subheader("🌾 Crop Prediction")
    soil = st.selectbox("Select Soil Type", ["Clay", "Loam", "Sandy"])
    season = st.selectbox("Season", ["Kharif", "Rabi", "Zaid"])
    land_size = st.number_input("Land Size (acres)", 1.0, 1000.0)
    if st.button("Predict Crop"):
        st.success(f"✅ Best crop for {soil} soil in {season} season is: **Wheat**")

def pest_prediction():
    st.subheader("🐛 Pest Prediction")
    crop = st.selectbox("Crop", ["Wheat", "Rice", "Maize", "Cotton"])
    if st.button("Predict Pests"):
        st.warning(f"⚠️ Likely pests for {crop}: Aphids, Stem Borers")

def market_trends():
    st.subheader("📈 Market Trends")
    crop = st.selectbox("Select Crop", ["Wheat", "Rice", "Cotton"])
    if st.button("Get Market Price"):
        st.info(f"💰 Current average price of {crop}: ₹2500 per quintal")

def cost_allocation():
    st.subheader("💵 Cost Allocation")
    crop = st.selectbox("Select Crop", ["Wheat", "Rice", "Maize"])
    land_size = st.number_input("Land Size (acres)", 1.0, 1000.0)
    if st.button("Calculate Cost"):
        st.success(f"✅ Estimated cultivation cost for {crop} on {land_size} acres = ₹{land_size*5000}")

def guidelines():
    st.subheader("📘 Guidelines & Help")
    st.write("👉 Use high-yield seeds\n👉 Rotate crops for better soil health\n👉 Use drip irrigation to save water")

def helpline():
    st.subheader("📞 Helpline")
    st.write("Call us at: **1800-123-456**")
    st.write("Email: support@farmerai.com")

# ---------------- DASHBOARD ----------------
def dashboard():
    st.title("📊 Farmer AI Dashboard")

    menu = ["Crop Prediction", "Pest Prediction", "Market Trends", 
            "Cost Allocation", "Guidelines", "Helpline"]
    choice = st.sidebar.radio("📌 Choose Module", menu)

    if choice == "Crop Prediction":
        crop_prediction()
    elif choice == "Pest Prediction":
        pest_prediction()
    elif choice == "Market Trends":
        market_trends()
    elif choice == "Cost Allocation":
        cost_allocation()
    elif choice == "Guidelines":
        guidelines()
    elif choice == "Helpline":
        helpline()

# ---------------- MAIN ----------------
def main():
    add_styles()
    dashboard()

if __name__ == "__main__":
    main()
