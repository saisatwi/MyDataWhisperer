# Directive Document: MyDataWhisperer Engine

## 1. Objective
Establish an asynchronous, production-deployed web interface (`MyDataWhisperer`) featuring resilient API key parsing, multi-model failover mechanisms, and real-time frontend latency diagnostics.

---

## 2. Scope & Technical Requirements
- **Server Architecture:** Asynchronous non-blocking web server powered by Python `aiohttp`.
- **Model Orchestration:**
  - Primary Provider: Groq API (`llama-3.3-70b-versatile` / `llama-3.1-8b-instant`).
  - Fallback Provider: Google Gemini API (`gemini-2.5-flash`).
- **Authentication Resilience:** Flexible parser accepting legacy (`AIzaSy...`) and modern (`AQ...`) Google API Key formats alongside standard Bearer tokens.
- **Frontend Engine:** Single-page interface with live time sync (`/api/time`), latency display, and keyboard short-cuts.
- **Deployment Target:** Public cloud deployment hosted via Render PaaS.

---

## 3. Completion Criteria
1. Server returns HTTP 200 for index, time, and query routes.
2. If Groq API fails or rate-limits, system executes Gemini API seamlessly without returning an error to the user interface.
3. System runs continuously on a public HTTPS URL without event-loop crashes.

---

## 4. Results & Handoff Appendix

### A. Artifact Links
- **Live Production URL:** [https://mydatawhisperer.onrender.com/](https://mydatawhisperer.onrender.com/)
- **GitHub Repository:** [https://github.com/saisatwi/mydatawhisper](https://github.com/saisatwi/mydatawhisper)

### B. Reproduction & Viewing Steps
1. Navigate to [https://mydatawhisperer.onrender.com/](https://mydatawhisperer.onrender.com/).
2. Submit a prompt (e.g., *"Explain asynchronous event loops in two sentences"*).
3. Observe response generation, provider success status in server logs, and latency metrics displayed on the frontend.

### C. Verification Checks & Actual Results
- **Endpoint Test `/api/time`:** Verified. Returns live server timestamp.
- **Provider Fallback Test:** Verified. Primary request attempts route to Groq; simulated 404 error successfully triggers Gemini backup handler.
- **Public URL Verification:** Verified HTTP 200 response on `https://mydatawhisperer.onrender.com/`.

### D. AI Contribution & Corrections
- **AI Output Utilized:** Refactored synchronous `urllib.request` worker execution within `asyncio.to_thread` wrappers to prevent blocking the `aiohttp` main event loop.
- **Human Corrections Applied:** Corrected model string deprecations (`gemini-1.5-flash` $\rightarrow$ `gemini-2.5-flash` and `llama-3.1-8b-instant` $\rightarrow$ `llama-3.3-70b-versatile`) and adjusted regex validation to support Google's updated `AQ.` key format.

### E. Limitations
- **Cold Start Delays:** Render free tier instances enter sleep mode after inactivity, leading to a 30–50 second delay on initial boot requests.
- **Context Length:** Stateless endpoint configuration without multi-turn server-side session persistence.