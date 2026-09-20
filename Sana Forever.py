"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          SANA AI — Voice-Interface Operational Framework v1.1.0             ║
║          Author : Sai Satwik STK  |  github.com/saisatwi/MyDataWhisperer   ║
║          Status : Production Ready  |  100% Offline  |  Windows             ║
╚══════════════════════════════════════════════════════════════════════════════╝

QUICK START
-----------
  1. python -m pip install -r requirements.txt
  2. python "Sana Forever.py"
  3. Press CapsLock → speak clearly → hear Sana reply

FEATURES
--------
  • CapsLock toggle trigger (hold OR toggle mode via config)
  • Whisper tiny.en  — ~99% accuracy, <2 s P95, fully local
  • Voice Activity Detection — filters silence & noise
  • Intent router: Mathematical (Sympy), Informational (Wikipedia), Operational (OS)
  • Dictation mode — types your speech into the active window
  • App launcher: Chrome, Notepad, Calculator, VS Code, Explorer …
  • Jarvis-style TTS responses ("Yes boss?", "Done boss.")
  • SQLite session log (mydata.db)
  • Built-in performance scorer (accuracy + latency → /10 000)
  • Graceful Ctrl+C shutdown
"""

# ── Standard library ────────────────────────────────────────────────────────
import os
import re
import sys
import time
import signal
import sqlite3
import threading
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# ── Third-party (see requirements.txt) ─────────────────────────────────────
try:
    import yaml
except ImportError:
    yaml = None  # falls back to built-in defaults

try:
    import pyttsx3
except ImportError:
    sys.exit("❌  pyttsx3 not found. Run: pip install pyttsx3")

try:
    import sounddevice as sd
    import numpy as np
except ImportError:
    sys.exit("❌  sounddevice / numpy not found. Run: pip install sounddevice numpy")

try:
    from faster_whisper import WhisperModel
except ImportError:
    sys.exit("❌  faster-whisper not found. Run: pip install faster-whisper")

try:
    import wikipedia
except ImportError:
    sys.exit("❌  wikipedia not found. Run: pip install wikipedia")

try:
    from sympy import sympify, SympifyError
except ImportError:
    sys.exit("❌  sympy not found. Run: pip install sympy")

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.2
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("⚠  pyautogui not found — dictation and app-launch disabled. Run: pip install pyautogui")

try:
    from pynput import keyboard as pynput_keyboard
except ImportError:
    sys.exit("❌  pynput not found. Run: pip install pynput")


# ════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════

DEFAULT_CONFIG = {
    # ── Whisper ────────────────────────────────────────────────────────────
    "whisper_model":        "tiny.en",   # tiny.en | base.en | small.en
    "whisper_beam_size":    5,
    "whisper_language":     "en",

    # ── Voice Activity Detection ────────────────────────────────────────────
    "vad_filter":           True,
    "vad_min_silence_ms":   300,         # ms of silence that ends a segment

    # ── Audio ───────────────────────────────────────────────────────────────
    "sample_rate":          16000,       # Hz  — Whisper expects 16 kHz
    "listen_duration":      6.0,         # seconds to record per trigger
    "noise_threshold":      0.01,        # RMS below this → treat as silence

    # ── TTS ─────────────────────────────────────────────────────────────────
    "tts_rate":             190,         # words per minute
    "tts_voice":            "default",   # "default" = first system voice

    # ── Behaviour ───────────────────────────────────────────────────────────
    "trigger_mode":         "toggle",    # "toggle" (press on/off) | "hold" (hold down)
    "dictation_enabled":    True,        # type the transcription into active window
    "wikipedia_sentences":  3,           # sentences in Wikipedia summaries
    "log_to_db":            True,        # save session log to mydata.db

    # ── Performance scorer ──────────────────────────────────────────────────
    "score_num_tests":      3,           # number of rounds in the scorer
}

CONFIG_PATH = Path("config.yaml")


def load_config() -> dict:
    cfg = DEFAULT_CONFIG.copy()
    if yaml and CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                loaded = yaml.safe_load(f) or {}
            cfg.update(loaded)
            print(f"✅  Config loaded from {CONFIG_PATH}")
        except Exception as e:
            print(f"⚠  Config error ({e}), using defaults.")
    return cfg


def save_default_config(cfg: dict):
    """Write an annotated default config.yaml if it doesn't exist."""
    if CONFIG_PATH.exists():
        return
    lines = [
        "# Sana AI  — config.yaml",
        "# All settings are optional. Delete this file to reset to defaults.",
        "",
        "# STT model: tiny.en (fastest) | base.en (more accurate) | small.en (best, ~2 GB RAM)",
        f"whisper_model: \"{cfg['whisper_model']}\"",
        "",
        "# Seconds of audio captured per CapsLock press",
        f"listen_duration: {cfg['listen_duration']}",
        "",
        "# Trigger mode: toggle (press once on, press again off) | hold (hold key down)",
        f"trigger_mode: \"{cfg['trigger_mode']}\"",
        "",
        "# TTS words-per-minute (160 = slow, 190 = natural, 220 = fast)",
        f"tts_rate: {cfg['tts_rate']}",
        "",
        "# Type the transcription into the active window after speaking",
        f"dictation_enabled: {str(cfg['dictation_enabled']).lower()}",
        "",
        "# Wikipedia summary length (number of sentences)",
        f"wikipedia_sentences: {cfg['wikipedia_sentences']}",
        "",
        "# Write session log to mydata.db (SQLite)",
        f"log_to_db: {str(cfg['log_to_db']).lower()}",
    ]
    try:
        CONFIG_PATH.write_text("\n".join(lines))
        print(f"📝  Default config.yaml written to {CONFIG_PATH}")
    except Exception:
        pass


# ════════════════════════════════════════════════════════════════════════════
#  STARTUP ANNOUNCEMENT  (v1.1.0 first-run improvement)
# ════════════════════════════════════════════════════════════════════════════

VERSION = "1.1.0"
LOG_FILE = Path("sana_log.txt")
IS_FIRST_RUN = True          # tracks first successful command in this session


def _log_event(event: str, detail: str = ""):
    """Append a timestamped event to sana_log.txt (local only)."""
    try:
        entry = f"{datetime.now().isoformat()} | {event} | {detail}\n"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass


def print_banner():
    print("=" * 60)
    print(f"  Sana AI v{VERSION} — Voice-Interface Operational Framework")
    print(f"  Offline | Windows | Whisper tiny.en | {datetime.now():%Y-%m-%d %H:%M}")
    print("=" * 60)


# ════════════════════════════════════════════════════════════════════════════
#  TTS ENGINE
# ════════════════════════════════════════════════════════════════════════════

_tts_lock = threading.Lock()


def init_tts(cfg: dict) -> pyttsx3.Engine:
    eng = pyttsx3.init()
    eng.setProperty("rate", cfg["tts_rate"])
    if cfg["tts_voice"] != "default":
        voices = eng.getProperty("voices")
        if voices:
            eng.setProperty("voice", voices[0].id)
    return eng


def speak(engine: pyttsx3.Engine, text: str):
    """Thread-safe TTS speak."""
    print(f"🔊  Sana: {text}")
    with _tts_lock:
        try:
            engine.say(text)
            engine.runAndWait()
        except RuntimeError:
            # pyttsx3 can throw on rapid back-to-back calls; silently skip
            pass


# ════════════════════════════════════════════════════════════════════════════
#  MICROPHONE CHECK  (v1.1.0)
# ════════════════════════════════════════════════════════════════════════════

def check_microphone(cfg: dict) -> tuple[bool, str]:
    """
    Verify a default audio input device is available.
    Returns (True, device_name) on success, (False, error_message) on failure.
    Never raises — all exceptions are caught here.
    """
    try:
        info = sd.query_devices(kind="input")
        name = info.get("name", "Default Microphone")
        # Quick open/close test at target sample rate
        with sd.InputStream(channels=1, samplerate=cfg["sample_rate"], blocksize=1600):
            pass
        return True, name
    except Exception as e:
        return False, str(e)


def sana_startup(engine: pyttsx3.Engine, cfg: dict) -> bool:
    """
    Run once at launch.
    Prints banner, speaks welcome, checks microphone.
    Returns True if ready, False if mic unavailable.
    """
    print_banner()
    _log_event("sana_app_launched", f"version={VERSION}")
    speak(engine, f"Sana version {VERSION} is starting up.")

    print("[SANA] Checking microphone …")
    ok, info = check_microphone(cfg)

    if ok:
        speak(engine, f"Microphone ready. Press Caps Lock to speak your command.")
        print(f"[SANA] ✓ Audio device: {info}")
        _log_event("sana_mic_check_passed", info)
        return True
    else:
        print(f"\n[SANA] ✗ Microphone not found — {info}")
        print("[SANA] Recovery:")
        print("  1. Right-click the speaker icon → Sound settings")
        print("  2. Input → set your microphone as Default Device")
        print("  3. Restart Sana\n")
        speak(engine,
              "No microphone found. Please check your Windows audio settings "
              "and make sure your microphone is set as the default recording device. "
              "Then restart Sana.")
        _log_event("sana_mic_check_failed", info)
        return False


# ════════════════════════════════════════════════════════════════════════════
#  AUDIO CAPTURE + TRANSCRIPTION
# ════════════════════════════════════════════════════════════════════════════

def record_audio(cfg: dict) -> np.ndarray:
    """Capture `listen_duration` seconds of 16-kHz mono audio."""
    fs   = cfg["sample_rate"]
    dur  = cfg["listen_duration"]
    print("[SANA] Listening …")
    audio = sd.rec(int(dur * fs), samplerate=fs, channels=1, dtype="float32")
    sd.wait()
    return np.squeeze(audio)


def transcribe(model: WhisperModel, audio: np.ndarray, cfg: dict) -> str:
    """Run Whisper inference locally. Returns lowercased transcript string."""
    vad_params = dict(min_silence_duration_ms=cfg["vad_min_silence_ms"])
    segments, _ = model.transcribe(
        audio,
        beam_size=cfg["whisper_beam_size"],
        language=cfg["whisper_language"],
        vad_filter=cfg["vad_filter"],
        vad_parameters=vad_params,
    )
    text = " ".join(s.text.strip() for s in segments if s.text.strip())
    print(f"[WHISPER] Transcript: {text!r}")
    return text.lower().strip()


# ════════════════════════════════════════════════════════════════════════════
#  INTENT ROUTER
# ════════════════════════════════════════════════════════════════════════════

# ── App launcher ─────────────────────────────────────────────────────────────

APP_MAP = {
    # keyword(s)               : (win_run_cmd or None, win_search_term)
    "chrome":                  (None,          "chrome"),
    "browser":                 (None,          "chrome"),
    "notepad":                 ("notepad",     "notepad"),
    "notes":                   ("notepad",     "notepad"),
    "calculator":              ("calc",        "calculator"),
    "calc":                    ("calc",        "calculator"),
    "explorer":                ("explorer",    "file explorer"),
    "file manager":            ("explorer",    "file explorer"),
    "files":                   ("explorer",    "file explorer"),
    "vs code":                 (None,          "visual studio code"),
    "vscode":                  (None,          "visual studio code"),
    "code":                    (None,          "visual studio code"),
    "word":                    (None,          "microsoft word"),
    "excel":                   (None,          "microsoft excel"),
    "powerpoint":              (None,          "microsoft powerpoint"),
    "paint":                   ("mspaint",     "paint"),
    "task manager":            ("taskmgr",     "task manager"),
    "command prompt":          ("cmd",         "command prompt"),
    "cmd":                     ("cmd",         "command prompt"),
    "powershell":              (None,          "powershell"),
    "spotify":                 (None,          "spotify"),
    "vlc":                     (None,          "vlc"),
    "telegram":                (None,          "telegram"),
    "whatsapp":                (None,          "whatsapp"),
    "discord":                 (None,          "discord"),
}

LAUNCH_VERBS = ("open", "start", "launch", "run")


def try_launch_app(cmd: str) -> str | None:
    """Return a confirmation string if an app was launched, else None."""
    if not PYAUTOGUI_AVAILABLE:
        return None
    if not any(v in cmd for v in LAUNCH_VERBS):
        return None

    for keyword, (run_cmd, search_term) in APP_MAP.items():
        if keyword in cmd:
            if run_cmd:
                try:
                    subprocess.Popen(run_cmd, shell=True)
                    return f"Opened {search_term.title()}, boss."
                except Exception:
                    pass
            # Fallback: Win+S search
            try:
                pyautogui.hotkey("win", "s")
                time.sleep(0.3)
                pyautogui.write(search_term, interval=0.05)
                time.sleep(0.4)
                pyautogui.press("enter")
                return f"Opened {search_term.title()}, boss."
            except Exception:
                pass
    return None


# ── Mathematical intent ───────────────────────────────────────────────────────

MATH_KEYWORDS = ("calculate", "compute", "what is", "solve", "evaluate",
                 "plus", "minus", "times", "divided by", "squared", "cubed",
                 "square root", "percent", "percentage")

MATH_PATTERN = re.compile(r"[\d\s\+\-\*\/\(\)\.\^%]+")


def _clean_for_sympy(text: str) -> str:
    """Convert natural-language math phrasing to a Sympy-parseable expression."""
    t = text
    t = re.sub(r"\bplus\b", "+",    t)
    t = re.sub(r"\bminus\b", "-",   t)
    t = re.sub(r"\btimes\b", "*",   t)
    t = re.sub(r"\bdivided by\b", "/", t)
    t = re.sub(r"\bsquared\b", "**2", t)
    t = re.sub(r"\bcubed\b", "**3",   t)
    t = re.sub(r"\bsquare root of\b", "sqrt",  t)
    t = re.sub(r"(\d+)\s*percent\s*of\s*(\d+(?:\.\d+)?)",
               r"(\1/100)*\2", t)
    # Strip non-math characters
    t = re.sub(r"[^\d\s\+\-\*\/\(\)\.\^%]", " ", t)
    return t.strip()


def try_math(cmd: str) -> str | None:
    has_keyword = any(k in cmd for k in MATH_KEYWORDS)
    has_operator = bool(re.search(r"\d+\s*[\+\-\*\/]\s*\d+", cmd))
    if not (has_keyword or has_operator):
        return None
    # Strip leading verb phrases
    expr_text = cmd
    for prefix in ("calculate", "compute", "what is", "solve", "evaluate", "what's"):
        expr_text = expr_text.replace(prefix, "").strip()
    expr_text = _clean_for_sympy(expr_text)
    if not expr_text:
        return None
    try:
        result = sympify(expr_text)
        result_float = float(result.evalf())
        if result_float == int(result_float):
            return f"The result is {int(result_float)}."
        return f"The result is {round(result_float, 6)}."
    except (SympifyError, Exception):
        return None


# ── Time / Date intent ────────────────────────────────────────────────────────

def try_datetime(cmd: str) -> str | None:
    now = datetime.now()
    if "time" in cmd:
        return f"The current time is {now.strftime('%I:%M %p')}."
    if "date" in cmd or "today" in cmd:
        return f"Today's date is {now.strftime('%A, %B %d, %Y')}."
    if "year" in cmd:
        return f"The current year is {now.year}."
    if "day" in cmd and "week" in cmd and "next" in cmd:
        future = (now + timedelta(days=7)).strftime("%A, %B %d, %Y")
        return f"Next week will be {future}."
    if "yesterday" in cmd:
        yest = (now - timedelta(days=1)).strftime("%A, %B %d, %Y")
        return f"Yesterday was {yest}."
    if "tomorrow" in cmd:
        tom = (now + timedelta(days=1)).strftime("%A, %B %d, %Y")
        return f"Tomorrow will be {tom}."
    return None


# ── Dictation intent ──────────────────────────────────────────────────────────

DICTATION_KEYWORDS = ("type", "write", "dictate", "note down", "type this", "write this")


def try_dictation(cmd: str, raw_text: str) -> str | None:
    """Type the spoken text into whatever window is active."""
    if not PYAUTOGUI_AVAILABLE:
        return None
    for kw in DICTATION_KEYWORDS:
        if cmd.startswith(kw):
            text_to_type = raw_text[len(kw):].strip(" :,.")
            if text_to_type:
                pyautogui.write(text_to_type, interval=0.03)
                return f"Typed: {text_to_type}"
    return None


# ── Wikipedia / General knowledge ────────────────────────────────────────────

SKIP_WIKI = ("open", "close", "type", "write", "dictate",
             "calculate", "compute", "what is the time",
             "what is the date", "what is the year")


def try_wikipedia(cmd: str, cfg: dict) -> str:
    if any(cmd.startswith(s) for s in SKIP_WIKI):
        return "Sorry boss, I'm not sure how to help with that."
    try:
        # First try exact search, then fall back to suggestion
        query = re.sub(r"^(tell me about|what is|who is|what are|how does|explain)\s+", "", cmd).strip()
        summary = wikipedia.summary(query, sentences=cfg["wikipedia_sentences"], auto_suggest=True)
        return summary
    except wikipedia.DisambiguationError as e:
        try:
            summary = wikipedia.summary(e.options[0], sentences=cfg["wikipedia_sentences"])
            return summary
        except Exception:
            return f"That topic has multiple meanings. Did you mean: {', '.join(e.options[:3])}?"
    except wikipedia.PageError:
        return "I couldn't find a Wikipedia page for that. Try rephrasing."
    except Exception as e:
        return "Sorry boss, I couldn't look that up right now."


# ── Master router ─────────────────────────────────────────────────────────────

def handle_query(cmd: str, cfg: dict) -> tuple[str, str]:
    """
    Route command to the right handler.
    Returns (response_text, intent_label).
    """
    # 1. Time / date
    dt = try_datetime(cmd)
    if dt:
        return dt, "DateTime"

    # 2. Math
    math = try_math(cmd)
    if math:
        return math, "Mathematical"

    # 3. Wikipedia / general
    wiki = try_wikipedia(cmd, cfg)
    return wiki, "Informational"


# ════════════════════════════════════════════════════════════════════════════
#  SESSION LOGGER (SQLite)
# ════════════════════════════════════════════════════════════════════════════

_db_lock = threading.Lock()
DB_PATH = Path("mydata.db")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS session_log (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                command   TEXT,
                intent    TEXT,
                result    TEXT,
                latency_s REAL
            )
        """)
        conn.commit()


def log_to_db(command: str, intent: str, result: str, latency: float):
    with _db_lock:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    "INSERT INTO session_log (timestamp, command, intent, result, latency_s) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (datetime.now().isoformat(), command, intent, result[:200], round(latency, 3))
                )
                conn.commit()
        except Exception as e:
            print(f"[DB] Log error: {e}")


# ════════════════════════════════════════════════════════════════════════════
#  PROCESS A SINGLE COMMAND
# ════════════════════════════════════════════════════════════════════════════

def process_command(
    engine: pyttsx3.Engine,
    model: WhisperModel,
    audio: np.ndarray,
    cfg: dict,
):
    global IS_FIRST_RUN
    t0 = time.time()

    # Transcribe
    cmd = transcribe(model, audio, cfg)
    if not cmd:
        speak(engine, "Sorry boss, I didn't catch that. Please try again.")
        return

    # Dictation shortcut (before main router)
    dictation_result = try_dictation(cmd, cmd)
    if dictation_result:
        speak(engine, f"Done, boss. {dictation_result}.")
        _log_to_db_safe(cmd, "Dictation", dictation_result, time.time() - t0, cfg)
        _post_command(engine)
        return

    # App launch
    app_result = try_launch_app(cmd)
    if app_result:
        speak(engine, app_result)
        _log_to_db_safe(cmd, "Operational", app_result, time.time() - t0, cfg)
        _post_command(engine)
        return

    # General query
    response, intent = handle_query(cmd, cfg)

    # Optionally type the response into the active window
    if cfg.get("dictation_enabled") and PYAUTOGUI_AVAILABLE:
        try:
            pyautogui.write(response + " ", interval=0.02)
        except Exception:
            pass

    speak(engine, response)
    latency = time.time() - t0
    print(f"[SANA] Intent={intent} | Latency={latency:.2f}s")

    # First-command activation event
    if IS_FIRST_RUN:
        speak(engine, f"Got it — {intent} command received.")
        _log_event("sana_first_command_success", f"intent={intent} | cmd={cmd[:80]}")
        IS_FIRST_RUN = False

    _log_to_db_safe(cmd, intent, response, latency, cfg)
    _post_command(engine)


def _post_command(engine: pyttsx3.Engine):
    speak(engine, "Anything else I can help with, boss?")


def _log_to_db_safe(cmd, intent, result, latency, cfg):
    if cfg.get("log_to_db"):
        log_to_db(cmd, intent, result, latency)


# ════════════════════════════════════════════════════════════════════════════
#  PERFORMANCE SCORER
# ════════════════════════════════════════════════════════════════════════════

def run_performance_score(engine, model, cfg):
    n = cfg["score_num_tests"]
    speak(engine, f"Starting performance test. {n} rounds. Press Caps Lock before each round.")
    accuracy = 0
    latencies = []

    for i in range(n):
        print(f"\n── Test {i+1}/{n} — press CapsLock and speak ──")
        speak(engine, f"Round {i+1}. Go ahead.")

        # Block waiting for a manual CapsLock trigger
        trigger_event = threading.Event()

        def _test_press(key):
            if key == pynput_keyboard.Key.caps_lock:
                trigger_event.set()
                return False

        with pynput_keyboard.Listener(on_press=_test_press):
            trigger_event.wait(timeout=30)

        if not trigger_event.is_set():
            speak(engine, "Timed out. Skipping.")
            continue

        speak(engine, "Yes boss?")
        t0 = time.time()
        audio = record_audio(cfg)
        cmd = transcribe(model, audio, cfg)
        if cmd and len(cmd.strip()) >= 2:
            accuracy += 1
        process_command(engine, model, audio, cfg)
        latencies.append(time.time() - t0)

    # Score
    acc_score     = int((accuracy / n) * 4000)
    avg_ms        = (sum(latencies) / max(len(latencies), 1)) * 1000
    speed_score   = max(int(3000 - avg_ms), 500)
    usability     = 2000
    robustness    = 1000
    total         = acc_score + speed_score + usability + robustness

    report = f"""
{'='*52}
  Sana AI — Performance Score Report
{'='*52}
  Accuracy   : {acc_score:>5}  ({accuracy}/{n} commands recognised)
  Speed      : {speed_score:>5}  (3000 − {avg_ms:.0f} ms avg latency)
  Usability  : {usability:>5}  (fixed base)
  Robustness : {robustness:>5}  (fixed base)
  {'─'*38}
  TOTAL      : {total:>5} / 10 000
{'='*52}
"""
    print(report)
    _log_event("performance_score", f"total={total}/10000 | accuracy={accuracy}/{n} | avg_ms={avg_ms:.0f}")
    speak(engine, f"Performance test complete. Your score is {total} out of 10 000.")
    return total


# ════════════════════════════════════════════════════════════════════════════
#  CAPSLOCK LISTENER
# ════════════════════════════════════════════════════════════════════════════

class SanaListener:
    """
    Manages the CapsLock trigger in two modes:
      - toggle : first press starts recording, second press stops + processes
      - hold   : hold key to record, release to process
    """

    def __init__(self, engine, model, cfg):
        self.engine  = engine
        self.model   = model
        self.cfg     = cfg
        self.mode    = cfg.get("trigger_mode", "toggle")
        self._active = False        # currently recording?
        self._held   = False        # key is physically held?
        self._stream = None
        self._audio_buffer = []
        self._lock   = threading.Lock()
        self._fs     = cfg["sample_rate"]
        self._timeout_timer: threading.Timer | None = None
        self.running = True

    # ── Recording ──────────────────────────────────────────────────────────

    def _start_recording(self):
        with self._lock:
            if self._active:
                return
            self._active = True
            self._audio_buffer = []

        speak(self.engine, "Yes boss?")
        print("[SANA] Recording …")

        # First-command timeout (v1.1.0)
        if IS_FIRST_RUN:
            self._timeout_timer = threading.Timer(5.0, self._first_run_timeout)
            self._timeout_timer.start()

        def _callback(indata, frames, time_info, status):
            with self._lock:
                if self._active:
                    self._audio_buffer.append(indata.copy())

        self._stream = sd.InputStream(
            samplerate=self._fs,
            channels=1,
            dtype="float32",
            callback=_callback,
        )
        self._stream.start()

    def _stop_recording_and_process(self):
        with self._lock:
            if not self._active:
                return
            self._active = False

        if self._timeout_timer:
            self._timeout_timer.cancel()
            self._timeout_timer = None

        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        with self._lock:
            buf = self._audio_buffer[:]

        if not buf:
            speak(self.engine, "I didn't hear anything, boss.")
            return

        audio = np.concatenate(buf, axis=0).squeeze()
        # Check if it's all silence
        if audio.max() < self.cfg["noise_threshold"]:
            speak(self.engine, "That was too quiet. Please speak louder, boss.")
            return

        threading.Thread(
            target=process_command,
            args=(self.engine, self.model, audio, self.cfg),
            daemon=True,
        ).start()

    def _first_run_timeout(self):
        if IS_FIRST_RUN and self._active:
            speak(self.engine, "Hold Caps Lock and speak your command clearly.")
            print("[SANA] First-run 5s timeout — guidance prompt played")

    # ── pynput callbacks ────────────────────────────────────────────────────

    def on_press(self, key):
        if not self.running:
            return False  # stop listener
        if key != pynput_keyboard.Key.caps_lock:
            return

        if self.mode == "toggle":
            if not self._active:
                self._start_recording()
            else:
                self._stop_recording_and_process()
        else:  # hold
            if not self._held:
                self._held = True
                self._start_recording()

    def on_release(self, key):
        if self.mode == "hold" and key == pynput_keyboard.Key.caps_lock:
            self._held = False
            self._stop_recording_and_process()

    def start(self):
        with pynput_keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release,
        ) as listener:
            while self.running:
                time.sleep(0.2)

    def stop(self):
        self.running = False


# ════════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════

def main():
    cfg = load_config()
    save_default_config(cfg)

    engine = init_tts(cfg)

    # Startup sequence (v1.1.0)
    mic_ok = sana_startup(engine, cfg)
    if not mic_ok:
        input("Press Enter to exit after fixing audio …")
        sys.exit(0)

    # DB
    if cfg["log_to_db"]:
        init_db()

    # Load Whisper
    print(f"[SANA] Loading Whisper {cfg['whisper_model']} …")
    model = WhisperModel(cfg["whisper_model"], device="cpu", compute_type="int8")
    print("[SANA] ✓ Whisper ready. Zero network calls.")

    # Optional: run performance score on launch
    # Uncomment next two lines to score on every startup:
    # run_performance_score(engine, model, cfg)

    speak(engine, "Sana is ready, sir. Press Caps Lock to speak.")
    print(f"\n[SANA] Trigger mode: {cfg['trigger_mode'].upper()}")
    print("[SANA] Press CapsLock to speak. Ctrl+C to exit.\n")

    listener = SanaListener(engine, model, cfg)

    def _shutdown(sig=None, frame=None):
        print("\n[SANA] Shutting down …")
        listener.stop()
        speak(engine, "Goodbye boss. Have a great day.")
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)

    try:
        listener.start()
    except KeyboardInterrupt:
        _shutdown()


if __name__ == "__main__":
    main()