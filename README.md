# 🚨 AI-Powered Safety Precursor Intelligence System

**Smart India Hackathon (SIH 26165) — Oil India Limited**

An enterprise-grade AI platform that detects escalating safety incident patterns across Oil India's Duliajan facility in Assam. Using NLP, a Temporal Knowledge Graph, and multi-factor risk scoring, it connects isolated hazard reports across time, equipment, and locations to predict Serious Injuries and Fatalities (SIF) **before** they happen.

---

## 🌟 Key Features

| Feature | Description |
|---|---|
| **NLP Entity Extraction** | 230 Oil India domain terms — equipment, hazards, locations, Hindi-mixed reports |
| **Fuzzy Matching** | Handles typos and misspellings from field workers ("wellhad" → "wellhead") |
| **ML Classification** | TF-IDF + Logistic Regression with confidence scores and per-class breakdown |
| **Novel Hazard Detection** | Flags unknown hazard types when classifier confidence < 35% |
| **Severity Detection (1-5)** | Natural language severity extraction: "could have been fatal" = 5/5 |
| **Quantity Extraction** | Auto-extracts dangerous readings: LEL %, vibration mm/s, temperature °C, spill volume |
| **Shift/Time Detection** | Detects night shift (+8 risk points) and shift change (+5 risk points) |
| **14-Factor Risk Engine** | Time-decay weighting, cross-equipment correlation, SIF pathways, adjustable thresholds |
| **Temporal Knowledge Graph** | NetworkX graph linking incidents, equipment, locations over time |
| **Interactive Graph Viz** | Cytoscape.js with risk-level coloring, filters, hover tooltips, edge coloring |
| **AI Explanations** | Google Gemini generates natural-language "Why Now?" briefings |
| **Interactive Chatbot** | Gemini-powered safety assistant with quick questions |
| **Facility Heatmap** | Leaflet.js map of Oil India's Duliajan facility locations |
| **Risk Trajectory Chart** | Chart.js time-series of risk score escalation |
| **PDF/Excel Upload** | Ingest safety reports from uploaded documents |
| **Email Alerts** | Automatic precursor alerts via SMTP |
| **MongoDB Persistence** | Survives server restarts (with JSON fallback) |
| **JWT Auth** | SQLite-based authentication with role-based access |
| **Mobile Responsive** | Bottom tab navigation for field workers on phones |

---

## 🧠 AI Architecture — 5 Layers

```
Report Text (typed, uploaded, or from dataset)
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  1. NLP Engine (spaCy + SentenceTransformers)        │
│     - Entity extraction (230 domain terms)           │
│     - Fuzzy matching for field-worker typos          │
│     - Severity detection (1-5 from language)         │
│     - Quantity extraction (%, °C, mm/s, litres)     │
│     - Shift/time-of-day detection                    │
│     - Semantic embeddings (all-MiniLM-L6-v2)        │
│     - Duplicate detection (cosine similarity)        │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  2. ML Classifier (TF-IDF + Logistic Regression)    │
│     - 7-class incident categorization               │
│     - Confidence scores with per-class breakdown    │
│     - Novel hazard detection (< 35% = unknown)      │
│     - 97.4% accuracy on held-out test data          │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  3. Temporal Knowledge Graph (NetworkX)              │
│     - Links incidents → equipment → locations        │
│     - Semantic similarity edges between reports      │
│     - Graph rebuilt on server restart                │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  4. 14-Factor Risk Engine                            │
│     - Severity, Frequency, Recency (time-decay)     │
│     - Severity Trend, Semantic Similarity           │
│     - Equipment/Location Recurrence                 │
│     - Unresolved Actions, SIF Pathway, Urgency      │
│     - Night Shift (+8), Shift Change (+5)           │
│     - Cross-Equipment Correlation (+12)             │
│     - Quantity-Based Alerting (+5)                  │
│     → Risk Score: 0-100, trajectory: ESCALATING/    │
│       STABLE/DECREASING                             │
│     → Adjustable thresholds for safety officers     │
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
│     - Dashboard: Risk circle, confidence bars, AI   │
│     - Analytics: Charts, heatmap, equipment stats   │
│     - Event Graph: Filters, risk coloring, tooltips │
│     - Chatbot: Gemini-powered safety assistant      │
│     - Mobile: Bottom tabs, slide-up report input    │
└─────────────────────────────────────────────────────┘
```

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

## ⚡ 14-Factor Risk Engine

| # | Factor | Max Points | Description |
|---|---|---|---|
| 1 | **Base Severity** | 50 | NLP-extracted severity (1-5) × 10 |
| 2 | **Frequency** | 20 | Time-decay weighted count of related events |
| 3 | **Recency** | 15 | How recent was the last related event |
| 4 | **Severity Trend** | 15 | Is the situation escalating? |
| 5 | **Semantic Similarity** | 5 | Are reports about the same underlying issue? |
| 6 | **Equipment Recurrence** | 10 | Same equipment involved again? |
| 7 | **Location Recurrence** | 5 | Same location again? |
| 8 | **Unresolved Actions** | 15 | Open corrective actions from previous incidents |
| 9 | **SIF Pathway** | 15 | Loss of Control / Energy Release / Exposure |
| 10 | **Urgency Score** | 10 | Language urgency ("immediately", "emergency") |
| 11 | **Night Shift** | 8 | Incidents during night shift (higher statistical risk) |
| 12 | **Shift Change** | 5 | Handover periods (communication gap risk) |
| 13 | **Cross-Equipment** | 12 | 3+ different equipment types failing = systemic |
| 14 | **Quantity Alert** | 5 | Dangerous readings (LEL >10%, vibration >4mm/s, temp >80°C) |

### Time-Decay Weighting

Recent reports matter more. Weight = 2^(-age_days / 14):

- **Today** → 1.00 (full impact)
- **1 week ago** → 0.71
- **2 weeks ago** → 0.50
- **1 month ago** → 0.25
- **2 months ago** → 0.06 (almost nothing)

---

## 🚀 Quick Start (Run on Any Machine)

### Prerequisites

- **Python 3.9+** (3.11 recommended)
- **Node.js 18+** (for frontend)
- **Git**

### Step 1: Clone the Repository

```bash
git clone https://github.com/peeyush521/Sih-oil7.git
cd Sih-oil7
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**
- `fastapi` + `uvicorn` — Backend web ser
