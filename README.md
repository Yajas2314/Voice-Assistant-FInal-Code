# Voice-Assistant-FInal-Code
# 🤖 Zephyr 1.0 - AI Assistant

# Zephyr AI Assistant

A futuristic AI-powered desktop voice assistant built using:

* Electron
* JavaScript
* Python
* Groq AI
* Sarvam AI
* Express.js

Zephyr includes:

* AI chat
* Speech-to-text
* Text-to-speech
* Voice commands
* Windows automation
* Futuristic HUD interface
* Multi-model AI support

---

# Features

## AI Features

* Groq AI integration
* Whisper speech-to-text
* Sarvam text-to-speech
* Fast AI responses
* Multi-key API rotation

## Desktop Features

* Transparent futuristic HUD
* Frameless Electron window
* Always-on-top mode
* Window controls
* Local desktop application

## Automation Features

* Open applications
* Web search
* Open URLs
* System commands
* Voice-based control

---

# Technologies Used

## Frontend

* HTML
* CSS
* JavaScript
* Electron

## Backend

* Node.js
* Express.js
* Python

## AI APIs

* Groq API
* Sarvam API
* OpenRouter (optional)

---

# Project Structure

```text
Zephyr/
│
├── main.js
├── preload.js
├── renderer.js
├── index.html
├── style.css
├── package.json
├── .env
├── .gitignore
├── assets/
│   └── icon.png
├── backend/
│   └── mcp_server.py
└── node_modules/
```

---

# Installation

## 1. Install Node.js

Download and install Node.js:

[https://nodejs.org](https://nodejs.org)

---

## 2. Clone or Create Project Folder

```bash
mkdir Zephyr
cd Zephyr
```

---

## 3. Initialize npm

```bash
npm init -y
```

---

## 4. Install Dependencies

```bash
npm install electron express cors dotenv groq-sdk
```

---

# Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
SARVAM_API_KEY=your_sarvam_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
```

---

# Git Ignore

Create a `.gitignore` file:

```text
.env
node_modules/
```

---

# Running Zephyr

Start the assistant:

```bash
npm start
```

---

# package.json Script

Make sure your `package.json` contains:

```json
"main": "main.js",
"scripts": {
  "start": "electron ."
}
```

---

# Windows Compatibility

Zephyr is optimized for Windows.

Supported:

* Windows 10
* Windows 11

Some macOS-specific automation from the original inspiration project has been removed or replaced with Windows-compatible commands.

---

# Security Notes

* Never upload `.env`
* Never expose API keys publicly
* Keep API keys private
* Use `.gitignore`

---

# Future Upgrades

Planned upgrades:

* Wake word detection
* Offline AI models
* Advanced automation
* Smart memory
* Face recognition
* AI avatars
* AR/VR support
* Multi-agent system

---

# Credits

Inspired by futuristic AI assistant architectures using:

* Electron
* Groq
* MCP systems
* Voice AI pipelines

Customized and rebuilt for the Zephyr AI Assistant project.
