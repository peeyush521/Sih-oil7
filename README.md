# AI-Powered Safety Precursor Intelligence System 🚨
**Smart India Hackathon (SIH 26165) — Oil India**

An enterprise-grade AI platform that detects escalating safety incident patterns across industrial environments. Using NLP and a Temporal Knowledge Graph, it connects isolated hazard reports across time, equipment, and locations to predict Serious Injuries and Fatalities (SIF) **before** they happen.

---

## 🌟 Core Innovation: Temporal Precursor Intelligence

Standard safety systems treat incident reports as isolated text classification problems. **Our system connects the dots.** Instead of waiting for a catastrophic failure, our architecture uses a **Deterministic Risk Engine** that models the escalation of semantically similar events over time.

### Pipeline
1. **Unstructured Data Ingestion** — Parses messy, human-written safety logs
2. **Entity Normalization** — spaCy resolves varying nomenclature (`"Pump P-104"`, `"P104"` → `PUMP_104`)
3. **Semantic Similarity** — SentenceTransformers (384-dim embeddings) match incidents despite different wording
4. **Temporal Knowledge Graph** — NetworkX constructs a dynamic, time-aware web of hazards and locations
5. **Deterministic Risk Escalation** — Explainable 0–100 risk score based on recency, frequency, and severity
6. **AI Explanation** — Converts raw risk math into human-readable "Why did risk change?" briefing

---

## 📊 Scientific Benchmark Results

Validated against standard industry approaches using 500+ synthetic incident escalation sequences:

| Method | Precision | Recall | F1-Score | False Alerts/100 | Avg Lead Time |
|---|---|---|---|---|---|
| **Baseline 1 (Keyword-only)** | 100.0% | 75.0% | 85.7% | 0.0 | 4.0 days |
| **Baseline 2 (Single-Report ML)** | 40.0% | 100.0% | 57.1% | 60.0 | 24.5 days |
| **Our System (Temporal Graph)** | **100.0%** | **100.0%** | **100.0%** | **0.0** | **3.0 days** |

Our system achieves **zero false alerts** by waiting for an escalating *pattern* rather than reacting to isolated events.

Run the benchmark yourself:
```bash
python benchmark.py
```

---

## 🖥️ Technology Stack

| Layer | Technology |
|---|---|
| **NLP / Entity Extraction** | spaCy (NER) + SentenceTransformers (semantic similarity) |
| **Classification** | scikit-learn (TF-IDF + Logistic Regression) |
| **Knowledge Graph** | NetworkX (temporal multi-directed graph) |
| **Risk Scoring** | Custom deterministic engine (frequency + severity + recency + SIF pathway) |
| **LLM Explanation** | Google Gemini API (with template fallback) |
| **Backend** | Python, FastAPI (REST API) |
| **Frontend** | React, Vite, Cytoscape.js (knowledge graph visualization) |
| **Persistence** | JSON file-based state (MongoDB-ready architecture) |
| **Auth / Admin** | Spring Boot (Java) — separate service for JWT auth + audit logs |

---

## 🚀 How to Run

### 1. Clone & Install
```bash
git clone https://github.com/peeyush521/Sih-oil7.git
cd Sih-oil7

# Install Python backend dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

### 2. (Optional) Set Up Gemini API Key
For AI-powered natural language explanations:
```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# Linux/Mac
export GEMINI_API_KEY=your_api_key_here
```
> Without an API key, the system uses deterministic template-based explanations (still fully functional).

### 3. Start the Backend
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### 4. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```

### 5. Run the Demo
1. Open **http://localhost:5173/**
2. Click **[ ＋ Load next report ]** to step through 13 incident reports
3. Watch the **Risk Trajectory** graph plot escalation over time
4. Review the **"Why Now?"** evidence panel for risk multipliers
5. Try the **Custom Input** box — type your own safety report and click **Analyze**
6. Click **[ ✓ Mark complete ]** to simulate closed-loop risk mitigation

### 6. Run the Benchmark
```bash
python benchmark.py
```

---

## 📁 Project Structure

```
├── main.py                  # FastAPI backend (all endpoints)
├── nlp_engine.py            # spaCy NER + SentenceTransformers embeddings
├── graph_engine.py          # NetworkX temporal knowledge graph
├── risk_engine.py           # Deterministic risk scoring + interventions
├── classification_engine.py # TF-IDF + Logistic Regression classifier
├── llm_engine.py            # Gemini API with template fallback
├── data_loader.py           # Dataset generation + CSV loader
├── benchmark.py             # 500-sequence controlled benchmark
├── synthetic_data.py        # Synthetic incident chain generator
├── requirements.txt         # Python dependencies
├── frontend/
│   ├── src/App.jsx          # React dashboard (Cytoscape graph, risk viz)
│   ├── src/index.css        # Industrial dark-theme UI
│   └── dist/                # Production build
└── static/                  # Vanilla JS fallback UI
```

---

## 🔑 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/process_next` | POST | Process next report from dataset |
| `/api/submit_report` | POST | Analyze a custom safety report |
| `/api/state` | GET | Get all processed reports + current state |
| `/api/graph_data` | GET | Get knowledge graph nodes + edges |
| `/api/simulate` | POST | Simulate intervention impact |
| `/api/export` | GET | Export all reports as JSON |
| `/api/reset` | GET | Reset simulation state |
| `/api/health` | GET | System health check |

---

## 🔐 Spring Boot Auth Service (Java Team)

The Java team builds a separate Spring Boot service for production-grade auth and audit logging. See `SPRING_BOOT_AUTH.md` for the full implementation guide.

---

## 👥 Team Split (6 People)

| Role | Focus | Stack |
|---|---|---|
| **NLP Engineers (2)** | Entity extraction, classification, data sourcing | Python, spaCy, scikit-learn |
| **Graph + Risk (2)** | Knowledge graph, risk scoring, precursor logic | Python, NetworkX |
| **Backend + Explainability (1)** | FastAPI endpoints, LLM integration, persistence | Python, FastAPI |
| **Frontend + Auth (2)** | Dashboard, graph visualization, Spring Boot auth | React, Cytoscape.js, Java |

---

*Designed for safety. Engineered for impact.*
