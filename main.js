# Integrated `main.js` for Zephyr (Windows-Compatible)

```javascript
require('dotenv').config();

const {
  app,
  BrowserWindow,
  ipcMain,
  shell,
  systemPreferences,
  session
} = require('electron');

const path = require('path');
const express = require('express');
const http = require('http');
const cors = require('cors');
const { exec } = require('child_process');
const os = require('os');
const fs = require('fs');
const Groq = require('groq-sdk');

// ─────────────────────────────────────────────────────────────
// ENVIRONMENT CHECK
// ─────────────────────────────────────────────────────────────

console.log('[Zephyr] Initializing...');
console.log(`Groq Key: ${process.env.GROQ_API_KEY ? 'Loaded' : 'Missing'}`);
console.log(`Gemini Key: ${process.env.GEMINI_API_KEY ? 'Loaded' : 'Missing'}`);
console.log(`OpenRouter Key: ${process.env.OPENROUTER_API_KEY ? 'Loaded' : 'Missing'}`);

// ─────────────────────────────────────────────────────────────
// GROQ API ROTATION
// ─────────────────────────────────────────────────────────────

const GROQ_KEYS = [
  process.env.GROQ_API_KEY,
  process.env.GROQ_API_KEY_2,
  process.env.GROQ_API_KEY_3,
].filter(Boolean);

let currentKeyIndex = 0;

let groq = new Groq({
  apiKey: GROQ_KEYS[currentKeyIndex]
});

function rotateGroqKey(reason) {
  currentKeyIndex = (currentKeyIndex + 1) % GROQ_KEYS.length;

  groq = new Groq({
    apiKey: GROQ_KEYS[currentKeyIndex]
  });

  console.log(`[Groq] Rotated Key -> ${currentKeyIndex + 1}`);
}

function isKeyExhausted(err) {
  const msg = (err.message || '').toLowerCase();

  return (
    msg.includes('rate limit') ||
    msg.includes('quota') ||
    msg.includes('permission') ||
    msg.includes('blocked')
  );
}

// ─────────────────────────────────────────────────────────────
// EXPRESS LOCAL SERVER
// ─────────────────────────────────────────────────────────────

let server;

function startLocalServer() {
  const appServer = express();

  appServer.use(cors());
  appServer.use(express.static(__dirname));

  server = http.createServer(appServer);

  server.listen(3000, () => {
    console.log('[Zephyr] Local server running at http://localhost:3000');
  });
}

// ─────────────────────────────────────────────────────────────
// ELECTRON WINDOW
// ─────────────────────────────────────────────────────────────

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 800,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    backgroundColor: '#00000000',

    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },

    icon: path.join(__dirname, 'assets', 'icon.png'),
    show: false,
  });

  mainWindow.loadURL('http://localhost:3000/index.html');

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    mainWindow.maximize();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// ─────────────────────────────────────────────────────────────
// MICROPHONE PERMISSION
// ─────────────────────────────────────────────────────────────

async function requestMicrophonePermission() {
  const status = systemPreferences.getMediaAccessStatus('microphone');

  console.log(`[Mic] Status -> ${status}`);

  if (status !== 'granted') {
    shell.openExternal('ms-settings:privacy-microphone');
  }
}

// ─────────────────────────────────────────────────────────────
// WINDOW CONTROLS
// ─────────────────────────────────────────────────────────────

ipcMain.on('minimize-window', () => {
  if (mainWindow) mainWindow.minimize();
});

ipcMain.on('maximize-window', () => {
  if (mainWindow) {
    mainWindow.isMaximized()
      ? mainWindow.unmaximize()
      : mainWindow.maximize();
  }
});

ipcMain.on('close-window', () => {
  if (mainWindow) mainWindow.close();
});

// ─────────────────────────────────────────────────────────────
// OPEN WINDOWS APPS
// ─────────────────────────────────────────────────────────────

function openWindowsApp(appName) {
  const apps = {
    chrome: 'start chrome',
    vscode: 'code',
    notepad: 'notepad',
    calculator: 'calc',
    explorer: 'explorer',
    spotify: 'start spotify',
    discord: 'start discord',
    whatsapp: 'start whatsapp',
    telegram: 'start telegram',
    edge: 'start msedge',
  };

  if (apps[appName]) {
    exec(apps[appName]);
    return true;
  }

  return false;
}

// ─────────────────────────────────────────────────────────────
// COMMAND HANDLER
// ─────────────────────────────────────────────────────────────

ipcMain.handle('run-command', async (event, data) => {

  // OPEN APP
  if (data.action === 'open_app') {
    const success = openWindowsApp(data.app);

    return {
      success,
      error: success ? null : 'Unknown app'
    };
  }

  // OPEN URL
  if (data.action === 'open_url') {
    exec(`start ${data.url}`);

    return {
      success: true
    };
  }

  // WEB SEARCH
  if (data.action === 'web_search') {
    const query = encodeURIComponent(data.query);

    exec(`start https://www.google.com/search?q=${query}`);

    return {
      success: true
    };
  }

  // SYSTEM COMMANDS
  if (data.action === 'system') {

    const commands = {
      shutdown: 'shutdown /s /t 0',
      restart: 'shutdown /r /t 0',
      lock: 'rundll32.exe user32.dll,LockWorkStation',
    };

    if (commands[data.command]) {
      exec(commands[data.command]);

      return {
        success: true
      };
    }
  }

  return {
    success: false,
    error: 'Unknown action'
  };
});

// ─────────────────────────────────────────────────────────────
// GROQ CHAT HANDLER
// ─────────────────────────────────────────────────────────────

ipcMain.handle('groq-chat', async (event, messages) => {

  const retries = GROQ_KEYS.length;

  for (let i = 0; i < retries; i++) {

    try {

      const completion = await groq.chat.completions.create({
        messages,
        model: 'llama-3.3-70b-versatile'
      });

      const reply = completion.choices[0].message.content;

      return {
        success: true,
        reply
      };

    } catch (err) {

      console.error('[Groq Error]', err.message);

      if (isKeyExhausted(err)) {
        rotateGroqKey(err.message);
        continue;
      }

      return {
        success: false,
        error: err.message
      };
    }
  }

  return {
    success: false,
    error: 'All keys exhausted'
  };
});

// ─────────────────────────────────────────────────────────────
// GROQ SPEECH TO TEXT
// ─────────────────────────────────────────────────────────────

ipcMain.handle('groq-stt', async (event, buffer) => {

  const tempPath = path.join(os.tmpdir(), `zephyr_audio_${Date.now()}.webm`);

  fs.writeFileSync(tempPath, Buffer.from(buffer));

  try {

    const transcription = await groq.audio.transcriptions.create({
      file: fs.createReadStream(tempPath),
      model: 'whisper-large-v3-turbo',
      language: 'en'
    });

    fs.unlinkSync(tempPath);

    return {
      success: true,
      text: transcription.text
    };

  } catch (err) {

    if (fs.existsSync(tempPath)) {
      fs.unlinkSync(tempPath);
    }

    return {
      success: false,
      error: err.message
    };
  }
});

// ─────────────────────────────────────────────────────────────
// GEMINI CHAT
// ─────────────────────────────────────────────────────────────

ipcMain.handle('gemini-chat', async (event, messages) => {

  try {

    const apiKey = process.env.GEMINI_API_KEY;

    const contents = messages.map(msg => ({
      role: msg.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: msg.content }]
    }));

    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ contents })
      }
    );

    const data = await response.json();

    const reply = data.candidates[0].content.parts[0].text;

    return {
      success: true,
      reply
    };

  } catch (err) {

    return {
      success: false,
      error: err.message
    };
  }
});

// ─────────────────────────────────────────────────────────────
// ELECTRON LIFECYCLE
// ─────────────────────────────────────────────────────────────

app.whenReady().then(async () => {

  console.log('[Zephyr] App Ready');

  await requestMicrophonePermission();

  session.defaultSession.setPermissionRequestHandler(
    (webContents, permission, callback) => {

      const allowed = [
        'media',
        'microphone',
        'audioCapture'
      ];

      callback(allowed.includes(permission));
    }
  );

  startLocalServer();
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
```

---
npm install electron express cors dotenv groq-sdk

GROQ_API_KEY=your_key
GROQ_API_KEY_2=your_second_key
GEMINI_API_KEY=your_key
OPENROUTER_API_KEY=your_key

