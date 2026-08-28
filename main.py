from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from nlp_engine import get_nlp_engine
from graph_engine import get_graph_engine
from risk_engine import calculate_risk, get_intervention_recommendation
from classification_engine import get_classification_engine
from llm_engine import generate_llm_explanation
from data_loader import load_industrial_dataset

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the real dataset
real_dataset = load_industrial_dataset()
dataset_index = 0

all_processed_reports = []

class ProcessResponse(BaseModel):
    report: dict
    report_class: str
    extracted_entities: dict
    risk_data: dict
    llm_explanation: str
    interventions: list
    is_precursor: bool

class CustomReportRequest(BaseModel):
    text: str

@app.get("/api/reset")
def reset_state():
    global dataset_index, all_processed_reports
    dataset_index = 0
    all_processed_reports = []
    
    get_graph_engine().reset()
    
    return {"status": "reset_complete"}

@app.get("/api/state")
def get_state():
    return {
        "total_reports": len(all_processed_reports),
        "reports": all_processed_reports,
        "is_complete": dataset_index >= len(real_dataset)
    }

@app.post("/api/process_next", response_model=ProcessResponse)
def process_next_report():
    global dataset_index
    
    if dataset_index >= len(real_dataset):
        raise HTTPException(status_code=400, detail="No more reports in dataset")
        
    raw_record = real_dataset[dataset_index]
    
    # Map to our report structure
    report = {
        "id": f"RPT-REAL-{dataset_index+1:03d}",
        "date": raw_record["Data"],
        "text": raw_record["Description"],
        "location": raw_record["Local"],
        "action_status": raw_record.get("Action Status", "Closed")
    }
    
    dataset_index += 1
    
    nlp = get_nlp_engine()
    graph = get_graph_engine()
    
    extracted_entities = nlp.extract_entities(report["text"])
    
    # Inject the structured location into the entities so it appears prominently in the Knowledge Graph
    if report["location"] and report["location"] not in extracted_entities["locations"]:
        extracted_entities["locations"].append(report["location"])
    embedding = nlp.get_embedding(report["text"])
    
    # Classification
    classifier = get_classification_engine()
    report_class = classifier.classify(report["text"])
    
    graph.add_report(report["id"], report["date"], report["text"], extracted_entities, embedding, report.get("action_status", "Closed"))
    
    related_reports = graph.get_related_reports(report["id"], nlp)
    
    risk_data = calculate_risk(report["id"], graph.reports[report["id"]], related_reports)
    interventions = get_intervention_recommendation(risk_data, extracted_entities)
    
    # LLM Explanation
    llm_explanation = generate_llm_explanation(risk_data, extracted_entities.get("equipment", []), related_reports)
    
    is_precursor = risk_data["score"] >= 70
    
    processed_result = {
        "report": report,
        "report_class": report_class,
        "extracted_entities": extracted_entities,
        "risk_data": risk_data,
        "llm_explanation": llm_explanation,
        "interventions": interventions,
        "is_precursor": is_precursor
    }
    all_processed_reports.append(processed_result)
    
    return processed_result

@app.post("/api/submit_report", response_model=ProcessResponse)
def submit_custom_report(request: CustomReportRequest):
    import datetime
    
    report_id = f"RPT-CUS-{len(all_processed_reports)+1:03d}"
    date_str = datetime.date.today().isoformat()
    
    report = {
        "id": report_id,
        "date": date_str,
        "text": request.text,
        "location": "Custom_Input_Area"
    }
    
    nlp = get_nlp_engine()
    graph = get_graph_engine()
    
    extracted_entities = nlp.extract_entities(report["text"])
    
    if report["location"] not in extracted_entities["locations"]:
        extracted_entities["locations"].append(report["location"])
    embedding = nlp.get_embedding(report["text"])
    
    classifier = get_classification_engine()
    report_class = classifier.classify(report["text"])
    
    graph.add_report(report["id"], report["date"], report["text"], extracted_entities, embedding, report.get("action_status", "Closed"))
    
    related_reports = graph.get_related_reports(report["id"], nlp)
    
    risk_data = calculate_risk(report["id"], graph.reports[report["id"]], related_reports)
    interventions = get_intervention_recommendation(risk_data, extracted_entities)
    
    llm_explanation = generate_llm_explanation(risk_data, extracted_entities.get("equipment", []), related_reports)
    
    is_precursor = risk_data["score"] >= 70
    
    processed_result = {
        "report": report,
        "report_class": report_class,
        "extracted_entities": extracted_entities,
        "risk_data": risk_data,
        "llm_explanation": llm_explanation,
        "interventions": interventions,
        "is_precursor": is_precursor
    }
    all_processed_reports.append(processed_result)
    
    return processed_result

@app.get("/api/graph_data")
def get_graph_data():
    graph_engine = get_graph_engine()
    elements = []
    
    for node, data in graph_engine.graph.nodes(data=True):
        elements.append({
            "data": {
                "id": node,
                "label": node,
                "type": data.get("type", "Unknown")
            }
        })
        
    for u, v, data in graph_engine.graph.edges(data=True):
        elements.append({
            "data": {
                "source": u,
                "target": v,
                "label": data.get("relation", "")
            }
        })
        
    return elements
    
@app.post("/api/simulate")
def simulate_intervention(intervention_type: str):
    if not all_processed_reports:
        return {"risk_score": 0, "trajectory": "STABLE"}
        
    latest_risk = all_processed_reports[-1]["risk_data"]["score"]
    
    if intervention_type == "delay":
        return {"risk_score": min(latest_risk + 10, 100), "trajectory": "ESCALATING"}
    elif intervention_type == "resolve_action":
        return {"risk_score": max(latest_risk - 25, 10), "trajectory": "DECREASING"}
    elif intervention_type == "inspect":
        return {"risk_score": max(latest_risk - 36, 10), "trajectory": "DECREASING"}
    elif intervention_type == "replace":
        return {"risk_score": max(latest_risk - 69, 5), "trajectory": "DECREASING"}
    return {"risk_score": latest_risk, "trajectory": "STABLE"}

app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

@app.get("/")
def read_root():
    return FileResponse("frontend/dist/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
