import os
import subprocess
import time
import pyautogui
import pyttsx3
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
from faster_whisper import WhisperModel
import threading
import ctypes
from ctypes import wintypes
import difflib


# ========================= WINDOWS API SETUP =========================
user32 = ctypes.WinDLL('user32', use_last_error=True)
GetKeyState = user32.GetKeyState
GetKeyState.argtypes = [wintypes.INT]
GetKeyState.restype = wintypes.SHORT


# ========================= LOAD MODELS =========================
print("Loading models... please wait")
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('volume', 0.95)


def speak(text):
    print(f"\nSANA: {text}")
    engine.say(text)
    engine.runAndWait()


# ========================= VOICE INPUT =========================
def listen():
    speak("Speak now")
    print("Listening for 3 seconds...")

    try:
        audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1, dtype='int16')
        sd.wait()
        audio = audio.flatten()

        temp_wav = os.path.join(os.getenv('TEMP'), 'sana_voice.wav')
        wavfile.write(temp_wav, 16000, audio)

        segments, _ = whisper_model.transcribe(temp_wav)
        text = " ".join(seg.text for seg in segments).strip().lower()

        try:
            os.remove(temp_wav)
        except:
            pass

        if text:
            print(f"You: {text}")
            return text

    except Exception as e:
        print("Audio error:", e)

    return ""


# ========================= UNIVERSAL COMMAND HANDLER =========================

def clean(text):
    """Normalize voice text for better matching."""
    return text.replace(" ", "").replace(".", "").replace(",", "").replace("-", "").strip()


def open_anything(voice):
    """Universal fuzzy opening system."""

    apps = {
        "chrome": "chrome",
        "googlechrome": "chrome",
        "browser": "chrome",
        "google": "chrome",

        "edge": "msedge",
        "microsoftedge": "msedge",

        "notepad": "notepad",
        "texteditor": "notepad",

        "calculator": "calc",
        "calc": "calc",

        "excel": "excel",
        "spreadsheet": "excel",

        "word": "winword",

        "powerpoint": "powerpnt",
        "ppt": "powerpnt",

        "vs": "code",
        "vscode": "code",
        "visualstudio": "code",
        "code": "code",

        "cmd": "cmd",
        "terminal": "cmd",
    }

    v = clean(voice)

    # 1. Exact or fuzzy match for apps
    best = difflib.get_close_matches(v, list(apps.keys()), n=1, cutoff=0.45)
    if best:
        app = apps[best[0]]
        pyautogui.hotkey("win")
        time.sleep(0.3)
        pyautogui.write(app)
        pyautogui.press("enter")
        speak(f"Opening {best[0]}")
        return

    # 2. Try opening as website
    if "open" in voice:
        parts = voice.split()
        if len(parts) >= 2:
            site = parts[-1].replace(".", "")
            url = f"https://{site}.com"
            os.startfile(url)
            speak(f"Opening website {site}")
            return

    # 3. Try opening folders
    if "folder" in voice or "directory" in voice:
        speak("Which folder name?")
        folder = listen().lower()
        base = os.path.expanduser("~")
        for root, dirs, files in os.walk(base):
            for d in dirs:
                if folder in d.lower():
                    os.startfile(os.path.join(root, d))
                    speak(f"Opening folder {d}")
                    return

    # 4. If still nothing -> treat as text
    pyautogui.write(f"SANA heard: {voice}")
    speak("Command processed")


# ========================= MAIN JARVIS FUNCTION =========================
def jarvis():
    speak("Yes boss?")
    cmd = listen()

    if not cmd:
        speak("Did not hear you properly")
        return

    if "open" in cmd or "start" in cmd or "launch" in cmd:
        open_anything(cmd)
    else:
        pyautogui.write(f"You said: {cmd}")
        speak("Done")


# ========================= START OLLAMA =========================
print("Starting Ollama server...")
try:
    subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
except:
    print("Ollama not found, skipping...")

time.sleep(5)
print("SANA is ready.")


speak("Sana is always on. Press Caps Lock anytime.")


# ========================= FOREVER LOOP =========================
was_on = bool(GetKeyState(0x14) & 0x0001)

while True:
    try:
        is_on = bool(GetKeyState(0x14) & 0x0001)

        if is_on and not was_on:
            threading.Thread(target=jarvis, daemon=True).start()

        was_on = is_on
        time.sleep(0.05)

    except:
        time.sleep(0.1)
