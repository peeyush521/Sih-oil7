# AI-Powered Safety Precursor Intelligence System

**Smart India Hackathon (SIH 26165) - Oil India Limited**

An enterprise-grade AI platform that detects escalating safety incident patterns across Oil India's Duliajan facility in Assam. Using NLP, a Temporal Knowledge Graph, and multi-factor risk scoring, it connects isolated hazard reports across time, equipment, and locations to predict Serious Injuries and Fatalities (SIF) **before** they happen.

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

## Quick Copy-Paste (All Commands Together)

For experienced users who want to run everything at once:

```bash
git clone https://github.com/peeyush521/Sih-oil7.git
cd Sih-oil7
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cd frontend && npm install && npm run build && cd ..
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Then open http://127.0.0.1:8000 in your browser.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `python` command not found | Try `python3` or `py` instead. Make sure Python is added to PATH during installation |
| `pip` command not found | Try `pip3` or `python -m pip install -r requirements.txt` |
| `node` command not found | Install Node.js from [nodejs.org](https://nodejs.org/) |
| `git` command not found | Install Git from [git-scm.com](https://git-scm.com/) |
| Can't find model 'en_core_web_sm' | Run `python -m spacy download en_core_web_sm` again |
| Port 8000 already in use | Run: `netstat -ano | findstr :8000` then `taskkill /PID <number> /F` (Windows) or `kill -9 <number>` (Mac/Linux) |
| Frontend shows "Frontend not built yet" | Run `cd frontend && npm install && npm run build && cd ..` |
| Chatbot says "Gemini API not configured" | Set the GEMINI_API_KEY environment variable (see Step 4) |
| ModuleNotFoundError for any package | Run `pip install -r requirements.txt` again |
| `uvicorn` not recognized | Try `python -m uvicorn main:app --host 127.0.0.1 --port 8000` |

---

## Key Features

| Feature | Description |
|---|---|
| **NLP Entity Extraction** | 230 Oil India domain terms - equipment, hazards, locations, Hindi-mixed reports |
| **Fuzzy Matching** | Handles typos and misspellings from field workers ("wellhad" -> "wellhead") |
| **ML Classification** | TF-IDF + Logistic Regression with confidence scores and per-class breakdown |
| **Novel Hazard Detection** | Flags unknown hazard types when classifier confidence < 35% |
| **Severity Detection (1-5)** | Natural language severity extraction: "could have been fatal" = 5/5 |
| **Quantity Extraction** | Auto-extracts dangerous readings: LEL %, vibration mm/s, temperature C, spill volume |
| **Shift/Time Detection** | Detects night shift (+8 risk points) and shift change (+5 risk points) |
| **14-Factor Risk Engine** | Time-decay weighting, cross-equipment correlation, SIF pathways, adjustable thresholds |
| **Temporal Knowledge Graph** | NetworkX graph linking incidents, equipment, locations over time |
| **Interactive Graph Viz** | Cytoscape.js with risk-level coloring, filters, hover tooltips, edge coloring |
| **AI Explanations** | Google Gemini generates natural-language "Why Now?" briefings |
| **Interactive Chatbot** | Gemini-powered safety assistant with quick questions |
| **Facility Heatmap** | Leaflet.js map of Oil India Duliajan facility locations |
| **Risk Trajectory Chart** | Chart.js time-series of risk score escalation |
| **PDF/Excel Upload** | Ingest safety reports from uploaded documents |
| **Email Alerts** | Automatic precursor alerts via SMTP |
| **MongoDB Persistence** | Survives server restarts (with JSON fallback) |
| **JWT Auth** | SQLite-based authentication with role-based access |
| **Mobile Responsive** | Bottom tab navigation for field workers on phones |

---

## AI Architecture - 5 Layers

```
Report Text (typed, uploaded, or from dataset)
    |
    v
+---------------------------------------------+
|  1. NLP Engine (spaCy + SentenceTransformers)|
|     - Entity extraction (230 domain terms)   |
|     - Fuzzy matching for field-worker typos  |
|     - Severity detection (1-5 from language) |
|     - Quantity extraction (%, C, mm/s)       |
|     - Shift/time-of-day detection            |
|     - Semantic embeddings (all-MiniLM-L6-v2) |
|     - Duplicate detection (cosine similarity)|
+-----------------------+---------------------+
                        |
                        v
+---------------------------------------------+
|  2. ML Classifier (TF-IDF + LogReg)         |
|     - 7-class incident categorization       |
|     - Confidence scores per class           |
|     - Novel hazard detection (< 35%)        |
|     - 97.4% accuracy on held-out test data  |
+-----------------------+---------------------+
