# farmwise_ai_all_in_one.py
import streamlit as st
from gtts import gTTS
import os
import speech_recognition as sr

# ---------------------------
# Helper Functions
# ---------------------------

def text_to_speech(text, lang='hi'):
    """Convert text to speech and return audio file path"""
    tts = gTTS(text=text, lang=lang)
    filename = "voice.mp3"
    tts.save(filename)
    return filename

def play_audio(file_path):
    """Streamlit audio player"""
    audio_file = open(file_path, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')

def voice_input(lang='hi-IN'):
    """Record voice and convert to text"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Speak now...")
        audio = r.listen(source, phrase_time_limit=5)
        try:
            text = r.recognize_google(audio, language=lang)
            return text
        except:
            return "Sorry, could not understand."

# ---------------------------
# Central AI Engine (Simplified)
# ---------------------------

def ai_engine(inputs):
    soil = inputs['soil']
    season = inputs['season']
    area = inputs['area']
    location = inputs['location']

    # Crop prediction logic
    if soil == "Loamy" and season.lower() in ["kharif", "monsoon"]:
        crop = "Rice"
    elif soil == "Sandy" and season.lower() in ["rabi", "winter"]:
        crop = "Wheat"
    else:
        crop = "Maize"

    # Pest prediction logic
    pests = {
        "Rice": "Rice weevil, Leaf roller",
        "Wheat": "Aphids, Armyworm",
        "Maize": "Stem borer, Fall armyworm"
    }
    pest = pests.get(crop, "No major pests predicted")

    # Cost estimation logic
    base_cost = {"Rice": 5000, "Wheat": 4000, "Maize": 3000}
    cost = base_cost.get(crop, 3500) * area

    # Result dictionary
    result = {
        'crop': crop,
        'pest': pest,
        'cost': cost
    }
    return result

# ---------------------------
# Streamlit App
# ---------------------------

st.title("🌾 FarmWise AI - Voice Enabled All-in-One Assistant")
st.write("Voice interaction and AI-powered crop, pest, and cost prediction for Indian farmers.")

# User Inputs
soil = st.selectbox("Select Soil Type", ["Loamy", "Sandy", "Clayey", "Alluvial"])
season = st.selectbox("Select Season", ["Kharif", "Rabi", "Zaid"])
area = st.number_input("Enter Land Area in acres", min_value=0.1, step=0.1)
location = st.text_input("Enter your location (City/Village)")

lang = st.selectbox("Select Language for Voice", ["hi", "en", "ta", "te", "bn", "ml", "kn", "mr", "gu", "pa", "or", "as"])
voice_option = st.radio("Do you want to use voice input?", ["No", "Yes"])

# Voice input capture
user_query = None
if voice_option == "Yes":
    lang_code = lang + "-IN" if lang != "en" else "en-US"
    user_query = voice_input(lang=lang_code)
    st.success(f"You said: {user_query}")

# Prepare inputs
inputs = {
    'soil': soil,
    'season': season,
    'area': area,
    'location': location,
    'query': user_query
}

# Run AI Engine
if st.button("Predict"):
    result = ai_engine(inputs)
    result_text = f"🌱 Recommended Crop: {result['crop']}\n🐛 Predicted Pests: {result['pest']}\n💰 Estimated Cost: ₹{result['cost']}"
    
    st.text(result_text)

    # Voice Output
    audio_file = text_to_speech(result_text, lang=lang)
    play_audio(audio_file)

