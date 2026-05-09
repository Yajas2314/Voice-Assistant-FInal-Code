import streamlit as st
from datetime import datetime
import hashlib
import os
import requests
import pytz
from openai import OpenAI

# =========================================================
# 🤖 ZEPHYR 2.0 - ADVANCED AI ASSISTANT
# =========================================================

APP_NAME = "ZEPHYR 2.0"

# =========================================================
# 🔐 SECURITY
# =========================================================

PASSWORD_HASH = hashlib.sha256(
    "1234".encode()
).hexdigest()

# =========================================================
# 🌦 WEATHER API
# =========================================================

WEATHER_API_KEY = "089cb559edf9127ca22ca63afa575f8c"

# =========================================================
# 🤖 OPENAI CLIENT
# =========================================================

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# =========================================================
# 🎨 PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🤖",
    layout="wide"
)

# =========================================================
# 🧠 SESSION STATE
# =========================================================

if "auth" not in st.session_state:
    st.session_state.auth = False

if "logs" not in st.session_state:
    st.session_state.logs = []

if "login_attempts" not in st.session_state:
    st.session_state.login_attempts = 0

# =========================================================
# 🔐 AUTHENTICATION
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate():

    st.subheader("🔐 Secure Login")

    if st.session_state.login_attempts >= 3:
        st.error("Too many failed attempts.")
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
                f"❌ Wrong Password "
                f"({st.session_state.login_attempts}/3)"
            )

    return st.session_state.auth

# =========================================================
# 📜 LOGGING
# =========================================================

def log_command(command):

    india_timezone = pytz.timezone("Asia/Kolkata")

    current_time = datetime.now(
        india_timezone
    ).strftime("%I:%M:%S %p")

    entry = f"[{current_time}] {command}"

    st.session_state.logs.append(entry)

    os.makedirs("logs", exist_ok=True)

    with open("logs/history.txt", "a") as file:
        file.write(entry + "\n")

# =========================================================
# 🕒 INDIA TIME
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
            return "❌ City not found."

        temp = data["main"]["temp"]

        feels = data["main"]["feels_like"]

        humidity = data["main"]["humidity"]

        desc = data["weather"][0]["description"]

        country = data["sys"]["country"]

        wind = data["wind"]["speed"]

        return (
            f"📍 {city}, {country}\n\n"
            f"🌡 Temperature: {temp}°C\n"
            f"🤗 Feels Like: {feels}°C\n"
            f"💧 Humidity: {humidity}%\n"
            f"🌬 Wind Speed: {wind} m/s\n"
            f"☁ Condition: {desc}"
        )

    except Exception as e:
        return f"⚠ Weather Error: {str(e)}"

# =========================================================
# 🌐 SEARCH LINKS
# =========================================================

def get_search_links(query):

    clean_query = query.strip().replace(
        " ",
        "+"
    )

    return {

        "google":
            f"https://www.google.com/search?q={clean_query}",

        "youtube":
            f"https://www.youtube.com/results?"
            f"search_query={clean_query}",

        "websites":
            f"https://www.google.com/search?q="
            f"{clean_query}+tutorial+guide",

        "recipe":
            f"https://www.google.com/search?q="
            f"{clean_query}+recipe"
    }

# =========================================================
# 🤖 AI ENGINE
# =========================================================

def ask_ai(prompt):

    try:

        if prompt.strip() == "":
            return (
                "I can't understand what you typed. "
                "Please try again."
            )

        response = client.responses.create(

            model="gpt-4.1-mini",

            input=f"""
You are Zephyr 2.0.

You are:
- intelligent
- reliable
- modern
- educational
- safe
- friendly

Your tasks:
- answer every query properly
- help students
- help in coding
- help in science
- help in mathematics
- help in general knowledge
- give proper steps
- explain clearly

Rules:
- If query is unclear say:
  "I can't understand what you typed.
   Please try again."

- Never give blank answers
- Keep answers clear and useful
- Be polite and natural

User Query:
{prompt}
"""
        )

        ai_reply = response.output_text.strip()

        if ai_reply == "":
            return (
                "I can't understand what you typed."
            )

        return ai_reply

    except Exception:

        return (
            "⚠ AI Service unavailable right now."
        )

# =========================================================
# ⚙ COMMAND ENGINE
# =========================================================

def handle_command(command):

    command = command.strip()

    lower_command = command.lower()

    log_command(command)

    # =====================================================
    # 🕒 TIME
    # =====================================================

    if "time" in lower_command:

        return (
            f"🕒 Current Indian Time: "
            f"{tell_time()}"
        )

    # =====================================================
    # 🌦 WEATHER
    # =====================================================

    elif lower_command.startswith("weather"):

        city = lower_command.replace(
            "weather",
            ""
        ).strip()

        if city == "":

            return (
                "Please type a city name.\n\n"
                "Example:\n"
                "weather Mumbai"
            )

        return get_weather(city)

    # =====================================================
    # 🔎 SEARCH
    # =====================================================

    elif lower_command.startswith("search"):

        query = lower_command.replace(
            "search",
            ""
        ).strip()

        if query == "":
            return "Please type something to search."

        links = get_search_links(query)

        st.markdown(
            f"""
### 🔎 Recommended Results

- [🌐 Google Search]({links['google']})

- [🎥 YouTube Videos]({links['youtube']})

- [📘 Tutorials & Websites]({links['websites']})

- [🍳 Recipes & Articles]({links['recipe']})
""",
            unsafe_allow_html=True
        )

        return f"Searching for: {query}"

    # =====================================================
    # 🔒 LOCK
    # =====================================================

    elif "lock" in lower_command:

        st.session_state.auth = False

        return "🔒 System Locked"

    # =====================================================
    # 🧹 CLEAR LOGS
    # =====================================================

    elif "clear logs" in lower_command:

        st.session_state.logs.clear()

        return "🧹 Logs Cleared"

    # =====================================================
    # 🤖 AI DEFAULT
    # =====================================================

    else:

        ai_response = ask_ai(command)

        links = get_search_links(command)

        st.markdown(
            f"""
### 🔎 Recommended Links

- [🌐 Google Search]({links['google']})

- [🎥 YouTube Videos]({links['youtube']})

- [📘 Tutorials & Websites]({links['websites']})

- [🍳 Articles & Recipes]({links['recipe']})
""",
            unsafe_allow_html=True
        )

        return "🤖 " + ai_response

# =========================================================
# 🎨 UI DESIGN
# =========================================================

st.markdown("""
<style>

body {
    background-color: #0b0f1a;
}

.title {
    text-align: center;
    font-size: 55px;
    font-weight: bold;
    color: #00f0ff;
    text-shadow: 0 0 25px #00f0ff;
    margin-bottom: 25px;
}

.panel {
    border: 1px solid #00f0ff;
    border-radius: 18px;
    padding: 20px;
    background-color: rgba(0,0,0,0.35);
    box-shadow: 0 0 15px #00f0ff;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# 🤖 TITLE
# =========================================================

st.markdown(
    f'<div class="title">🤖 {APP_NAME}</div>',
    unsafe_allow_html=True
)

# =========================================================
# 🔐 LOGIN
# =========================================================

if not st.session_state.auth:

    if not authenticate():
        st.stop()

# =========================================================
# 📊 DASHBOARD
# =========================================================

col1, col2 = st.columns(2)

# =========================================================
# 💬 LEFT PANEL
# =========================================================

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

# =========================================================
# 📈 RIGHT PANEL
# =========================================================

with col2:

    st.markdown(
        '<div class="panel">',
        unsafe_allow_html=True
    )

    st.subheader("📊 System Information")

    st.write(
        "🕒 Indian Time:",
        tell_time()
    )

    st.write(
        "📜 Total Logs:",
        len(st.session_state.logs)
    )

    st.write(
        "🌦 Weather Example:",
        "weather Tokyo"
    )

    st.write(
        "🔎 Search Example:",
        "search best gaming laptop"
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

# =========================================================
# 📜 LOGS
# =========================================================

st.subheader("📜 Activity Logs")

if len(st.session_state.logs) == 0:

    st.info("No logs available.")

else:

    for log in reversed(
        st.session_state.logs[-10:]
    ):
        st.text(log)

# =========================================================
# 🦶 FOOTER
# =========================================================

st.markdown("---")

st.write(
    "🔐 Secure | 🌐 Google Connected | "
    "🎥 YouTube Connected | 🤖 OpenAI Powered "
    "| 🇮🇳 Indian Time Enabled | Zephyr 2.0"
)
