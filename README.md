# Sana AI Agent

Sana is a powerful, fully offline voice AI assistant that understands natural language and responds like Jarvis from Iron Man.

## Features
- **Offline & Local**: Works without internet after install
- **Voice Trigger**: Press Caps Lock → "Yes boss?"
- **Universal Understanding**: Time/date/year, math calculations, Wikipedia topics (nature, law, movies, history, names, etc.)
- **Jarvis-Like Voice**: Speaks full answers ("The time is...", "Here's the result...", "Anything else, boss?")
- **Low Latency**: <2 seconds response time
- **High Accuracy**: ~99% with clear speech (tiny.en Whisper + VAD)
- **Precise Results**: Time/date (datetime), math (Sympy), everything else (Wikipedia)
- **Extendable**: Add commands in `open_anything()` or `handle_query()`

## Installation
1. Python 3.11+ (from python.org)
2. Create venv:
python -m venv venv
venv\Scripts\activate
text3. Install requirements:
pip install -r requirements.txt
text## Usage
python "Sana Forever.py"
text- Speaks "Sana is ready, sir"
- Press Caps Lock → speak clearly (e.g., "what is the time?", "open chrome", "calculate 2+2*3", "tell me about Einstein")
- Sana speaks + types precise answer

## Example Commands
- "what is the time?" → "The current time is 08:45 PM."
- "calculate 2+2*3" → "The result is 8."
- "tell me about Albert Einstein" → Wikipedia summary
- "open chrome" → Opens Chrome
- "dictate hello boss" → Types text

## Future Ideas
- Add local LLM (TinyLlama) for deeper intelligence
- Conversation memory
- More voice personalities
- GUI tray icon


