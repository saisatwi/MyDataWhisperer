# 🎙️ SANA – AI Voice Assistant

A lightweight desktop voice assistant built with Python that supports:

✔ Voice wake-up
✔ Speech-to-text (Whisper)
✔ Fuzzy command matching
✔ App launching
✔ Text-to-speech replies
✔ Windows automation

🚀 Features
1️⃣ Voice Activation

Press Caps Lock to trigger SANA

Windows API captures the event

Immediately calls jarvis() function

Sana responds: “Yes boss?”

2️⃣ Audio Recording (3 seconds)

Uses sounddevice

Captures 16 kHz WAV

Stored temporarily before sending to Whisper

3️⃣ Whisper Speech-to-Text

Uses faster-whisper

Converts your speech into text

Supports accents & noisy environments

4️⃣ Fuzzy Command Matching

Cleans transcripts

Uses:

difflib.get_close_matches

Dynamic keyword matching

Extremely accurate for:

"Open Chrome"

"Start Notepad"

“Launch Visual Studio Code”

etc.

5️⃣ App Launcher

Uses PyAutoGUI to simulate:

Windows Key

Typing application name

Pressing Enter

6️⃣ Sana Speaks Back

Text-to-speech (pyttsx3)

Confirms actions like:

“Opening Chrome”

“Launching Notepad”