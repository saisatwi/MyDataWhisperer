"""
sana_web.py — Resilient Production Engine with Model Fallbacks & Auto .env Reading
"""

import os
import sys
import time
import json
import ssl
import asyncio
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from aiohttp import web

# Automatically locate and load .env in the same directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

print("\n" + "=" * 65)
print(" 🚀 SANA AI BACKEND ENGINE STARTUP CHECK")
print("=" * 65)
print(f" Loaded .env Path:      {env_path}")
print(f" Groq Key Configured:   {'✅ YES' if GROQ_API_KEY else '❌ NOT DETECTED'}")
print(f" Gemini Key Configured: {'✅ YES' if GEMINI_API_KEY else '❌ NOT DETECTED'}")
print("=" * 65 + "\n")

SYSTEM_PROMPT = "You are Sana, an intelligent, concise, and helpful AI assistant."
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Bypass SSL verification for local environments with custom network/antivirus certificates
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

@web.middleware
async def cors_middleware(request, handler):
    if request.method == "OPTIONS":
        response = web.Response(status=200)
    else:
        try:
            response = await handler(request)
        except web.HTTPException as ex:
            response = ex

    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

def _sync_call_groq(prompt: str) -> str | None:
    if not GROQ_API_KEY:
        return None
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {**DEFAULT_HEADERS, "Authorization": f"Bearer {GROQ_API_KEY}"}
    
    # Active model cascade list
    models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "openai/gpt-oss-20b", "mixtral-8x7b-32768"]
    
    for model in models:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, context=SSL_CONTEXT, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    print(f"✅ [Groq - {model}] Call Successful!")
                    return data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            err = e.read().decode('utf-8')
            print(f"⚠️ [Groq {model} HTTP Error {e.code}]: Attempting next fallback model...")
        except Exception as e:
            print(f"❌ [Groq Connection Error]: {e}")
            
    return None

def _sync_call_gemini(prompt: str) -> str | None:
    if not GEMINI_API_KEY:
        return None
        
    models = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-flash"]
    
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        headers = {**DEFAULT_HEADERS}
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{SYSTEM_PROMPT}\n\nQuestion: {prompt}"}]
                }
            ]
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, context=SSL_CONTEXT, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    print(f"✅ [Gemini - {model}] Call Successful!")
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except urllib.error.HTTPError as e:
            err = e.read().decode('utf-8')
            print(f"⚠️ [Gemini {model} HTTP Error {e.code}]: Attempting next fallback model...")
        except Exception as e:
            print(f"❌ [Gemini Connection Error]: {e}")
            
    return None

async def call_llm(prompt: str) -> str | None:
    # Executes Groq first, falls back to Gemini if Groq fails or rate limits
    handlers = [_sync_call_groq, _sync_call_gemini]
    for handler in handlers:
        res = await asyncio.to_thread(handler, prompt)
        if res:
            return res
    return None

async def handle_index(request):
    return web.FileResponse(Path(__file__).parent / "sana_web.html")

async def handle_time(request):
    now_str = datetime.now().strftime("%I:%M:%S %p | %A, %b %d, %Y")
    return web.json_response({"server_time": now_str})

async def handle_ask(request):
    t0 = time.time()
    try:
        data = await request.json()
    except Exception:
        data = {}

    text = (data.get("text") or "").strip()
    if not text:
        return web.json_response({"error": "Prompt cannot be empty"}, status=400)

    if "time" in text.lower() or "date" in text.lower():
        now_str = datetime.now().strftime("%I:%M %p on %A, %B %d, %Y")
        return web.json_response({
            "answer": f"The current time is {now_str}.",
            "latency": round(time.time() - t0, 2)
        })

    answer = await call_llm(text)

    if answer:
        return web.json_response({
            "answer": answer,
            "latency": round(time.time() - t0, 2)
        })

    return web.json_response({
        "answer": "Unable to connect to AI provider. Please check your console logs.",
        "latency": round(time.time() - t0, 2)
    }, status=200)

def main():
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_get('/', handle_index)
    app.router.add_get('/api/time', handle_time)
    app.router.add_post('/api/ask', handle_ask)
    app.router.add_options('/api/ask', handle_ask)

    port = int(os.getenv("PORT", 5000))
    print(f"🌐 SANA AI ENGINE RUNNING AT: http://localhost:{port}")
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()