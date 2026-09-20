import os
from google import genai
from groq import Groq

# Set keys directly if not using environment variables
GROQ_KEY = os.getenv("GROQ_API_KEY", "your_actual_groq_key_here")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "your_actual_gemini_key_here")

# --- 1. TEST GROQ API ---
print("Testing Groq API...")
try:
    groq_client = Groq(api_key=GROQ_KEY)
    
    # Active model: "llama-3.3-70b-versatile" or "openai/gpt-oss-20b"
    groq_response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Hello! Reply with 'Groq connected successfully'."}],
    )
    print("✅ Groq Success:", groq_response.choices[0].message.content)

except Exception as e:
    print(f"❌ Groq Error: {e}")

print("\n" + "="*40 + "\n")

# --- 2. TEST GEMINI API ---
print("Testing Gemini API...")
try:
    gemini_client = genai.Client(api_key=GEMINI_KEY)
    
    # Active model: "gemini-2.5-flash"
    gemini_response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello! Reply with 'Gemini connected successfully'.",
    )
    print("✅ Gemini Success:", gemini_response.text)

except Exception as e:
    print(f"❌ Gemini Error: {e}")