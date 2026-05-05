import streamlit as st
from datetime import datetime
import hashlib
import webbrowser
import os
import requests
from openai import OpenAI

# ---------------- CONFIG ---------------- #
APP_NAME = "ZEPHYR 2.0"

# 🔐 SECURITY
PASSWORD_HASH = hashlib.sha256("1234".encode()).hexdigest()

# 🌦 WEATHER API
WEATHER_API_KEY = "089cb559edf9127ca22ca63afa575f8c"

# 🤖 OPENAI API (SET IN ENV VARIABLE)
client = OpenAI(api_key=os.getenv("GITHUB_API_KEY"))

st.set_page_config(page_title=APP_NAME, layout="wide")

# ---------------- SESSION ---------------- #
if "auth" not in st.session_state:
    st.session_state.auth = False

if "logs" not in st.session_state:
    st.session_state.logs = []

if "login_attempts" not in st.session_state:
    st.session_state.login_attempts = 0

# ---------------- SECURITY ---------------- #
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def authenticate():
    st.subheader("🔐 Secure Login")

    if st.session_state.login_attempts >= 3:
        st.error("Too many failed attempts. Access blocked.")
        st.stop()

    pwd = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        if hash_password(pwd) == PASSWORD_HASH:
            st.session_state.auth = True
            st.success("Access Granted")
        else:
            st.session_state.login_attempts += 1
            st.error(f"Access Denied ({st.session_state.login_attempts}/3)")

    return st.session_state.auth

def log_command(command):
    time = datetime.now().strftime("%H:%M:%S")
    entry = f"[{time}] {command}"

    st.session_state.logs.append(entry)

    os.makedirs("logs", exist_ok=True)
    with open("logs/history.txt", "a") as f:
        f.write(entry + "\n")

# ---------------- FEATURES ---------------- #

# 🕒 Time
def tell_time():
    return datetime.now().strftime("%H:%M")

# 🌦 Weather
def get_weather(city="Mumbai"):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"{city}: {temp}°C, {desc}"
    except:
        return "Weather API error"

# 🌐 Web
def search_google(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")

def open_google():
    webbrowser.open("https://www.google.com")

# 🎵 Spotify
def open_spotify():
    webbrowser.open("https://open.spotify.com")

# 💻 Apps (Windows)
def open_notepad():
    os.system("notepad")

def open_chrome():
    os.system("start chrome")

# 🤖 AI
def ask_ai(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are Zephyr, a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)}"

# ---------------- COMMAND ENGINE ---------------- #
def handle_command(command):
    command = command.lower()
    log_command(command)

    if "time" in command:
        return f"🕒 {tell_time()}"

    elif "weather" in command:
        return f"🌦 {get_weather()}"

    elif command.startswith("search"):
        query = command.replace("search", "")
        search_google(query)
        return f"🌐 Searching: {query}"

    elif "open google" in command:
        open_google()
        return "🌐 Opening Google"

    elif "spotify" in command:
        open_spotify()
        return "🎵 Opening Spotify"

    elif "open notepad" in command:
        open_notepad()
        return "💻 Opening Notepad"

    elif "open chrome" in command:
        open_chrome()
        return "🌐 Opening Chrome"

    elif "lock" in command:
        st.session_state.auth = False
        return "🔒 System Locked"

    elif "clear logs" in command:
        st.session_state.logs.clear()
        return "🧹 Logs Cleared"

    else:
        return "🤖 " + ask_ai(command)

# ---------------- UI ---------------- #
st.markdown("""
<style>
body {
    background-color: #0b0f1a;
}
.title {
    text-align: center;
    font-size: 45px;
    color: #00f0ff;
    text-shadow: 0 0 30px #00f0ff;
}
.panel {
    border: 1px solid #00f0ff;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 0 20px #00f0ff;
}
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="title">🤖 {APP_NAME}</div>', unsafe_allow_html=True)

# ---------------- AUTH ---------------- #
if not st.session_state.auth:
    if not authenticate():
        st.stop()

# ---------------- DASHBOARD ---------------- #
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("💬 Command Center")

    user_input = st.text_input("Enter command")

    if st.button("Execute"):
        if user_input:
            result = handle_command(user_input)
            st.success(result)

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("📊 System Info")

    st.write("🕒 Time:", tell_time())
    st.write("🌦 Weather:", get_weather())
    st.write("📜 Logs:", len(st.session_state.logs))

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- LOGS ---------------- #
st.subheader("📜 Activity Logs")
for log in reversed(st.session_state.logs[-10:]):
    st.text(log)

# ---------------- FOOTER ---------------- #
st.markdown("---")
st.write("🔐 Secure | 🌐 API Powered | 🤖 AI Enabled Zephyr 2.0")
