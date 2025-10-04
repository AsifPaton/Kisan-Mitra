# dashboard.py
import streamlit as st
import subprocess
import sys
import os

# --- USER AUTHENTICATION ---
USERS = {
    "farmer": "1234",
    "admin": "admin"
}

# --- LOGIN FUNCTION ---
def login():
    st.title("🌾 Farmer AI App - Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("✅ Login successful")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid Username or Password")

# --- RUN OTHER PY FILES ---
def run_script(script_name):
    if os.path.exists(script_name):
        st.info(f"Running {script_name} ...")
        # run streamlit python file
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", script_name])
    else:
        st.error(f"File {script_name} not found!")

# --- DASHBOARD PAGE ---
def dashboard():
    st.title("📊 Farmer AI Dashboard")
    st.write(f"Welcome, **{st.session_state['username']}** 👨‍🌾")

    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Choose Module", 
        ["Crop Prediction", "Pest Prediction", "Market Trends", 
         "Cost Allocation", "Guidelines", "Helpline", "Logout"])

    if choice == "Crop Prediction":
        run_script("crop_prediction.py")
    elif choice == "Pest Prediction":
        run_script("pest_prediction.py")
    elif choice == "Market Trends":
        run_script("market_trends.py")
    elif choice == "Cost Allocation":
        run_script("cost_allocation.py")
    elif choice == "Guidelines":
        run_script("guidelines.py")
    elif choice == "Helpline":
        run_script("helpline.py")
    elif choice == "Logout":
        st.session_state.clear()
        st.experimental_rerun()

# --- MAIN APP ---
if "logged_in" not in st.session_state:
    login()
else:
    dashboard()
