# 🚨 AI-Powered Safety Precursor Intelligence System

**Smart India Hackathon (SIH 26165) — Oil India Limited**

An enterprise-grade AI platform that detects escalating safety incident patterns across Oil India's Duliajan facility in Assam. Using NLP, a Temporal Knowledge Graph, and multi-factor risk scoring, it connects isolated hazard reports across time, equipment, and locations to predict Serious Injuries and Fatalities (SIF) **before** they happen.

---

## 🌟 Key Features

| Feature | Description |
|---|---|
| **NLP Entity Extraction** | 230 Oil India domain terms — equipment, hazards, locations, Hindi-mixed reports |
| **ML Classification** | TF-IDF + Logistic Regression — 97.4% accuracy on unseen test data |
| **Temporal Knowledge Graph** | NetworkX graph linking incidents, equipment, locations over time |
| **9-Factor Risk Engine** | Frequency, recency, severity trend, SIF pathway, urgency, and more |
| **AI Explanations** | Google Gemini generates natural-language "Why Now?" briefings |
| **Interactive Chatbot** | Gemini-powered safety assistant with quick questions |
| **Facility Heatmap** | Leaflet.js map of Oil India's Duliajan facility locations |
| **Risk Trajectory Chart** | Chart.js time-series of risk score escalation |
| **Knowledge Graph Viz** | Cytoscape.js interactive graph of precursor chains |
| **PDF/Excel Upload** | Ingest safety reports from uploaded documents |
| **Email Alerts** | Automatic precursor alerts via SMTP |
| **MongoDB Persistence** | Survives server restarts (with JSON fallback) |
| **Spring Boot Auth** | JWT + RBAC for production deployment |

---

## 📊 ML Performance

| Metric | Value |
|---|---|
| **Dataset** | 190 reports (5 styles: clean, messy, Hindi-mixed, escalation, edge cases) |
| **Classification Accuracy** | **97.4%** on held-out test set (80/20 stratified split) |
| **Cross-Validation** | **98.9% ± 1.3%** (5-fold) |
| **NLP Vocabulary** | **230 Oil India domain terms** |
| **Classes** | 7 merged categories: Fall/Slip, Chemical/Gas, Electrical, Thermal/Burn, Cut/Abrasion, Mechanical/Crush, Manual/Mechanical |

### Per-Class F1 Scores

| Class | Precision | Recall | F1-Score |
|---|---|---|---|
| Chemical/Gas | 1.00 | 0.92 | 0.96 |
| Cut/Abrasion | 1.00 | 1.00 | 1.00 |
| Electrical | 1.00 | 1.00 | 1.00 |
| Fall/Slip | 0.90 | 1.00 | 0.95 |
| Manual/Mechanical | 1.00 | 1.00 | 1.00 |
| Mechanical/Crush | 1.00 | 1.00 | 1.00 |
| Thermal/Burn | 1.00 | 1.00 | 1.00 |
| **Weighted Avg** | **0.98** | **0.97** | **0.97** |

---

## 🏗️ Architecture

```
Report Text (typed, uploaded, or from dataset)
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  1. NLP Engine (spaCy + SentenceTransformers)        │
│     - Entity extraction (230 domain terms)           │
│     - Semantic embeddings (all-MiniLM-L6-v2)        │
│     - Duplicate detection (cosine similarity)        │
│     - Hindi/English code-switch handling             │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  2. ML Classifier (TF-IDF + Logistic Regression)    │
│     - 7-class incident categorization               │
│     - 97.4% accuracy on held-out test data          │
│     - Trained at startup on 190 reports             │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  3. Temporal Knowledge Graph (NetworkX)              │
│     - Links incidents → equipment → locations        │
│     - Semantic similarity edges between reports      │
│     - Time-aware relationships                      │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  4. 9-Factor Risk Engine                             │
│     - Frequency, Recency, Severity Trend            │
│     - Semantic Similarity, Equipment Recurrence     │
│     - Location Recurrence, Unresolved Actions       │
│     - SIF Pathway, Urgency Score                    │
│     → Risk Score: 0-100, trajectory: ESCALATING/    │
│       STABLE/DECREASING                             │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  5. AI Explanation (Google Gemini)                   │
│     - "Why Now?" natural language briefing          │
│     - Falls back to template if API unavailable     │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  6. Frontend Dashboard (React + Vite)                │
│     - Dashboard: Risk circle, sparkline, AI reason  │
│     - Analytics: Charts, heatmap, equipment stats   │
│     - Event Graph: Cytoscape.js knowledge graph     │
│     - Chatbot: Gemini-powered safety assistant      │
└─────────────────────────────────────────────────────┘
```

---

## How to Run Locally (Step-by-Step)

### What You Need First

| Tool | Version | How to Check | How to Install |
|---|---|---|---|
| **Python** | 3.9 or higher | Open terminal, type `python --version` | [python.org/downloads](https://www.python.org/downloads/) |
| **Node.js** | 18 or higher | Open terminal, type `node --version` | [nodejs.org](https://nodejs.org/) (download LTS) |
| **Git** | Any version | Open terminal, type `git --version` | [git-scm.com](https://git-scm.com/) |
| **pip** | Comes with Python | Open terminal, type `pip --version` | Automatically included with Python |

> **Windows users:** During Python installation, check the box that says **"Add Python to PATH"** - this is critical!

---

### Step 1 - Clone the Project

Open a terminal (Command Prompt, PowerShell, or Terminal) and run:

```bash
git clone https://github.com/peeyush521/Sih-oil7.git
cd Sih-oil7
```

This downloads the entire project to your computer.

---

### Step 2 - Install Python Packages

```bash
pip install -r requirements.txt
```

This installs ~15 packages (FastAPI, spaCy, scikit-learn, etc.). Takes 2-5 minutes on first run.

> **If `pip` doesn't work**, try `pip3 install -r requirements.txt` or `python -m pip install -r requirements.txt`

---

### Step 3 - Download the spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

This downloads a small English language model (~15MB) used for NLP entity extraction.

---

### Step 4 - Set the Gemini API Key (Optional but Recommended)

The system works WITHOUT an API key (uses template-based explanations), but for full AI explanations and chatbot, set your key:

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

**Windows Command Prompt:**
```cmd
set GEMINI_API_KEY=your_api_key_here
```

**Mac/Linux:**
```bash
export GEMINI_API_KEY=your_api_key_here
```

> **Tip:** For permanent setup, create a `.env` file in the project root with `GEMINI_API_KEY=your_api_key_here`

---

### Step 5 - Build the Frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

This installs React dependencies and builds the frontend (~1 minute).

---

### Step 6 - Start the Backend Server

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

**Wait until you see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

> This means the server is running. **Keep this terminal window open!**

---

### Step 7 - Open in Your Browser

Open **http://127.0.0.1:8000** in Chrome, Firefox, or Edge.

---

### Step 8 - Use the System

1. **Sign up** with any email and password (stored locally on your machine)
2. **Log in** with the email/password you just created
3. Click **"+ Load next report"** to process safety reports one by one
4. Watch the **Risk Trajectory** graph escalate as patterns emerge
5. Check **Classification** for confidence scores and hazard type
6. Check **"Why Now?"** for AI-generated explanations
7. Switch to **Analytics** tab for charts, heatmap, equipment stats
8. Switch to **Event Graph** tab - use **filters** to view CRITICAL-only or by equipment
9. Click the **Chatbot** button to ask questions about safety data
10. Use **Custom Input** to type your own safety report and see real-time analysis

---

## 🐳 Docker Deployment (Alternative)

```bash
# Build and start both backend and frontend
docker-compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

Or run just the backend:

```bash
docker build -t safeguard-ai .
docker run -p 8000:8000 --env-file .env safeguard-ai
```

---

## 📁 Project Structure

```
Sih-oil7/
├── main.py                          # FastAPI backend (all endpoints)
├── nlp_engine.py                    # spaCy NER + SentenceTransformers + 230 domain terms
├── classification_engine.py         # TF-IDF + Logistic Regression (97.4% accuracy)
├── graph_engine.py                  # NetworkX temporal knowledge graph
├── risk_engine.py                   # 9-factor deterministic risk scoring
├── llm_engine.py                    # Google Gemini API with template fallback
├── data_loader.py                   # 190-report dataset + CSV loader
├── alerts.py                        # Email precursor alerts (SMTP)
├── pdf_generator.py                 # PDF report export
├── mongo_persistence.py             # MongoDB persistence (JSON fallback)
├── benchmark.py                     # 500-sequence controlled benchmark
├── classifier_metrics.json          # Pre-computed classifier metrics
├── benchmark_data.json              # Pre-computed benchmark comparison
├── real_industrial_safety_data.csv  # 190-report dataset
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Docker build config
├── docker-compose.yml               # Full stack orchestration
├── .env                             # Environment variables (GEMINI_API_KEY)
├── frontend/
│   ├── src/
│   │   ├── App.jsx                  # React dashboard (4 tabs)
│   │   └── index.css                # Industrial dark-theme UI
│   ├── dist/                        # Production build (served by FastAPI)
│   ├── package.json                 # Frontend dependencies
│   └── vite.config.js               # Vite configuration
├── sif-auth/                        # Spring Boot auth service (Java)
│   └── src/main/java/com/sih/auth/  # JWT, RBAC, Audit
├── PITCH_DECK.md                    # Presentation script
├── SPRING_BOOT_AUTH.md              # Java auth implementation guide
└── README.md                        # This file
```

---

## 🔑 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | System health check (reports count, Gemini status) |
| `/api/process_next` | POST | Process next report from dataset |
| `/api/submit_report` | POST | Analyze a custom safety report (JSON: `{"text": "..."}`) |
| `/api/upload_report` | POST | Upload PDF/Excel/CSV/TXT file with safety reports |
| `/api/state` | GET | All processed reports + current state |
| `/api/graph_data` | GET | Knowledge graph nodes + edges (Cytoscape format) |
| `/api/analytics` | GET | Location distribution, equipment frequency, hazard types |
| `/api/benchmark` | GET | ML metrics: accuracy, CV scores, per-class F1 |
| `/api/chat` | POST | Chatbot: ask questions about safety data (JSON: `{"question": "..."}`) |
| `/api/duplicates` | GET | Detect similar/duplicate reports |
| `/api/precursor_patterns` | GET | Advanced precursor pattern analysis |
| `/api/simulate` | POST | Simulate intervention impact |
| `/api/export` | GET | Export all reports as JSON |
| `/api/export/pdf` | GET | Export PDF safety report |
| `/api/reset` | GET | Reset simulation state |

---

## 🗣️ Chatbot — What to Ask

The Gemini-powered chatbot answers questions about loaded safety data:

| Question | What It Returns |
|---|---|
| "Which location is most hazardous?" | Locations ranked by incident count + avg risk |
| "What are the danger zones?" | RED/YELLOW/GREEN zone classification |
| "What should I do next?" | Prioritized action recommendations |
| "Give me a summary" | Total reports, precursors, locations, equipment stats |
| "Which equipment is most dangerous?" | Equipment ranked by incident count + avg risk |
| "Is the risk increasing?" | Trend analysis from loaded reports |
| "What's causing the most incidents?" | Root cause clustering |
| "Should I shut down any equipment?" | Risk-based equipment recommendations |

**Without Gemini**: Rule-based answers using keyword matching and structured data queries.

**With Gemini**: Open-ended natural language answers using full context from all loaded reports.

---

## 📊 Dataset

The system ships with **190 industrial safety reports** covering Oil India's Duliajan facility:

| Category | Count | Description |
|---|---|---|
| **Clean Reports** | 40 | Professional incident reports with clear descriptions |
| **Messy Reports** | 40 | Abbreviated field notes, shorthand, incomplete sentences |
| **Hindi-Mixed Reports** | 30 | Hinglish code-switching ("P-104 ka seal toot gaya hai") |
| **Escalation Chains** | 26 | Sequential reports showing risk escalation over time |
| **Edge Cases** | 54 | Short reports, multi-hazard, unusual equipment, rare events |

**25 unique facility locations**: Well pads, pump houses, processing units, fuel farms, warehouses, treatment plants, scaffold towers.

**10 equipment types**: Pipeline, compressor, separator, tank, bund, panel, forklift, scaffolding, valve, wellhead.

---

## 🔬 For Judges

### "Is this real AI or just if-else rules?"

**Five AI layers:**

1. **spaCy NER** — Pre-trained transformer extracts entities from free text (230 domain terms)
2. **Sentence Transformers** — Converts reports to 384-dim vectors for semantic similarity
3. **Scikit-Learn Classifier** — TF-IDF + Logistic Regression trained on 190 reports with 80/20 split (97.4% accuracy)
4. **9-Factor Risk Engine** — Composite scoring based on safety science research
5. **Google Gemini** — Generates natural language explanations from structured risk data

### "How does it handle unseen data?"

- 80/20 stratified train/test split
- 5-fold cross-validation: 98.9% ± 1.3%
- Handles Hindi-mixed, abbreviated, and messy field notes
- F1-score: 0.97 weighted average across 7 classes

### "What's the business impact?"

- Detects precursor patterns **before** serious incidents occur
- Reduces false alerts (keyword-only: 60/100 false alerts -> our system: 2/100)
- Average lead time: 3.0 days before potential SIF event
- Explainable risk scores with traceable reasoning

---

## 🔐 Spring Boot Auth (Separate Service)

See `SPRING_BOOT_AUTH.md` for JWT + RBAC + Audit implementation.

```bash
cd sif-auth
./mvnw spring-boot:run
# Runs on http://localhost:8080
```

---

## 👥 Team Roles

| Role | Focus | Stack |
|---|---|---|
| **NLP Engineers (2)** | Entity extraction, classification, data | Python, spaCy, scikit-learn |
| **Graph + Risk (2)** | Knowledge graph, risk scoring, precursors | Python, NetworkX |
| **Backend + AI (1)** | FastAPI, Gemini integration, persistence | Python, FastAPI, MongoDB |
| **Frontend + Auth (1)** | Dashboard, heatmap, chatbot, auth | React, Leaflet, Cytoscape.js, Java |

---

## 🐛 Troubleshooting

| Issue | Fix |
|---|---|
| `ModuleNotFoundError: spacy` | Run `pip install -r requirements.txt` |
| `Can't find model 'en_core_web_sm'` | Run `python -m spacy download en_core_web_sm` |
| Frontend shows "Frontend not built yet" | Run `cd frontend && npm install && npm run build` |
| Chatbot says "Gemini API not configured" | Set `GEMINI_API_KEY` environment variable |
| Reports reset on restart | Check `api_state.json` file permissions |
| Port 8000 already in use | `netstat -ano | findstr :8000` then `taskkill /PID <pid> /F` |

---

## 📄 License

Built for Smart India Hackathon 2026 — Oil India Limited.

*Designed for safety. Engineered for impact.* 🇮🇳

---

## ☁️ Deploy to Render (Free Hosting)

### One-Click Deploy

1. Push your code to GitHub (already done)
2. Go to [render.com](https://render.com) → Sign up (free)
3. Click **New +** → **Web Service**
4. Connect your GitHub repo: `peeyush521/Sih-oil7`
5. Render auto-detects `render.yaml` — click **Deploy**
6. Wait 5-10 minutes for build to complete
7. You get a live URL like: `https://safeguard-ai.onrender.com`

### Mobile Demo

Once deployed, **anyone can open the link on their phone**:
- Sidebar disappears on mobile
- Bottom tab bar appears (Dashboard, Reports, Analytics, Graph)
- "Type Report" button opens slide-up modal
- Chatbot works on mobile
- No app install needed — just tap the link

### Environment Variables

In Render dashboard → Environment tab:
- Add `GEMINI_API_KEY` = your API key

### Free Tier Limits

| Limit | Value |
|---|---|
| Sleeps after | 15 min of inactivity |
| First request after sleep | ~30-50 seconds (cold start) |
| Monthly hours | 750 hours free |

**Tip for demo:** Keep the tab open before judges arrive so it doesn't sleep.
