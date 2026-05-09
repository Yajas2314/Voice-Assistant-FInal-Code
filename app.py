import streamlit as st
from datetime import datetime
import pytz
import hashlib
import requests
import os
import uuid
import tempfile

from openai import OpenAI
from gtts import gTTS
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder

# =========================================================
# 🤖 ZEPHYR 2.0
# =========================================================

APP_NAME = "ZEPHYR 2.0"

# =========================================================
# 🔐 PASSWORD
# =========================================================

PASSWORD_HASH = hashlib.sha256(
    "1234".encode()
).hexdigest()

# =========================================================
# 🌦 WEATHER API
# =========================================================

WEATHER_API_KEY = "089cb559edf9127ca22ca63afa575f8c"

# =========================================================
# 🤖 OPENAI
# =========================================================

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# =========================================================
# 🎨 PAGE
# =========================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🤖",
    layout="wide"
)

# =========================================================
# 🧠 SESSION
# =========================================================

if "auth" not in st.session_state:
    st.session_state.auth = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "logs" not in st.session_state:
    st.session_state.logs = []

# =========================================================
# 🇮🇳 INDIA TIME
# =========================================================


def tell_time():

    india_timezone = pytz.timezone(
        "Asia/Kolkata"
    )

    india_time = datetime.now(
        india_timezone
    )

    return india_time.strftime(
        "%I:%M:%S %p"
    )

# =========================================================
# 🔐 AUTH
# =========================================================


def authenticate():

    st.subheader("🔐 Login")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        if hashlib.sha256(
            password.encode()
        ).hexdigest() == PASSWORD_HASH:

            st.session_state.auth = True

            st.success("Access Granted")

        else:
            st.error("Wrong Password")

# =========================================================
# 📜 LOGGING
# =========================================================


def log_command(command):

    current_time = tell_time()

    entry = f"[{current_time}] {command}"

    st.session_state.logs.append(entry)

# =========================================================
# 🌦 WEATHER
# =========================================================


def get_weather(city):

    try:

        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}"
            f"&appid={WEATHER_API_KEY}"
            "&units=metric"
        )

        response = requests.get(url)

        data = response.json()

        if data["cod"] != 200:
            return "City not found"

        temp = data["main"]["temp"]

        desc = data["weather"][0]["description"]

        humidity = data["main"]["humidity"]

        return (
            f"📍 {city}\n\n"
            f"🌡 Temperature: {temp}°C\n"
            f"☁ Condition: {desc}\n"
            f"💧 Humidity: {humidity}%"
        )

    except Exception as e:
        return f"Weather Error: {str(e)}"

# =========================================================
# 🔊 SPEAK
# =========================================================


def speak(text):

    tts = gTTS(text=text, lang="en")

    filename = f"voice_{uuid.uuid4()}.mp3"

    tts.save(filename)

    audio_file = open(filename, "rb")

    audio_bytes = audio_file.read()

    st.audio(audio_bytes, format="audio/mp3")

# =========================================================
# 🌐 SEARCH LINKS
# =========================================================


def get_search_links(query):

    query = query.replace(" ", "+")

    return {

        "google":
        f"https://www.google.com/search?q={query}",

        "youtube":
        f"https://www.youtube.com/results?search_query={query}",

        "websites":
        f"https://www.google.com/search?q={query}+tutorial",

        "recipe":
        f"https://www.google.com/search?q={query}+recipe"
    }

# =========================================================
# 🤖 AI ENGINE
# =========================================================


def ask_ai(prompt):

    try:

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        messages = [
            {
                "role": "system",
                "content": """
You are Zephyr 3.0.

You are a futuristic AI assistant.

Your tasks:
- answer every question properly
- help students
- solve coding doubts
- explain maths and science
- explain concepts clearly
- behave naturally
- be friendly and intelligent
"""
            }
        ]

        messages.extend(
            st.session_state.chat_history[-10:]
        )

        response = client.chat.completions.create(

            model="gpt-4.1-mini",

            messages=messages,

            temperature=0.7,

            max_tokens=600
        )

        ai_reply = (
            response
            .choices[0]
            .message.content
        )

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": ai_reply
            }
        )

        return ai_reply

    except Exception as e:

        return f"AI Error: {str(e)}"

# =========================================================
# ⚙ COMMAND ENGINE
# =========================================================


def handle_command(command):

    lower_command = command.lower()

    log_command(command)

    # TIME
    if "time" in lower_command:

        return f"🕒 Indian Time: {tell_time()}"

    # WEATHER
    elif lower_command.startswith("weather"):

        city = lower_command.replace(
            "weather",
            ""
        ).strip()

        if city == "":
            return "Example: weather Mumbai"

        return get_weather(city)

    # OPEN GOOGLE
    elif "open google" in lower_command:

        st.markdown(
            "[🌐 Open Google](https://google.com)"
        )

        return "Google Ready"

    # OPEN SPOTIFY
    elif "open spotify" in lower_command:

        st.markdown(
            "[🎵 Open Spotify](https://open.spotify.com)"
        )

        return "Spotify Ready"

    # OPEN YOUTUBE
    elif "open youtube" in lower_command:

        st.markdown(
            "[▶ Open YouTube](https://youtube.com)"
        )

        return "YouTube Ready"

    # AI MODE
    else:

        response = ask_ai(command)

        links = get_search_links(command)

        st.markdown(
            f"""
### 🔎 Recommended Links

- [🌐 Google Search]({links['google']})
- [🎥 YouTube Videos]({links['youtube']})
- [📘 Tutorials]({links['websites']})
- [🍳 Articles & Recipes]({links['recipe']})
"""
        )

        return response

# =========================================================
# 🎨 UI
# =========================================================

st.markdown(
    """
<style>
.title {
    text-align:center;
    font-size:55px;
    color:#00f0ff;
    font-weight:bold;
    text-shadow:0 0 20px #00f0ff;
}
</style>
""",
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="title">🤖 {APP_NAME}</div>',
    unsafe_allow_html=True
)

# =========================================================
# LOGIN
# =========================================================

if not st.session_state.auth:

    authenticate()

    st.stop()

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚡ Zephyr Controls")

    st.write("🕒", tell_time())

    st.write("📜 Logs:", len(st.session_state.logs))

    if st.button("Clear Chat"):

        st.session_state.chat_history = []

# =========================================================
# CHAT HISTORY
# =========================================================

for message in st.session_state.chat_history:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# =========================================================
# 🎤 VOICE INPUT
# =========================================================

st.subheader("🎤 Voice Assistant")

voice = mic_recorder(
    start_prompt="Start Recording",
    stop_prompt="Stop Recording",
    key="voice_recorder"
)

if voice:

    recognizer = sr.Recognizer()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    ) as temp_audio:

        temp_audio.write(voice["bytes"])

        temp_audio_path = temp_audio.name

    with sr.AudioFile(temp_audio_path) as source:

        audio_data = recognizer.record(source)

        try:

            text = recognizer.recognize_google(
                audio_data
            )

            st.success(f"You said: {text}")

            reply = handle_command(text)

            with st.chat_message("assistant"):

                st.markdown(reply)

            speak(reply)

        except:
            st.error("Could not understand audio")

# =========================================================
# 💬 CHAT INPUT
# =========================================================

user_input = st.chat_input(
    "Ask Zephyr anything..."
)

if user_input:

    with st.chat_message("user"):

        st.markdown(user_input)

    reply = handle_command(user_input)

    with st.chat_message("assistant"):

        st.markdown(reply)

    speak(reply)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.write(
    "🤖 OpenAI Powered | 🎤 Voice Enabled | "
    "🌐 Smart Search | 🇮🇳 Indian Time | Zephyr 3.0"
)
