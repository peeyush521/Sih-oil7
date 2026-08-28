import spacy
import spacy.cli
from sentence_transformers import SentenceTransformer
import re
import numpy as np

class NLPEngine:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

        self.equipment_keywords = ["pump p-104", "pump 104", "p-104", "p104", "compressor b", "pump", "compressor", "valve", "pipe"]
        self.hazard_keywords = ["leak", "leakage", "spill", "slip", "fall", "fire", "smoke", "pressure", "vibration", "oil"]
        self.location_keywords = ["area a", "area b", "warehouse c", "unit d", "unit a"]
        
        # Normalization Dictionary
        self.normalization_map = {
            "pump p-104": "PUMP_104",
            "pump 104": "PUMP_104",
            "p-104": "PUMP_104",
            "p104": "PUMP_104",
            "compressor b": "COMPRESSOR_B",
            "area a": "UNIT_A",
            "unit a": "UNIT_A",
            "oil": "OIL_LEAK",
            "spill": "OIL_LEAK",
            "leak": "OIL_LEAK",
            "leakage": "OIL_LEAK",
            "slip": "SLIP_HAZARD",
            "fall": "SLIP_HAZARD"
        }
        
    def extract_entities(self, text: str):
        doc = self.nlp(text.lower())
        
        equipment = []
        hazards = []
        locations = []
        
        text_lower = text.lower()
        
        for keyword in self.equipment_keywords:
            if keyword in text_lower:
                equipment.append(keyword)
        for keyword in self.hazard_keywords:
            if keyword in text_lower:
                hazards.append(keyword)
        for keyword in self.location_keywords:
            if keyword in text_lower:
                locations.append(keyword)
                
        # Regex for common equipment IDs
        if not equipment:
            matches = re.findall(r'[a-zA-Z]-\d{3,}', text)
            if matches:
                equipment.extend([m.lower() for m in matches])
                
        # Deduplicate while preserving specific terms over generic (e.g., 'pump p-104' over 'pump')
        equipment = self._deduplicate_entities(equipment)
        hazards = self._deduplicate_entities(hazards)
        locations = self._deduplicate_entities(locations)
        
        # Entity Normalization
        equipment = list(set([self.normalization_map.get(e, e.upper()) for e in equipment]))
        hazards = list(set([self.normalization_map.get(e, e.upper()) for e in hazards]))
        locations = list(set([self.normalization_map.get(e, e.upper()) for e in locations]))
        
        # Simple severity heuristic
        severity = 1
        if any(w in text_lower for w in ["near miss", "almost", "injury", "critical", "severe", "failed"]):
            severity = 3
        elif any(w in text_lower for w in ["hazard", "spill", "slip", "leakage"]):
            severity = 2
            
        return {
            "equipment": equipment,
            "hazards": hazards,
            "locations": locations,
            "severity": severity
        }
        
    def _deduplicate_entities(self, entities):
        entities = list(set(entities))
        # Keep longest matching string (e.g., if both 'pump' and 'pump p-104' are present, keep 'pump p-104')
        final_entities = []
        for e1 in entities:
            if not any(e1 != e2 and e1 in e2 for e2 in entities):
                final_entities.append(e1)
        return final_entities

    def get_embedding(self, text: str):
        return self.encoder.encode(text)

    def calculate_similarity(self, emb1, emb2):
        from sentence_transformers import util
        return util.cos_sim(emb1, emb2).item()

# Singleton instance
nlp_engine = None
def get_nlp_engine():
    global nlp_engine
    if nlp_engine is None:
        nlp_engine = NLPEngine()
    return nlp_engine
