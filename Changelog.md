# Changelog — Sana AI

All notable changes to this project are documented here.  
Format: [version] — date — what changed / what's unchanged.

---

## [1.1.0] — September 2026 — First Run Release

### Added
- **Startup announcement**: TTS + stdout welcome message with version number on every launch
- **Microphone check**: `sounddevice` device detection and test-stream on startup; device name confirmed via TTS
- **CapsLock guidance**: trigger instruction delivered on first launch ("Press CapsLock to speak your command")
- **First-command timeout**: if CapsLock is held 5 seconds with no speech, a guidance prompt fires ("Hold CapsLock and speak clearly")
- **Success confirmation**: spoken intent type on first successful command ("Got it — Informational command received")
- **Error recovery**: mic failure now delivers a plain-language recovery message — no raw Python traceback shown to user
- **Activation event**: `sana_first_command_success` logged to `sana_log.txt` (local only, zero network)
- **config.yaml**: all settings annotated with inline plain-English comments
- **CHANGELOG.md**: this file
- **Version string**: `v1.1.0` in startup banner and spoken welcome
- **setup.py**: one-command installer that creates venv and installs requirements
- **Toggle mode**: CapsLock now works as press-on / press-off (configurable to hold mode)
- **Real-time streaming mic**: replaced fixed-duration `sd.rec()` with `sd.InputStream` callback for true streaming capture
- **Thread-safe TTS**: `_tts_lock` prevents pyttsx3 re-entrancy crashes
- **SQLite session log**: every command, intent, result, and latency written to `mydata.db`
- **Performance scorer**: `run_performance_score()` — accuracy + latency → score /10 000

### Changed
- Startup: app now announces itself instead of starting silently
- Mic failure: user-facing recovery message instead of unhandled `PortAudioError` traceback
- `handle_query()`: restructured as a proper intent router with separate handlers for DateTime, Mathematical, and Informational intents
- App launcher: uses `subprocess.Popen` for direct OS calls before falling back to Win+S search

### Unchanged (intentionally)
- Whisper tiny.en inference pipeline
- VAD logic and thresholds
- NLP intent classification logic (Mathematical / Informational / Operational)
- Sympy math engine
- Wikipedia API integration
- pyttsx3 TTS engine
- 100% offline architecture — zero external API calls during operation
- ~99% recognition accuracy benchmark
- <2s P95 latency benchmark

---

## [1.0.0] — 2025 — Initial Release

- Core voice assistant: CapsLock trigger, Whisper STT, intent classification
- Offline-first: zero external API calls during voice processing
- Sympy math engine, Wikipedia lookup, OS action dispatch (open apps, dictate text)
- Windows-only; requires Python 3.11+
- Fixed-duration audio capture (1.5 s default)
- SQLite logging (basic)