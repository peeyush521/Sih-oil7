import networkx as nx
from typing import List, Dict, Any

class TemporalKnowledgeGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.reports = {}

    def reset(self):
        self.graph.clear()
        self.reports.clear()

    def add_report(self, report_id: str, date: str, text: str, extracted_entities: dict, embedding: Any, action_status: str = "Closed"):
        # Store report metadata
        self.reports[report_id] = {
            "date": date,
            "text": text,
            "entities": extracted_entities,
            "embedding": embedding,
            "action_status": action_status
        }
        
        # Add nodes and edges
        self.graph.add_node(report_id, type="Incident", date=date, severity=extracted_entities.get("severity", 1))
        
        for eq in extracted_entities.get("equipment", []):
            self.graph.add_node(eq, type="Equipment")
            self.graph.add_edge(report_id, eq, relation="INVOLVES")
            
        for loc in extracted_entities.get("locations", []):
            self.graph.add_node(loc, type="Location")
            self.graph.add_edge(report_id, loc, relation="OCCURRED_AT")
            
        for haz in extracted_entities.get("hazards", []):
            self.graph.add_node(haz, type="Hazard")
            self.graph.add_edge(report_id, haz, relation="CAUSED_BY")

    def get_related_reports(self, report_id: str, nlp_engine, similarity_threshold=0.5) -> List[Dict]:
        if report_id not in self.reports:
            return []
            
        target_report = self.reports[report_id]
        target_embedding = target_report["embedding"]
        target_entities = target_report["entities"]
        
        related = []
        for rid, rep in self.reports.items():
            if rid == report_id:
                continue
                
            # Check date (must be before or same day)
            if rep["date"] > target_report["date"]:
                continue
                
            evidence = []
            
            # 1. Semantic Similarity
            sim = nlp_engine.calculate_similarity(target_embedding, rep["embedding"])
            if sim >= similarity_threshold:
                evidence.append(f"High semantic similarity ({(sim*100):.1f}%)")
                
            # 2. Entity Recurrence
            shared_eq = set(target_entities.get("equipment", [])) & set(rep["entities"].get("equipment", []))
            if shared_eq:
                evidence.append(f"Same equipment ({', '.join(shared_eq)})")
                
            shared_loc = set(target_entities.get("locations", [])) & set(rep["entities"].get("locations", []))
            if shared_loc:
                evidence.append(f"Same location ({', '.join(shared_loc)})")
                
            if evidence:
                related.append({
                    "id": rid,
                    "date": rep["date"],
                    "text": rep["text"],
                    "severity": rep["entities"].get("severity", 1),
                    "action_status": rep.get("action_status", "Closed"),
                    "evidence": evidence
                })
                
        # Sort by date descending (most recent first)
        related.sort(key=lambda x: x["date"], reverse=True)
        return related

# Singleton
graph_engine = None
def get_graph_engine():
    global graph_engine
    if graph_engine is None:
        graph_engine = TemporalKnowledgeGraph()
    return graph_engine
