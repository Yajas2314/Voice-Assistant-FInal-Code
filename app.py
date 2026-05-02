import streamlit as st
from datetime import datetime
import speech_recognition as sr
import pyttsx3
import webbrowser
import hashlib
import os

# ---------------- CONFIG ---------------- #
APP_NAME = "ZEPHYR 2.0"
PASSWORD_HASH = hashlib.sha256("1234".encode()).hexdigest()

# ---------------- INIT ---------------- #
st.set_page_config(page_title=APP_NAME, layout="wide")

if "auth" not in st.session_state:
    st.session_state.auth = False

if "logs" not in st.session_state:
    st.session_state.logs = []

# ---------------- SECURITY ---------------- #
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def authenticate():
    st.markdown("### 🔐 Secure Login")
    pwd = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        if hash_password(pwd) == PASSWORD_HASH:
            st.session_state.auth = True
            st.success("Access Granted")
        else:
            st.error("Access Denied")

    return st.session_state.auth

def log_command(command):
    time = datetime.now().strftime("%H:%M:%S")
    entry = f"[{time}] {command}"
    st.session_state.logs.append(entry)

    os.makedirs("logs", exist_ok=True)
    with open("logs/history.txt", "a") as f:
        f.write(entry + "\n")

# ---------------- VOICE ---------------- #
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening...")
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio)
        return command.lower()
    except:
        return ""

# ---------------- FEATURES ---------------- #
def tell_time():
    return datetime.now().strftime("%H:%M")

def search_google(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")

# ---------------- COMMAND HANDLER ---------------- #
def handle_command(command):
    log_command(command)

    if "time" in command:
        result = tell_time()
        speak(f"The time is {result}")
        return f"🕒 Time: {result}"

    elif "search" in command:
        query = command.replace("search", "")
        search_google(query)
        return f"🌐 Searching: {query}"

    elif "hello" in command:
        speak("Hello, how can I help you?")
        return "👋 Hello!"

    elif "lock" in command:
        st.session_state.auth = False
        return "🔒 System Locked"

    elif "exit" in command:
        speak("Goodbye")
        return "👋 Exiting..."

    else:
        return "⚠️ Command not recognized"

# ---------------- UI DESIGN ---------------- #
st.markdown("""
<style>
body {
    background-color: #0b0f1a;
}
.main-title {
    text-align: center;
    font-size: 42px;
    color: #00f0ff;
    text-shadow: 0 0 25px #00f0ff;
}
.panel {
    border: 1px solid #00f0ff;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 0 20px #00f0ff;
}
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="main-title">🤖 {APP_NAME}</div>', unsafe_allow_html=True)

# ---------------- AUTH CHECK ---------------- #
if not st.session_state.auth:
    if not authenticate():
        st.stop()

# ---------------- LAYOUT ---------------- #
col1, col2 = st.columns(2)

# -------- LEFT: VOICE -------- #
with col1:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("🎤 Voice Command")

    if st.button("Start Listening"):
        command = listen()
        st.write("You:", command)

        if command:
            response = handle_command(command)
            st.success(response)

    st.markdown('</div>', unsafe_allow_html=True)

# -------- RIGHT: TEXT -------- #
with col2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("💬 Manual Command")

    user_input = st.text_input("Enter command")

    if st.button("Execute"):
        if user_input:
            response = handle_command(user_input.lower())
            st.success(response)

    st.markdown('</div>', unsafe_allow_html=True)

# -------- LOGS -------- #
st.markdown("### 📜 Activity Logs")
for log in reversed(st.session_state.logs[-5:]):
    st.text(log)

# -------- FOOTER -------- #
st.markdown("---")
st.write("🔐 Secure | ⚡ Fast | 🤖 Zephyr 2.0")
