Set-Content README.md @"
# 🚀 MyDataWhisperer — Sana AI Web Assistant

MyDataWhisperer is an asynchronous web assistant built with Python (`aiohttp`) and a responsive frontend interface. It features a model cascade failover mechanism across **Google Gemini** and **Groq** endpoints to maintain uptime and ensure low-latency responses.

---

## ✨ Features

- **Asynchronous Engine:** Built on Python's \`aiohttp\` for non-blocking network I/O.
- **Model Cascade & Failover:** Automatically routes requests to primary models (Groq) and falls back to secondary models (Gemini) upon rate limits or connection errors.
- **Interactive UI:** Clean web UI with real-time latency measurement and status tracking.
- **Environment Management:** Automated \`.env\` parsing via \`python-dotenv\` for local API key configuration.
- **Bypass SSL Constraints:** Native SSL context handling for local developer environments behind network proxies or antivirus firewalls.

---

## 🛠️ Tech Stack & Dependencies

- **Language:** Python 3.10+
- **Web Framework:** \`aiohttp\`
- **Environment Management:** \`python-dotenv\`
- **AI Libraries:** \`google-genai\`, \`groq\`
- **Frontend:** HTML5, CSS3, JavaScript (Fetch API)

---

## 📋 Prerequisites

Ensure you have Python 3.10 or higher installed. Install all required dependencies using \`requirements.txt\`:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

---

## ⚙️ Environment Setup

1. Clone this repository:
   \`\`\`bash
   git clone https://github.com/saisatwi/mydatawhisper.git
   cd mydatawhisper
   \`\`\`

2. Create a \`.env\` file in the root directory and add your API keys:
   \`\`\`env
   GROQ_API_KEY=your_groq_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   PORT=5000
   \`\`\`

---

## 🚀 Usage

Start the backend server by running:

\`\`\`bash
python sana_web.py
\`\`\`

Once running, navigate to the following URL in your browser:
\`\`\`
http://localhost:5000
\`\`\`

---

## 👤 Author

**Sai Satwik**
- GitHub: [@saisatwi](https://github.com/saisatwi)

---

## 🛡️ License

Distributed under the MIT License.
"@