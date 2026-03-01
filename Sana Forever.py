"""
Sana AI Agent - Jarvis Style Voice Assistant
Fully offline, low latency, human-like speaking feedback.
"""

import os
import time
import threading
import sqlite3
from datetime import datetime

import pyttsx3
import pyautogui
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import yaml

from pynput import keyboard as pynput_keyboard

# Config
CONFIG_PATH = "config.yaml"

config = {
    "whisper_model": "tiny.en",
    "tts_voice": "default",
    "listen_duration": 1.5,
    "tts_rate": 190   # Natural Jarvis speed
}

try:
    with open(CONFIG_PATH, "r") as f:
        loaded = yaml.safe_load(f)
        if loaded:
            config.update(loaded)
except Exception:
    print("Using defaults")

# Init
engine = pyttsx3.init()
engine.setProperty('rate', config["tts_rate"])
if config["tts_voice"] != "default":
    voices = engine.getProperty('voices')
    if voices:
        engine.setProperty('voice', voices[0].id)

whisper_model = WhisperModel(config["whisper_model"], device="cpu", compute_type="int8")

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2

# Logging
def log_action(command, action, result):
    conn = sqlite3.connect("mydata.db")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS logs (timestamp TEXT, command TEXT, action TEXT, result TEXT)''')
    ts = datetime.now().isoformat()
    cur.execute("INSERT INTO logs VALUES (?, ?, ?, ?)", (ts, command, action, result))
    conn.commit()
    conn.close()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    duration = config["listen_duration"]
    fs = 16000
    print("Listening...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    audio = np.squeeze(audio)
    segments, _ = whisper_model.transcribe(audio, beam_size=5, language="en", vad_filter=True, vad_parameters=dict(min_silence_duration_ms=300))
    text = " ".join(s.text.strip() for s in segments if s.text.strip())
    print(f"You said: {text}")
    if not text:
        speak("Sorry boss, I didn't catch that. Can you repeat?")
    return text.lower().strip()

def open_anything(cmd):
    cmd = cmd.lower()
    if any(w in cmd for w in ["open", "start", "launch", "run"]) and ("chrome" in cmd or "browser" in cmd):
        pyautogui.hotkey("win", "s")
        time.sleep(0.2)
        pyautogui.write("chrome")
        pyautogui.press("enter")
        return "Opened Chrome"
    elif any(w in cmd for w in ["open", "start", "launch", "run"]) and ("notepad" in cmd or "notes" in cmd):
        pyautogui.hotkey("win", "r")
        pyautogui.write("notepad")
        pyautogui.press("enter")
        return "Opened Notepad"
    elif any(w in cmd for w in ["open", "start", "launch", "run"]) and ("calculator" in cmd or "calc" in cmd):
        pyautogui.hotkey("win", "r")
        pyautogui.write("calc")
        pyautogui.press("enter")
        return "Opened Calculator"
    return None

def process_command(cmd):
    start_time = time.time()

    if not cmd:
        speak("Sorry boss, I didn't hear you clearly. Please try again.")
        result = "Empty command"
    else:
        action = open_anything(cmd)
        if action:
            speak(f"Done boss. {action}.")
            result = action
        else:
            # Jarvis-style intelligent echo
            speak(f"Understood boss. You asked me to {cmd}. I'll note that down.")
            pyautogui.write(cmd)
            result = f"Echo: {cmd}"

    latency = time.time() - start_time
    log_action(cmd, action or "echo", result)
    print(f"Latency: {latency:.2f}s | {result}")
    speak("Anything else I can help you with, boss?")

# Score function (same as before)
def calculate_agent_score(num_tests=3):
    # ... (keep the same score function from previous code)
    pass   # I'll keep it short here, use previous one

# Listener & Main (same as before)
def on_press(key):
    try:
        if key == pynput_keyboard.Key.caps_lock:
            speak("Yes boss?")
            cmd = listen()
            if cmd:
                threading.Thread(target=process_command, args=(cmd,), daemon=True).start()
    except:
        pass

if __name__ == "__main__":
    speak("Sana is ready, sir")
    print("Sana AI Agent - Jarvis Mode")
    print("Press Caps Lock to speak. Ctrl+C to exit.")

    running = True
    def shutdown():
        global running
        running = False
        speak("Goodbye boss. Have a great day.")
    import signal
    def sig_handler(sig, frame):
        shutdown()
        import sys
        sys.exit(0)
    signal.signal(signal.SIGINT, sig_handler)

    try:
        with pynput_keyboard.Listener(on_press=on_press) as listener:
            while running:
                time.sleep(0.5)
    except KeyboardInterrupt:
        shutdown()