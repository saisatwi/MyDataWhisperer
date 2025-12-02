🎙️ MyDataWhisperer — AI Voice Assistant for Windows

MyDataWhisperer is a Python-based desktop voice assistant that combines AI, machine learning, and automation to make interacting with your computer effortless. By pressing Caps Lock, the assistant wakes instantly, listens to your voice, transcribes your command using Whisper, and executes tasks like opening applications, automating workflows, or providing audible confirmation via text-to-speech. With fuzzy matching for commands and a lightweight local database to log actions, MyDataWhisperer creates a seamless, responsive, and intelligent desktop experience.

This project demonstrates a full-stack approach to AI-driven automation. It showcases practical skills in Python scripting, speech-to-text (Whisper), text-to-speech (pyttsx3), automation with PyAutoGUI, audio processing (sounddevice, numpy, scipy), configuration handling (PyYAML), and local data management. The assistant is designed to handle imprecise speech gracefully and provide instant feedback, highlighting both natural language processing and interactive automation capabilities.

⚡ Installation & Setup

To get started:

# Clone the repository
git clone https://github.com/saisatwi/sana-voice-assistant.git
cd MyDataWhisperer

# Create a virtual environment
python -m venv venv

# Activate the environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install required packages
pip install -r requirements.txt


Required packages include: pyttsx3, sounddevice, faster-whisper, PyAutoGUI, PyYAML, numpy, scipy. These libraries handle AI transcription, audio input/output, automation, and configuration.

▶️ Running the Assistant

Option 1 — Python Script:

python sana_forever.py


Option 2 — Background Batch Run (Windows):

Double-click sana_forever.bat

Press Caps Lock anytime to activate MyDataWhisperer

Once activated, the assistant listens, interprets your commands, executes actions, and confirms results via voice, providing a fully interactive experience.

🎯 Why This Project Matters

Demonstrates AI/ML integration with Whisper ASR

Shows Python automation and scripting expertise

Highlights NLP and fuzzy matching capabilities

Includes configurable system architecture and data logging

Relevant for roles like AI/ML Engineer, Python Developer, Data Engineer, Automation Engineer

Project structure:

MyDataWhisperer/
│
├── config.yaml            # Configuration settings
├── sana_forever.py        # Main script
├── sana_forever.bat       # Batch file for Windows background run
├── requirements.txt       # Python dependencies
├── mydatadb/              # Local database folder
│   ├── app_list.json
│   └── logs.txt
└── README.md              # Project documentation
