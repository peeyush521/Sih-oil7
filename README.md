# AI-Powered Safety Precursor Intelligence System 🚨
**Smart India Hackathon (SIH 26165) Prototype**

An enterprise-grade, full-stack AI platform designed to dynamically detect escalating safety incident patterns across industrial environments. By leveraging Natural Language Processing (NLP) and a Temporal Knowledge Graph, this system connects seemingly isolated hazard reports across time, equipment, and locations to mathematically predict Serious Injuries and Fatalities (SIF) before they happen.

---

## 🌟 Core Innovation: Temporal Precursor Intelligence
Standard safety systems treat incident reports as isolated text classification problems (e.g., flagging a report as "High Severity"). 

Our system connects the dots. Instead of waiting for a catastrophic failure, our architecture uses a **Deterministic Risk Engine** that models the escalation of semantically similar events. It actively tracks unresolved corrective actions, frequency spikes, and SIF pathway emergence to trigger preemptive alerts.

### How the Pipeline Works:
1. **Unstructured Data Ingestion**: Parses messy, human-written safety logs.
2. **Entity Normalization**: Uses `spaCy` to resolve varying nomenclatures (e.g., "Pump P-104", "P104", "Pump 104" → `PUMP_104`).
3. **Semantic Similarity**: Uses `SentenceTransformers` (384-dimensional embeddings) to mathematically match incidents despite different wording ("fluid escaping" vs "hydraulic leak").
4. **Temporal Graph Generation**: Uses `NetworkX` to construct a dynamic, time-aware web of hazards and locations.
5. **Deterministic Risk Escalation**: Calculates an explainable 0–100 risk score based on recency, frequency, and severity compounding.
6. **AI Explanation Generation**: Converts the raw math deltas back into a human-readable "Why did risk change?" briefing.

---

## 🕸️ The Precursor Chain (Temporal Graph)
This is the visual "brain" of our intelligence logic. While legacy systems treat safety reports as isolated documents in a database, our Precursor Chain maps the relational web of the entire facility in real-time to connect the dots.

* **Contextual AI (Nodes):** Raw text is shattered into structured entities: Incidents (Red), Equipment (Blue), Locations (Green), and Hazards (Yellow).
* **Hidden Connections (Edges):** If someone slips on Monday and an inspector reports a pressure drop on Thursday, the graph visually draws lines linking both independent events to the exact same equipment node (e.g., `PUMP_104`).
* **Precursor Detection:** As you load reports, the temporal graph grows. When a specific node accumulates a high density of hazard connections in a short timeframe, the system identifies that cluster as a **Precursor Chain**—a mathematically proven pathway indicating a major accident is imminent.

---

## 📊 Scientific Benchmark Results
We validated our Temporal Graph against standard industry approaches using an automated sequence generator testing 500+ synthetic incident escalations.

| Method | Precision | Recall | F1-Score | FA/100 (False Alerts) | Avg Lead Time (Days) |
|---|---|---|---|---|---|
| **Baseline 1 (Keyword-only)** | 100.0% | 75.0% | 85.7% | 0.0 | 4.0 days |
| **Baseline 2 (Single-Report ML)** | 40.0% | 100.0% | 57.1% | 60.0 | 24.5 days |
| **Our System (Temporal Graph)** | **100.0%** | **100.0%** | **100.0%** | **0.0** | **3.0 days** |

**Conclusion:** Our system achieved perfect precision and zero false alerts by intentionally waiting for an escalating *pattern* to form, completely eliminating the extreme alert fatigue suffered by standard ML models.

---

## 🖥️ Technology Stack
* **Backend:** Python, FastAPI (Headless REST API)
* **AI & NLP:** `spaCy`, `SentenceTransformers`, `scikit-learn`
* **Graph Engine:** `NetworkX`
* **Frontend:** React, Vite, CSS (Industrial Command Center UI)
* **Visualizations:** `Cytoscape.js`

---

## 🚀 How to Run the Demo Locally

### 1. Clone the Repository
```bash
git clone https://github.com/peeyush521/Sih-oil7.git
cd Sih-oil7
```

### 2. Install Dependencies
Ensure you have Python 3.9+ and Node.js installed.
```bash
# Install Python backend dependencies
pip install -r requirements.txt

# Download required spaCy language model
python -m spacy download en_core_web_sm
```

### 3. Start the Backend Server
Start the headless FastAPI engine (handles NLP, Risk Assessment, and Graph building).
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### 4. Start the Frontend Command Center
In a new terminal window, start the Vite development server for the UI.
```bash
cd frontend
npm install
npm run dev
```

### 5. Run the Presentation Flow
1. Open your browser to `http://localhost:5173/`.
2. Click **[ ＋ Load next report ]** sequentially to step through the 13-report dataset.
3. Watch the Risk Trajectory graph dynamically plot the risk escalation over time.
4. Review the generated **"Why Now?"** evidence panel to see the exact risk multipliers of the latest report.
5. Click **[ ✓ Mark complete ]** in the simulator to prove closed-loop risk mitigation.

---

*Designed for safety. Engineered for impact.*
