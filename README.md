# 🚀 MyDataWhisperer — Sana AI Low-Latency Web Assistant

[![Live Demo](https://img.shields.io/badge/Render-Live--Demo-brightgreen?style=for-the-badge&logo=render)](https://mydatawhisperer.onrender.com/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?style=for-the-badge&logo=github)](https://github.com/saisatwi/mydatawhisper)

MyDataWhisperer is an asynchronous web interface and AI backend engine built with Python (`aiohttp`) and a responsive frontend. It implements multi-provider model cascade failover (Groq & Google Gemini) to eliminate single-point API failures, manage rate limits, and maintain low-latency response delivery.

---

## 🔗 Submission Artifact Links

- **Live Production Application:** [https://mydatawhisperer.onrender.com/](https://mydatawhisperer.onrender.com/)
- **GitHub Repository:** [https://github.com/saisatwi/mydatawhisper](https://github.com/saisatwi/mydatawhisper)
- **Author:** Sai Satwik ([@saisatwi](https://github.com/saisatwi))

---

## ✨ Key System Features & Architecture

- **Asynchronous Engine:** High-concurrency event loop powered by Python's `aiohttp`.
- **Model Cascade & Failover Engine:** Automatically attempts low-latency generation via Groq (`llama-3.3-70b-versatile`) and falls back seamlessly to Google Gemini (`gemini-2.5-flash`) if rate limits or HTTP exceptions occur.
- **Resilient Key Parsing:** Supports legacy (`AIzaSy...`) and modern (`AQ...`) Google API Key formats alongside standard Bearer token authentication.
- **Frontend Diagnostics:** Live server time synchronization (`/api/time`) and request latency reporting.
- **Production SSL Handling:** Native custom SSL context handling for local developer environments behind corporate proxies or firewalls.

---

## 🛠️ Tech Stack & Dependencies

- **Backend:** Python 3.10+, `aiohttp`, `python-dotenv`
- **AI Engine Integrations:**
  - **Groq API:** `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`
  - **Google Gemini API:** `gemini-2.5-flash`
- **Deployment:** Render PaaS
- **Frontend:** HTML5, CSS3, JavaScript (Fetch API)
