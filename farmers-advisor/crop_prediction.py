# farmwise_streamlit.py
# Single-file Streamlit app for crop prediction based on soil, area, season, and location-based weather.
# No external dependencies besides Streamlit.
# Run: streamlit run farmwise_streamlit.py

import streamlit as st
import json
import math
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from typing import List, Dict, Any

st.set_page_config(page_title="FarmWise - Crop Predictor", layout="wide")

# -------------------------
# Utilities
# -------------------------
def convert_to_hectare(value: float, unit: str) -> float:
    unit = unit.lower()
    mapping = {
        'hectare': 1.0,
        'acre': 0.404686,
        'square meter': 0.0001,
        'square_meter': 0.0001,
        'bigha': 0.133333,
        'guntha': 0.025,
        'ground': 0.0025
    }
    return float(value) * mapping.get(unit, 1.0)

def fetch_weather_open_meteo(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetch simple daily climate summary from Open-Meteo (no API key).
    Returns dictionary with avg_temp_C, annual_precip_mm (estimated), recent_precip_mm.
    """
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto",
            "past_days": 3  # get recent daily sums too
        }
        url = "https://api.open-meteo.com/v1/forecast?" + urlencode(params)
        req = Request(url, headers={"User-Agent":"FarmWise-App/1.0"})
        with urlopen(req, timeout=8) as resp:
            data = json.load(resp)
        daily = data.get("daily", {})
        tmax = daily.get("temperature_2m_max", [])
        tmin = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        # average the available days' temps as an estimate for current average temp
        temps = []
        for a, b in zip(tmax, tmin):
            try:
                temps.append((a + b) / 2.0)
            except:
                pass
        avg_temp = sum(temps) / len(temps) if temps else None
        recent_precip = sum(precip) if precip else 0.0
        # rough annualize: recent_precip is sum for last N days (past_days param) -> scale to 365
        # The API returns daily arrays; since we requested past_days=3, scale accordingly if present
        if precip:
            days = len(precip)
            annual_precip = (recent_precip / max(1, days)) * 365.0
        else:
            annual_precip = None
        return {
            "avg_temp_c": round(avg_temp, 1) if avg_temp is not None else None,
            "recent_precip_mm": float(recent_precip),
            "est_annual_precip_mm": float(round(annual_precip,1)) if annual_precip is not None else None,
            "raw": data
        }
    except Exception as e:
        return {"error": str(e)}

# -------------------------
# Hardcoded Indian crop database (requirements & base yields kg/ha)
# Each entry: name, soils (list), min_rain,max_rain in mm/yr (None=very flexible), min_temp,max_temp degC, seasons list, irrigation_need (bool), base_yield_kg_per_ha
# -------------------------
CROPS = [
    # Cereals
    {"name":"Rice", "soils":["Alluvial","Clay","Silty","Loamy"], "min_rain":800, "max_rain":4000, "min_temp":20, "max_temp":35, "seasons":["Kharif","Zaid"], "irrigation":True, "base_yield":4500},
    {"name":"Wheat", "soils":["Loamy","Alluvial","Chalky"], "min_rain":300, "max_rain":900, "min_temp":10, "max_temp":25, "seasons":["Rabi"], "irrigation":False, "base_yield":3000},
    {"name":"Maize", "soils":["Loamy","Silty","Alluvial","Red"], "min_rain":500, "max_rain":1500, "min_temp":18, "max_temp":32, "seasons":["Kharif","Rabi"], "irrigation":False, "base_yield":2500},
    {"name":"Sorghum (Jowar)", "soils":["Red","Black","Loamy"], "min_rain":250, "max_rain":800, "min_temp":20, "max_temp":35, "seasons":["Kharif","Rabi"], "irrigation":False, "base_yield":1200},
    {"name":"Pearl Millet (Bajra)", "soils":["Sandy","Red","Black"], "min_rain":200, "max_rain":500, "min_temp":25, "max_temp":40, "seasons":["Kharif"], "irrigation":False, "base_yield":800},
    {"name":"Finger Millet (Ragi)", "soils":["Red","Black","Laterite"], "min_rain":400, "max_rain":1200, "min_temp":15, "max_temp":30, "seasons":["Kharif","Rabi"], "irrigation":False, "base_yield":900},
    {"name":"Barley", "soils":["Loamy","Chalky"], "min_rain":200, "max_rain":600, "min_temp":10, "max_temp":22, "seasons":["Rabi"], "irrigation":False, "base_yield":2200},
    # Pulses
    {"name":"Chickpea (Gram)", "soils":["Loamy","Red","Alluvial"], "min_rain":300, "max_rain":800, "min_temp":10, "max_temp":30, "seasons":["Rabi"], "irrigation":False, "base_yield":900},
    {"name":"Pigeon Pea (Arhar/Tur)", "soils":["Red","Black","Loamy"], "min_rain":600, "max_rain":1200, "min_temp":20, "max_temp":35, "seasons":["Kharif"], "irrigation":False, "base_yield":700},
    {"name":"Green Gram (Moong)", "soils":["Sandy","Loamy"], "min_rain":300, "max_rain":800, "min_temp":20, "max_temp":35, "seasons":["Kharif","Rabi"], "irrigation":False, "base_yield":500},
    {"name":"Black Gram (Urad)", "soils":["Loamy","Alluvial"], "min_rain":300, "max_rain":1000, "min_temp":20, "max_temp":35, "seasons":["Kharif"], "irrigation":False, "base_yield":500},
    {"name":"Lentil (Masoor)", "soils":["Loamy","Alluvial"], "min_rain":300, "max_rain":800, "min_temp":10, "max_temp":25, "seasons":["Rabi"], "irrigation":False, "base_yield":800},
    # Oilseeds
    {"name":"Groundnut", "soils":["Sandy","Loamy"], "min_rain":500, "max_rain":1200, "min_temp":20, "max_temp":35, "seasons":["Kharif"], "irrigation":False, "base_yield":1500},
    {"name":"Soybean", "soils":["Loamy","Alluvial"], "min_rain":500, "max_rain":1200, "min_temp":18, "max_temp":30, "seasons":["Kharif"], "irrigation":False, "base_yield":900},
    {"name":"Mustard (Rapeseed)", "soils":["Loamy","Alluvial"], "min_rain":300, "max_rain":800, "min_temp":5, "max_temp":25, "seasons":["Rabi"], "irrigation":False, "base_yield":800},
    {"name":"Sesame (Til)", "soils":["Sandy","Red"], "min_rain":300, "max_rain":800, "min_temp":20, "max_temp":35, "seasons":["Kharif"], "irrigation":False, "base_yield":400},
    {"name":"Sunflower", "soils":["Loamy","Sandy"], "min_rain":400, "max_rain":900, "min_temp":20, "max_temp":30, "seasons":["Rabi","Kharif"], "irrigation":False, "base_yield":700},
    # Cash & Fiber
    {"name":"Cotton", "soils":["Sandy","Loamy","Black"], "min_rain":400, "max_rain":1200, "min_temp":20, "max_temp":35, "seasons":["Kharif"], "irrigation":False, "base_yield":1500},
    {"name":"Sugarcane", "soils":["Loamy","Alluvial","Clay"], "min_rain":1000, "max_rain":4000, "min_temp":20, "max_temp":35, "seasons":["Kharif","Rabi"], "irrigation":True, "base_yield":80000},
    {"name":"Jute", "soils":["Loamy","Alluvial"], "min_rain":1200, "max_rain":4000, "min_temp":20, "max_temp":35, "seasons":["Kharif"], "irrigation":False, "base_yield":2000},
    # Vegetables (selected major ones)
    {"name":"Potato", "soils":["Loamy","Alluvial"], "min_rain":400, "max_rain":1200, "min_temp":10, "max_temp":25, "seasons":["Rabi","Kharif"], "irrigation":True, "base_yield":25000},
    {"name":"Tomato", "soils":["Loamy","Sandy"], "min_rain":400, "max_rain":1200, "min_temp":15, "max_temp":32, "seasons":["Rabi","Kharif"], "irrigation":True, "base_yield":45000},
    {"name":"Onion", "soils":["Loamy","Alluvial"], "min_rain":300, "max_rain":900, "min_temp":10, "max_temp":30, "seasons":["Rabi","Kharif"], "irrigation":True, "base_yield":15000},
    {"name":"Okra (Bhindi)", "soils":["Loamy","Sandy"], "min_rain":400, "max_rain":1200, "min_temp":20, "max_temp":35, "seasons":["Kharif"], "irrigation":False, "base_yield":8000},
    {"name":"Brinjal (Eggplant)", "soils":["Loamy","Alluvial"], "min_rain":400, "max_rain":1200, "min_temp":18, "max_temp":32, "seasons":["Kharif","Rabi"], "irrigation":True, "base_yield":20000},
    {"name":"Cabbage", "soils":["Loamy"], "min_rain":500, "max_rain":1200, "min_temp":8, "max_temp":25, "seasons":["Rabi"], "irrigation":True, "base_yield":20000},
    {"name":"Cauliflower", "soils":["Loamy"], "min_rain":500, "max_rain":1200, "min_temp":8, "max_temp":25, "seasons":["Rabi"], "irrigation":True, "base_yield":20000},
    {"name":"Chilli", "soils":["Loamy","Red"], "min_rain":500, "max_rain":1200, "min_temp":18, "max_temp":35, "seasons":["Kharif","Rabi"], "irrigation":True, "base_yield":4000},
    # Fruits (major)
    {"name":"Mango", "soils":["Alluvial","Loamy","Red"], "min_rain":750, "max_rain":2000, "min_temp":20, "max_temp":40, "seasons":["Perennial"], "irrigation":False, "base_yield":10000},
    {"name":"Banana", "soils":["Loamy","Alluvial"], "min_rain":1200, "max_rain":4000, "min_temp":20, "max_temp":35, "seasons":["Perennial"], "irrigation":True, "base_yield":40000},
    {"name":"Citrus (Orange)", "soils":["Loamy","Red"], "min_rain":600, "max_rain":1500, "min_temp":12, "max_temp":30, "seasons":["Perennial"], "irrigation":True, "base_yield":15000},
    {"name":"Guava", "soils":["Loamy","Alluvial"], "min_rain":600, "max_rain":2000, "min_temp":18, "max_temp":35, "seasons":["Perennial"], "irrigation":True, "base_yield":12000},
    {"name":"Papaya", "soils":["Loamy","Alluvial"], "min_rain":1000, "max_rain":4000, "min_temp":20, "max_temp":35, "seasons":["Perennial"], "irrigation":True, "base_yield":30000},
    # Spices & others
    {"name":"Turmeric", "soils":["Loamy","Red"], "min_rain":1000, "max_rain":2500, "min_temp":20, "max_temp":35, "seasons":["Kharif"], "irrigation":True, "base_yield":2000},
    {"name":"Ginger", "soils":["Loamy"], "min_rain":1200, "max_rain":3000, "min_temp":20, "max_temp":35, "seasons":["Kharif"], "irrigation":True, "base_yield":7000},
    {"name":"Black Pepper", "soils":["Loamy","Laterite"], "min_rain":1500, "max_rain":4000, "min_temp":20, "max_temp":35, "seasons":["Perennial"], "irrigation":True, "base_yield":1500},
    {"name":"Cardamom", "soils":["Loamy","Laterite"], "min_rain":1500, "max_rain":4000, "min_temp":15, "max_temp":30, "seasons":["Perennial"], "irrigation":True, "base_yield":700},
    # Fallow / alternative cereals
    {"name":"Tobacco", "soils":["Loamy","Red"], "min_rain":600, "max_rain":1200, "min_temp":18, "max_temp":30, "seasons":["Kharif","Rabi"], "irrigation":True, "base_yield":2500},
    {"name":"Millet (Small millets mix)", "soils":["Sandy","Red","Laterite"], "min_rain":200, "max_rain":800, "min_temp":20, "max_temp":38, "seasons":["Kharif"], "irrigation":False, "base_yield":600},
    # add more crops as needed...
]

# Normalize soils in DB for easier checks
def normalize_soil(s: str) -> str:
    s = s.strip().lower()
    mapping = {
        'sandy': 'Sandy', 'loamy':'Loamy', 'clay':'Clay', 'silty':'Silty', 'peaty':'Peaty',
        'chalky':'Chalky', 'alluvial':'Alluvial', 'red':'Red', 'black':'Black', 'laterite':'Laterite'
    }
    return mapping.get(s, s.title())

# -------------------------
# Scoring engine
# -------------------------
def score_crop_for_conditions(crop: Dict[str, Any], soil: str, annual_rain: float, avg_temp: float, season: str, has_irrigation: bool) -> Dict[str, Any]:
    """
    Returns dict with crop, score (0..1), match details, estimated_yield_kg_per_ha (base * score)
    """
    score = 0.0
    reasons: List[str] = []
    # Soil match (30% weight)
    soil_norm = soil
    soil_match = 1 if soil_norm in crop["soils"] else 0
    score += soil_match * 0.30
    if soil_match:
        reasons.append("Soil suitable")
    else:
        reasons.append("Soil not ideal")

    # Season match (20% weight)
    season_match = 1 if (season in crop["seasons"] or "Perennial" in crop["seasons"]) else 0
    score += season_match * 0.20
    if season_match:
        reasons.append("Season suitable")
    else:
        reasons.append("Season not ideal")

    # Rainfall match (20% weight)
    rain_ok = True
    rain_score = 0.0
    if crop.get("min_rain") is not None and crop.get("max_rain") is not None:
        minr = crop["min_rain"]
        maxr = crop["max_rain"]
        # If annual_rain is None, small neutral score
        if annual_rain is None:
            rain_score = 0.1
        else:
            if minr <= annual_rain <= maxr:
                rain_score = 1.0
            else:
                # partial credit: how far from range
                diff = 0.0
                if annual_rain < minr:
                    diff = (minr - annual_rain) / max(1, minr)
                else:
                    diff = (annual_rain - maxr) / max(1, maxr)
                rain_score = max(0.0, 1.0 - diff)
    else:
        rain_score = 0.5
    score += rain_score * 0.20
    reasons.append(f"Rainfall suitability: {round(rain_score*100)}%")

    # Temperature match (15% weight)
    temp_score = 0.0
    if crop.get("min_temp") is not None and crop.get("max_temp") is not None:
        minT = crop["min_temp"]
        maxT = crop["max_temp"]
        if avg_temp is None:
            temp_score = 0.5
        else:
            if minT <= avg_temp <= maxT:
                temp_score = 1.0
            else:
                diff = 0.0
                if avg_temp < minT:
                    diff = (minT - avg_temp) / max(1, abs(minT))
                else:
                    diff = (avg_temp - maxT) / max(1, abs(maxT))
                temp_score = max(0.0, 1.0 - diff)
    else:
        temp_score = 0.5
    score += temp_score * 0.15
    reasons.append(f"Temperature suitability: {round(temp_score*100)}%")

    # Irrigation check (15% weight)
    irrigation_needed = bool(crop.get("irrigation", False))
    irrigation_score = 1.0
    if irrigation_needed and not has_irrigation:
        # if irrigation required but user does not have it, reduce score
        irrigation_score = 0.0
        reasons.append("Irrigation needed but not available")
    else:
        reasons.append("Irrigation OK")
    score += irrigation_score * 0.15

    # Final normalization; ensure in [0,1]
    final_score = max(0.0, min(1.0, score))
    est_yield_per_ha = crop["base_yield"] * final_score  # simple adjustment
    return {
        "crop": crop["name"],
        "score": final_score,
        "score_pct": round(final_score * 100, 1),
        "reasons": reasons,
        "est_yield_kg_per_ha": round(est_yield_per_ha, 1),
        "base_yield_kg_per_ha": crop["base_yield"]
    }

# -------------------------
# Streamlit UI
# -------------------------
st.header("🌾 FarmWise — Crop Predictor (India)")

col1, col2 = st.columns([1,1])

with col1:
    st.subheader("Farm Inputs (you provide)")
    soil_input = st.selectbox("Soil type (choose nearest)", [
        "Alluvial","Loamy","Sandy","Clay","Silty","Red","Black","Laterite","Chalky","Peaty"
    ])
    area_input = st.number_input("Land area (numeric)", min_value=0.01, value=1.0, step=0.01, format="%.4f")
    unit_input = st.selectbox("Unit", ["hectare","acre","square_meter","bigha","guntha","ground"])
    season_input = st.selectbox("Season / Planting window", ["Kharif","Rabi","Zaid","Perennial"])
    irrigation_checkbox = st.checkbox("I have reliable irrigation (wells, canal, borewell etc.)", value=False)
    st.markdown("**Tip:** On mobile tap **Share location** to let the app fetch local weather (temperature & rainfall) automatically.")

with col2:
    st.subheader("Location & Weather (auto)")
    # read query params for lat/lon
    params = st.experimental_get_query_params()
    lat = None
    lon = None
    if "lat" in params and "lon" in params:
        try:
            lat = float(params.get("lat")[0])
            lon = float(params.get("lon")[0])
        except:
            lat = lon = None

    if lat is None or lon is None:
        st.info("Location not provided yet.")
        # embed JS to request geolocation and reload with lat/lon in query string
        location_js = """
        <script>
        function sendLocation() {
            if (!navigator.geolocation) {
                alert('Geolocation not supported in this browser');
                return;
            }
            navigator.geolocation.getCurrentPosition(function(pos) {
                const lat = pos.coords.latitude.toFixed(6);
                const lon = pos.coords.longitude.toFixed(6);
                const search = '?' + 'lat=' + lat + '&lon=' + lon;
                // reload with query params
                window.location = window.location.pathname + search;
            }, function(err) {
                alert('Could not get location: ' + err.message + '. You can enter coordinates manually below.');
            }, {enableHighAccuracy: true, timeout:10000});
        }
        </script>
        <button onclick="sendLocation()">Share location</button>
        """
        st.components.v1.html(location_js, height=60)
        st.text_input("Or enter Latitude manually", key="manual_lat")
        st.text_input("Or enter Longitude manually", key="manual_lon")
        # If manual provided, use those
        try:
            man_lat = st.session_state.get("manual_lat", "").strip()
            man_lon = st.session_state.get("manual_lon", "").strip()
            if man_lat and man_lon:
                lat = float(man_lat)
                lon = float(man_lon)
        except:
            lat = lon = None
    else:
        st.success(f"Location detected: lat {lat}, lon {lon}")

    # Fetch weather if we have coords
    weather = None
    if lat is not None and lon is not None:
        st.write("Fetching recent weather (Open-Meteo)...")
        weather = fetch_weather_open_meteo(lat, lon)
        if weather.get("error"):
            st.error("Weather fetch error: " + weather["error"])
            weather = None
        else:
            st.write(f"Estimated avg temp: {weather.get('avg_temp_c')} °C")
            st.write(f"Estimated annual rainfall (approx): {weather.get('est_annual_precip_mm')} mm")
            st.write(f"Recent precipitation (last days sum): {weather.get('recent_precip_mm')} mm")

    if weather is None:
        st.info("Weather not available — the engine will use default climate estimates.")

# -------------------------
# Prediction trigger
# -------------------------
st.markdown("---")
if st.button("Run Prediction"):
    with st.spinner("Scoring crops..."):
        soil_norm = normalize_soil(soil_input)
        area_ha = convert_to_hectare(area_input, unit_input)
        avg_temp = None
        annual_rain = None
        if weather:
            avg_temp = weather.get("avg_temp_c")
            annual_rain = weather.get("est_annual_precip_mm")
        # If weather missing, use approximate regional default based on soil/season heuristic:
        if avg_temp is None:
            avg_temp = 25.0
        if annual_rain is None:
            # coarse defaults by season
            if season_input == "Kharif":
                annual_rain = 900.0
            elif season_input == "Rabi":
                annual_rain = 500.0
            elif season_input == "Zaid":
                annual_rain = 700.0
            else:
                annual_rain = 900.0

        results = []
        for c in CROPS:
            r = score_crop_for_conditions(c, soil_norm, annual_rain, avg_temp, season_input, irrigation_checkbox)
            # calculate total estimated yield using area
            total_est_yield = r["est_yield_kg_per_ha"] * area_ha
            r["area_hectare"] = round(area_ha,4)
            r["total_est_yield_kg"] = round(total_est_yield,1)
            results.append(r)

        # sort descending by score
        results_sorted = sorted(results, key=lambda x: x["score"], reverse=True)
        top_n = results_sorted[:15]  # show top candidates

        st.success(f"Top {len(top_n)} crop suggestions for the given inputs:")
        for item in top_n:
            st.markdown(f"###  {item['crop']} — **Success: {item['score_pct']}%**")
            st.write(f"- Base yield (kg/ha): {item['base_yield_kg_per_ha']}")
            st.write(f"- Estimated yield for your land ({item['area_hectare']} ha): **{item['total_est_yield_kg']} kg**")
            st.write(f"- Why: {', '.join(item['reasons'])}")
            st.markdown("---")

        # Extra: allow user to download results as JSON
        st.download_button("Download full results (JSON)", data=json.dumps(results_sorted, indent=2), file_name="farmwise_results.json", mime="application/json")

    st.balloons()

st.markdown("----")
st.caption("This is a demo rule-based predictor. Replace / tune crop requirements and base yields with your local agronomic data for higher accuracy.")
