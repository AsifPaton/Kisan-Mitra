# dashboard.py
import streamlit as st
import json
import os

USER_FILE = "users.json"

# ---------------- USER MANAGEMENT ----------------
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

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

# ---------------- LOGIN / REGISTER ----------------
def login(users):
    st.subheader("🔑 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("✅ Login successful!")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid credentials")

def register(users):
    st.subheader("📝 Register")
    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")
    if st.button("Register"):
        if new_user in users:
            st.error("⚠️ Username already exists!")
        elif new_user.strip() == "" or new_pass.strip() == "":
            st.error("⚠️ Please enter valid details!")
        else:
            users[new_user] = new_pass
            save_users(users)
            st.success("✅ Registration successful! Please login.")

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
    st.write(f"Welcome, **{st.session_state['username']}** 👨‍🌾")

    menu = ["Crop Prediction", "Pest Prediction", "Market Trends", 
            "Cost Allocation", "Guidelines", "Helpline", "Logout"]
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
    elif choice == "Logout":
        st.session_state.clear()
        st.experimental_rerun()

# ---------------- MAIN ----------------
def main():
    add_styles()
    st.title("🌱 Farmer AI App")

    users = load_users()

    if "logged_in" not in st.session_state:
        auth_choice = st.radio("Select Option", ["Login", "Register"])
        if auth_choice == "Login":
            login(users)
        else:
            register(users)
    else:
        dashboard()

if __name__ == "__main__":
    main()
