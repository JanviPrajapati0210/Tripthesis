# ✈️ Tripthesis — AI-Powered Multi-Agent Travel Planner

Tripthesis is an AI travel planning platform where six specialist agents — flights, hotels, itinerary, budget, culture, and a feasibility reviewer — collaborate under a central orchestrator to generate a complete, validated trip plan in real time.

## 🚀 Live Demo

- **Deployed Application:** https://tripthesis.onrender.com
- **GitHub Repository:** https://github.com/JanviPrajapati0210/Tripthesis

## 🧩 Problem Statement

Most AI travel planners are a single prompt wrapped around a form — one model guessing at flights, hotels, a schedule, and a budget all at once, with no way to check its own work. The output often looks polished but can be geographically unrealistic (places too far apart for one day) or logistically inconsistent (a sunset activity scheduled at 9am), and there's no way to fix a small part of the plan without regenerating the whole thing.

## 💡 Solution Overview

Tripthesis solves this with a true multi-agent architecture instead of one large prompt:

- Six specialist agents each own one narrow responsibility, instead of one model trying to do everything at once
- A dedicated feasibility agent reviews the itinerary agent's output — checking pacing, geographic feasibility, and logical sequencing — before the plan reaches the user
- Independent agents run concurrently via a thread pool, so total generation time is roughly the slowest single agent call, not the sum of all six
- Results stream to the browser live via Server-Sent Events as each agent finishes, instead of one long wait
- Users can request a targeted change ("make Day 2 more relaxed") and only the itinerary agent re-runs — flights, hotels, budget, and culture stay exactly as they were
- A shared base module gives every agent consistent error handling, so one agent failing (rate limit, network issue, malformed response) never crashes the whole request

## ✨ Key Features

| Feature | Description |
|---|---|
| 🗓️ Day-by-Day Itinerary | Structured morning/afternoon/evening plan with specific places per day |
| 🔍 Feasibility Review | A dedicated agent critiques the itinerary for geographic and pacing issues before it reaches the user |
| ✈️ Flight Suggestions | Route, airline, and price-range recommendations |
| 🏨 Hotel Recommendations | Accommodation suggestions matched to budget tier and travel style |
| 💰 Budget Breakdown | Full estimated cost across the trip duration |
| 🍛 Culture & Food Guide | Local etiquette, cuisine, and practical travel tips |
| 🗺️ Live Map | Itinerary places geocoded via OpenStreetMap and pinned on an interactive Leaflet map |
| 💬 Chat-Based Refinement | Ask for a specific change in plain English; only the affected agent re-runs |
| 📄 PDF Export | One-click download of the complete, formatted travel plan |
| ⚡ Real-Time Streaming | Each agent's result appears in the UI the moment it completes, via Server-Sent Events |

## 🛠️ Technologies Used

**Backend**
- Flask — application server and routing
- Python 3.10+
- `concurrent.futures.ThreadPoolExecutor` — parallel agent execution

**AI**
- Groq API (`llama-3.3-70b-versatile`) — powers all six agents
- Custom prompt-per-agent design, with a dedicated agent-reviews-agent (feasibility) pattern

**Maps & Location**
- OpenStreetMap Nominatim — free geocoding, no API key required
- Leaflet.js — interactive map rendering

**Export**
- ReportLab — server-side PDF generation

**Frontend**
- Vanilla JavaScript
- Server-Sent Events (EventSource API) — live streaming updates, no polling

## 🗂️ Project Structure

```
tripthesis/
├── app.py                     # Flask routes, SSE streaming, geocoding
├── config.py                  # Environment-based configuration
├── requirements.txt
├── .env.example
├── agents/
│   ├── base.py                 # Shared Groq client + error handling
│   ├── orchestrator.py         # Parallel agent coordination (non-streaming route)
│   ├── flights_agent.py
│   ├── hotels_agent.py
│   ├── itinerary_agent.py      # Includes refine() for targeted chat-based edits
│   ├── budget_agent.py
│   ├── culture_agent.py
│   ├── feasibility_agent.py    # Reviews the itinerary agent's output
│   └── pdf_generator.py
├── templates/
│   ├── index.html              # Trip input form
│   ├── stream.html             # Live SSE results page + refinement chat box
│   └── result.html             # Non-streaming fallback results page
└── static/
    └── style.css
```

## ⚙️ Running Locally

**Prerequisites:** Python 3.10+, a free [Groq API key](https://console.groq.com)

```bash
# 1. Clone the repository
git clone https://github.com/Ladnil03/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME

# 2. Create a virtual environment and install dependencies
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Add your GROQ_API_KEY and generate a FLASK_SECRET_KEY (see below)

# 4. Run the app
python app.py
```

App runs at `http://localhost:5000`.

Generate a Flask secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | API key from console.groq.com |
| `FLASK_SECRET_KEY` | Yes | Random key used to sign session cookies |
| `FLASK_DEBUG` | No | Set to `1` for local development only — must stay off in any public deployment |

## 📡 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Trip input form |
| `/plan` | POST | Generates a complete plan synchronously (fallback route) |
| `/plan-stream` | POST | Initializes session state, renders the live streaming page |
| `/stream-events` | GET | SSE endpoint — streams each agent's result as it completes |
| `/refine-itinerary` | POST | Re-runs the itinerary agent with feedback, re-validates via the feasibility agent |
| `/save-plan` | POST | Saves the completed plan to session for export |
| `/download-pdf` | POST | Generates and downloads the plan as a PDF |

## ⚠️ Known Limitations

- Flight and hotel prices are LLM-generated estimates based on training data — not live pricing from a real booking API.
- Nominatim's free geocoding tier is rate-limited to 1 request/second, so itineraries with many places take a few extra seconds to map.
- Plans are stored in-session only and aren't persisted after the browser session ends.

## 🔮 Roadmap

- Ground flight/hotel pricing with a real fare API (e.g. Amadeus Self-Service)
- Persistent, database-backed plan storage
- Shareable multi-user plan links

## 👤 Author

Janvi Prajapati

## 📄 License

MIT License
