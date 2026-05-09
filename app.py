import streamlit as st
from datetime import datetime
import hashlib
import os
import requests
from openai import OpenAI

# ---------------- CONFIG ---------------- #
APP_NAME = "ZEPHYR 2.0"

# 🔐 SECURITY PASSWORD
PASSWORD_HASH = hashlib.sha256("1234".encode()).hexdigest()

# 🌦 WEATHER API
WEATHER_API_KEY = "089cb559edf9127ca22ca63afa575f8c"

# 🤖 OPENAI API
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🤖",
    layout="wide"
)

# ---------------- SESSION STATE ---------------- #
if "auth" not in st.session_state:
    st.session_state.auth = False

if "logs" not in st.session_state:
    st.session_state.logs = []

if "login_attempts" not in st.session_state:
    st.session_state.login_attempts = 0

# ---------------- SECURITY ---------------- #
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate():

    st.subheader("🔐 Secure Login")

    if st.session_state.login_attempts >= 3:
        st.error("Too many failed attempts. Access blocked.")
        st.stop()

    password = st.text_input(
        "Enter Password",
        type="password"
    )

    if st.button("Login"):

        if hash_password(password) == PASSWORD_HASH:

            st.session_state.auth = True
            st.success("✅ Access Granted")

        else:

            st.session_state.login_attempts += 1

            st.error(
                f"❌ Access Denied "
                f"({st.session_state.login_attempts}/3)"
            )

    return st.session_state.auth

# ---------------- LOGGING ---------------- #
def log_command(command):

    current_time = datetime.now().strftime("%H:%M:%S")

    entry = f"[{current_time}] {command}"

    st.session_state.logs.append(entry)

    os.makedirs("logs", exist_ok=True)

    with open("logs/history.txt", "a") as file:
        file.write(entry + "\n")

# ---------------- FEATURES ---------------- #

# 🕒 TIME
def tell_time():
    return datetime.now().strftime("%H:%M:%S")

# 🌦 WEATHER
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
            return "❌ City not found."

        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]

        desc = data["weather"][0]["description"]

        country = data["sys"]["country"]

        return (
            f"📍 {city}, {country}\n\n"
            f"🌡 Temperature: {temp}°C\n"
            f"🤗 Feels Like: {feels}°C\n"
            f"💧 Humidity: {humidity}%\n"
            f"☁ Condition: {desc}"
        )

    except Exception as e:
        return f"⚠ Weather Error: {str(e)}"

# 🌐 GOOGLE SEARCH LINK
def get_google_link(query):
    return f"https://www.google.com/search?q={query}"

# 🤖 AI FUNCTION
def ask_ai(prompt):

    try:

        # Empty Input
        if prompt.strip() == "":
            return "I can't understand what you typed. Please try again."

        response = client.responses.create(
            model="gpt-4.1-mini",

            input=f"""
            You are Zephyr 2.0.

            You are:
            - intelligent
            - reliable
            - friendly
            - educational
            - safe

            Rules:
            - Answer every query clearly.
            - If query is confusing say:
              'I can't understand what you typed.
               Please try again.'
            - Keep responses useful and simple.
            - Be polite and user friendly.

            User Query:
            {prompt}
            """
        )

        ai_reply = response.output_text.strip()

        if ai_reply == "":
            return "I can't understand what you typed. Please try again."

        return ai_reply

    except Exception:

        google_link = get_google_link(prompt)

        return (
            "⚠ AI service unavailable.\n\n"
            f"🔎 Backup Google Search:\n{google_link}"
        )

# ---------------- COMMAND ENGINE ---------------- #
def handle_command(command):

    command = command.lower()

    log_command(command)

    # 🕒 TIME
    if "time" in command:

        return f"🕒 Current Time: {tell_time()}"

    # 🌦 WEATHER
    elif "weather" in command:

        city = command.replace("weather", "").strip()

        if city == "":
            return (
                "Please type a city name.\n\n"
                "Example:\n"
                "weather Mumbai"
            )

        return get_weather(city)

    # 🔎 SEARCH
    elif command.startswith("search"):

        query = command.replace("search", "").strip()

        if query == "":
            return "Please type something to search."

        google_url = get_google_link(query)

        st.markdown(
            f"[🔎 Click here to search Google]({google_url})",
            unsafe_allow_html=True
        )

        return f"Searching Google for: {query}"

    # 🔒 LOCK
    elif "lock" in command:

        st.session_state.auth = False

        return "🔒 System Locked"

    # 🧹 CLEAR LOGS
    elif "clear logs" in command:

        st.session_state.logs.clear()

        return "🧹 Logs Cleared"

    # 🤖 AI DEFAULT
    else:

        ai_response = ask_ai(command)

        google_url = get_google_link(command)

        st.markdown(
            f"[🔎 Search on Google]({google_url})",
            unsafe_allow_html=True
        )

        return "🤖 " + ai_response

# ---------------- UI DESIGN ---------------- #
st.markdown("""
<style>

body {
    background-color: #0b0f1a;
}

.title {
    text-align: center;
    font-size: 50px;
    font-weight: bold;
    color: #00f0ff;
    text-shadow: 0 0 20px #00f0ff;
    margin-bottom: 20px;
}

.panel {
    border: 1px solid #00f0ff;
    border-radius: 15px;
    padding: 20px;
    background-color: rgba(0,0,0,0.35);
    box-shadow: 0 0 15px #00f0ff;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ---------------- #
st.markdown(
    f'<div class="title">🤖 {APP_NAME}</div>',
    unsafe_allow_html=True
)

# ---------------- AUTH ---------------- #
if not st.session_state.auth:

    if not authenticate():
        st.stop()

# ---------------- DASHBOARD ---------------- #
col1, col2 = st.columns(2)

# LEFT PANEL
with col1:

    st.markdown(
        '<div class="panel">',
        unsafe_allow_html=True
    )

    st.subheader("💬 Command Center")

    user_input = st.text_input(
        "Enter command",
        placeholder="Ask Zephyr anything..."
    )

    if st.button("Execute"):

        if user_input.strip() != "":

            result = handle_command(user_input)

            st.success(result)

        else:

            st.warning(
                "I can't understand what you typed."
            )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

# RIGHT PANEL
with col2:

    st.markdown(
        '<div class="panel">',
        unsafe_allow_html=True
    )

    st.subheader("📊 System Information")

    st.write("🕒 Current Time:", tell_time())

    st.write("📜 Total Logs:", len(st.session_state.logs))

    st.write(
        "🌦 Example Weather Command:",
        "weather Mumbai"
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

# ---------------- LOGS ---------------- #
st.subheader("📜 Activity Logs")

if len(st.session_state.logs) == 0:

    st.info("No logs available.")

else:

    for log in reversed(st.session_state.logs[-10:]):
        st.text(log)

# ---------------- FOOTER ---------------- #
st.markdown("---")

st.write(
    "🔐 Secure | 🌐 Google Backup | "
    "🤖 OpenAI Powered | Zephyr 2.0"
)
