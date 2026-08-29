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

        # ---- Oil & Gas domain keyword sets (replaces the old generic demo lists) ----
        self.equipment_keywords = [
            "wellhead valve", "wellhead", "manifold valve", "pipeline valve", "gas valve",
            "blowout preventer", "bop", "annular preventer", "christmas tree",
            "process furnace", "furnace", "floating roof tank", "fixed roof tank",
            "storage tank", "tank farm", "high pressure separator", "separator vessel",
            "pressure gauge", "pressure safety valve", "psv", "relief valve", "rupture disc",
            "drilling hoist", "hoist", "crane", "wire rope", "sling",
            "compressor", "compressor skid", "cooling tower", "diesel generator",
            "switchgear", "junction box", "scada", "fire water pump", "forklift",
            "filling carousel", "tanker loading arm", "loading arm", "scaffold",
            "sucker rod pump", "heater treater", "slide valve", "personnel transfer basket",
            "helideck", "pump", "valve", "pipe", "vessel", "tank",
        ]
        self.hazard_keywords = [
            "h2s", "gas leak", "gas smell", "gas odor", "hydrocarbon odor", "gas blowout",
            "blowout", "well control", "fire", "explosion", "flashback", "bleve", "ignition",
            "blast", "overpressure", "pressure spike", "pressure drop", "electrical shock",
            "arc flash", "earthing fault", "confined space", "oxygen level", "load swing",
            "fell", "fall", "guard rail", "slip", "spill", "leak", "leakage",
            "vehicle skid", "chemical splash", "corrosive", "skin contact", "crude oil mist",
            "manual lifting", "back strain", "high wind", "sea condition", "storm",
            "corrosion", "structural failure", "cracked", "worn out", "degraded",
            "no harness", "no hard hat", "ppe violation", "cyber", "remote command",
            "erratic", "malfunction", "trip", "vibration", "pressure", "smoke", "oil",
        ]
        self.location_keywords = [
            "field station", "rig", "platform", "refinery", "tank farm", "gathering station",
            "pipeline", "terminal", "plant", "substation", "field camp", "loading bay",
            "area a", "area b", "warehouse c", "unit d", "unit a",
        ]

        # Normalization Dictionary (expanded for oil & gas terms; generic entries kept
        # for backward compatibility with the original demo dataset)
        self.normalization_map = {
            "pump p-104": "PUMP_104", "pump 104": "PUMP_104", "p-104": "PUMP_104", "p104": "PUMP_104",
            "compressor b": "COMPRESSOR_B", "area a": "UNIT_A", "unit a": "UNIT_A",
            "oil": "OIL_LEAK", "spill": "OIL_LEAK", "leak": "OIL_LEAK", "leakage": "OIL_LEAK",
            "gas leak": "GAS_LEAK", "gas smell": "GAS_LEAK", "gas odor": "GAS_LEAK",
            "hydrocarbon odor": "GAS_LEAK", "gas blowout": "GAS_LEAK", "h2s": "H2S_EXPOSURE",
            "blowout": "BLOWOUT", "well control": "BLOWOUT",
            "fire": "FIRE", "explosion": "FIRE", "flashback": "FIRE", "bleve": "FIRE",
            "ignition": "FIRE", "blast": "FIRE",
            "overpressure": "PRESSURE", "pressure spike": "PRESSURE", "pressure drop": "PRESSURE",
            "pressure": "PRESSURE",
            "electrical shock": "ELECTRICAL", "arc flash": "ELECTRICAL", "earthing fault": "ELECTRICAL",
            "electrical": "ELECTRICAL",
            "confined space": "CONFINED_SPACE", "oxygen level": "CONFINED_SPACE",
            "load swing": "CRANE_HAZARD",
            "fell": "SLIP_HAZARD", "fall": "SLIP_HAZARD", "slip": "SLIP_HAZARD", "guard rail": "SLIP_HAZARD",
            "vehicle skid": "VEHICLE_HAZARD",
            "chemical splash": "CHEMICAL_EXPOSURE", "corrosive": "CHEMICAL_EXPOSURE",
            "skin contact": "CHEMICAL_EXPOSURE", "crude oil mist": "CHEMICAL_EXPOSURE",
            "manual lifting": "ERGONOMIC", "back strain": "ERGONOMIC",
            "high wind": "WEATHER", "sea condition": "WEATHER", "storm": "WEATHER",
            "corrosion": "STRUCTURAL", "structural failure": "STRUCTURAL", "cracked": "STRUCTURAL",
            "worn out": "STRUCTURAL", "degraded": "STRUCTURAL",
            "no harness": "PPE_VIOLATION", "no hard hat": "PPE_VIOLATION", "ppe violation": "PPE_VIOLATION",
            "cyber": "CYBER_SECURITY", "remote command": "CYBER_SECURITY",
            "erratic": "EQUIPMENT_MALFUNCTION", "malfunction": "EQUIPMENT_MALFUNCTION",
            "trip": "EQUIPMENT_MALFUNCTION", "vibration": "VIBRATION",
            "smoke": "FIRE",
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

        # Fallback severity heuristic — ONLY used when the caller doesn't supply a
        # real severity value (e.g. for free-typed custom reports with no ground truth).
        # main.py overrides this with the dataset's real severity for real reports.
        severity = 1
        if any(w in text_lower for w in ["near miss", "almost", "injury", "critical", "severe", "failed", "fatal", "hospitalized"]):
            severity = 3
        elif any(w in text_lower for w in ["hazard", "spill", "slip", "leakage", "leak"]):
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