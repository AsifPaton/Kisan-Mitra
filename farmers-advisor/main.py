# dashboard.py
import streamlit as st
import importlib

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

# ---------------- DASHBOARD ----------------
def dashboard():
    st.title("📊 Farmer AI Dashboard")

    menu = {
        "Crop Prediction": "crop_prediction",
        "Pest Prediction": "pest_prediction",
        "Market Trends": "market_trends",
        "Cost Allocation": "cost_allocation",
        "Guidelines": "guidelines",
        "Helpline": "helpline"
    }

    choice = st.sidebar.radio("📌 Choose Module", list(menu.keys()))

    module_name = menu[choice]

    try:
        module = importlib.import_module(module_name)
        if hasattr(module, "app"):   # each file should have app() function
            module.app()
        else:
            st.error(f"⚠️ The file {module_name}.py must define an `app()` function.")
    except Exception as e:
        st.error(f"❌ Error loading {module_name}: {e}")

# ---------------- MAIN ----------------
def main():
    add_styles()
    dashboard()

if __name__ == "__main__":
    main()
