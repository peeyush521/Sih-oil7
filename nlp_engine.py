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
        self.equipment_keywords = [
            # --- Oil & Gas equipment (original) ---
            "pump p-104", "pump 104", "p-104", "p104",
            "compressor", "valve", "pipe", "pipeline",
            "wellhead", "wh-12", "wh-13", "wh-14",
            "separator", "sep-201", "heat exchanger",
            "tank", "vessel", "boiler", "furnace",
            "turbine", "generator", "motor",
            "crane", "forklift", "rig",
            "drill", "drilling", "workover",
            "panel wb-07", "panel", "switchgear",
            "scaffold", "ladder", "platform",
            "harness", "lanyard", "guardrail",
            "gasket", "seal", "bearing",
            # --- Oil India domain-specific equipment (30+ new) ---
            "pig launcher", "pig receiver", "pigging",
            "blowout preventer", "bop",
            "well testing", "flow station", "metering",
            "separator vessel", "test separator",
            "produced water", "flowline",
            "bund wall", "bund", "secondary containment",
            "flare", "flare stack",
            "chemical injection pump", "dosing pump",
            "ccr", "central control room",
            "rcd", "residual current device",
            "melev", "meew", "mobile elevated work platform",
            "manlift", "cherry picker",
            "excavator", "backhoe", "bulldozer",
            "demulsifier", "methanol",
            "blowdown", "blowdown valve",
            "process heater", "fired heater",
            "air cooler", "fin fan",
            "steam trap", "steam trace",
            "flare header", "relief valve", "psv",
            "actuator", "solenoid valve",
            "scada", "plc", "dcs",
        ]
        self.hazard_keywords = [
            # --- General hazards (original) ---
            "leak", "leakage", "spill", "slip", "fall", "fire", "smoke",
            "pressure", "vibration", "oil", "gas", "chemical",
            "explosion", "ignition", "corrosion", "erosion",
            "overheating", "overpressure",
            "electrical", "shock", "arc", "short circuit",
            "confined space", "asphyxiation", "toxic",
            "heat", "burn", "scald",
            "cut", "laceration", "abrasion", "puncture",
            "crush", "pinch", "strike", "impact",
            "struck by", "caught in", "caught between",
            "ergonomic", "strain", "sprain",
            "collapse", "cave-in",
            # --- Oil India domain-specific hazards (30+ new) ---
            "h2s release", "gas release", "vapor release",
            "hydrocarbon release", "crude oil", "condensate",
            "flare", "torching",
            "blowout", "kick",
            "oxygen deficiency", "oxygen depletion",
            "organic vapor", "volatile organic",
            "acid", "caustic", "sodium hydroxide",
            "sulfuric acid", "hydrochloric acid",
            "asbestos", "silica dust",
            "mercury", "lead",
            "nitrogen", "inert gas",
            "static discharge", "electrostatic",
            "arc flash", "arc blast",
            "pinch point", "entanglement",
            "falling object", "dropped object",
        ]
        self.location_keywords = [
            # --- Facility areas (original) ---
            "area a", "area b", "warehouse c", "unit a", "unit b", "unit c",
            "duliajan", "jorhat", "nazira", "sivasagar",
            "well pad", "rig site", "loading bay", "laydown area",
            "control room", "admin building", "workshop",
            "pump house", "valve station", "tank farm", "pipe rack",
            "office", "cafeteria", "laboratory",
            "maintenance shop", "warehouse",
            # --- Oil India specific locations (30+ new) ---
            "processing unit", "production unit",
            "separation unit", "treatment unit",
            "compression station", "gas processing",
            "oil processing", "crude handling",
            "water injection", "water treatment",
            "effluent treatment", "waste management",
            "flaring system", "flare pit",
            "chemical storage", "chemical yard",
            "fuel farm", "fuel storage",
            "lube oil", "hydraulic oil storage",
            "cable tray", "cable trench",
            "switchyard", "substation",
            "instrument air", "utility building",
            "fire water", "fire pump house",
            "machine shop", "welding shop",
            "blasting", "painting shop",
            "spare parts", "tool room",
            "vehicle yard", "security",
            "helipad", "jetty",
        ]
        self.normalization_map = {
            "pump p-104": "PUMP_104", "p-104": "PUMP_104",
            "compressor": "COMPRESSOR",
            "wellhead wh-12": "WELLHEAD_WH12", "wh-12": "WELLHEAD_WH12",
            "wellhead wh-13": "WELLHEAD_WH13", "wh-13": "WELLHEAD_WH13",
            "separator sep-201": "SEPARATOR_SEP201",
            "panel wb-07": "PANEL_WB07",
            "area a": "UNIT_A", "unit a": "UNIT_A",
            "area b": "UNIT_B", "unit b": "UNIT_B",
            "warehouse c": "WAREHOUSE_C",
            "oil": "OIL_LEAK", "spill": "OIL_LEAK",
            "leak": "OIL_LEAK", "leakage": "OIL_LEAK",
            "slip": "SLIP_HAZARD", "fall": "SLIP_HAZARD",
            "fire": "FIRE_HAZARD", "explosion": "EXPLOSION_HAZARD",
            "electrical": "ELECTRICAL_HAZARD", "shock": "ELECTRICAL_HAZARD",
            "overheating": "THERMAL_HAZARD", "burn": "THERMAL_HAZARD",
            "pressure": "PRESSURE_HAZARD",
            "corrosion": "CORROSION_HAZARD", "vibration": "VIBRATION_HAZARD",
            "confined space": "CONFINED_SPACE",
            "chemical": "CHEMICAL_HAZARD", "toxic": "CHEMICAL_HAZARD",
            # Location normalization: keyword -> canonical dataset name
            "fuel farm": "Fuel_Farm_FF01", "fuel storage": "Fuel_Farm_FF01",
            "effluent treatment": "Effluent_Treatment_ET01",
            "pump house": "Pump_House_PH01",
            "chemical storage": "Chemical_Storage_CS01", "chemical yard": "Chemical_Storage_CS01",
            "warehouse": "Warehouse_WH01",
            "loading bay": "Loading_Bay_LB01",
            "laydown area": "Laydown_Area_LA01",
            "control room": "Control_Room_CR01",
            "admin building": "Admin_Building_AB01",
            "maintenance shop": "Maintenance_Shop_MS01", "workshop": "Maintenance_Shop_MS01",
            "tank farm": "Tank_Farm_TF01",
            "well pad": "Well_Pad_WP01",
            "pipe rack": "Pipe_Rack_PR01",
            "substation": "Substation_SS01",
            "laboratory": "Laboratory_LAB01",
            "gas processing": "Gas_Processing_GP01",
            "flare pit": "Flare_Pit_FP01",
            "tool room": "Tool_Room_TR01",
            "unit a": "Unit_A_Processing", "unit b": "Unit_B_Production", "unit c": "Unit_C_Treatment",
        }
        self.urgency_high = [
            "immediately", "critical", "emergency", "fatal",
            "could have been fatal", "near miss", "serious injury",
            "severe", "catastrophic", "evacuation", "shutdown",
            "stop work", "danger", "hazardous", "life threatening",
            "major incident", "uncontrolled",
        ]
        self.urgency_medium = [
            "needs attention", "monitor closely", "repair needed",
            "maintenance required", "inspection needed",
            "degrading", "worsening", "escalating", "recurring", "repeated",
        ]
        self.similarity_threshold = 0.85

    def extract_entities(self, text):
        self.nlp(text.lower())
        equipment, hazards, locations = [], [], []
        tl = text.lower()
        for kw in self.equipment_keywords:
            if kw in tl: equipment.append(kw)
        for kw in self.hazard_keywords:
            if kw in tl: hazards.append(kw)
        for kw in self.location_keywords:
            if kw in tl: locations.append(kw)
        if not equipment:
            matches = re.findall(r"[a-zA-Z]-\d{3,}", text)
            if matches: equipment.extend([m.lower() for m in matches])
        equipment = self._dedup(equipment)
        hazards = self._dedup(hazards)
        locations = self._dedup(locations)
        equipment = list(set([self.normalization_map.get(e, e.upper()) for e in equipment]))
        hazards = list(set([self.normalization_map.get(e, e.upper()) for e in hazards]))
        locations = list(set([self.normalization_map.get(e, e.upper()) for e in locations]))
        severity = 1
        if any(w in tl for w in self.urgency_high): severity = 3
        elif any(w in tl for w in self.urgency_medium): severity = 2
        elif any(w in tl for w in ["hazard", "spill", "slip", "leakage", "near miss"]): severity = 2
        urgency = sum(3 if w in tl else 0 for w in self.urgency_high) + sum(1 if w in tl else 0 for w in self.urgency_medium)
        urgency = min(urgency, 10)
        return {"equipment": equipment, "hazards": hazards, "locations": locations, "severity": severity, "urgency_score": urgency}

    def _dedup(self, entities):
        entities = list(set(entities))
        # Remove substrings that are part of longer entries
        result = []
        for e1 in entities:
            is_subset = False
            for e2 in entities:
                if e1 != e2 and e1 in e2:
                    is_subset = True
                    break
            if not is_subset:
                result.append(e1)
        return result

    def get_embedding(self, text):
        return self.encoder.encode(text)

    def calculate_similarity(self, emb1, emb2):
        from sentence_transformers import util
        return util.cos_sim(emb1, emb2).item()

    def detect_duplicates(self, reports, threshold=None):
        if threshold is None: threshold = self.similarity_threshold
        duplicates = []
        embeddings = [self.get_embedding(r.get("text", "")) for r in reports]
        for i in range(len(reports)):
            for j in range(i + 1, len(reports)):
                sim = self.calculate_similarity(embeddings[i], embeddings[j])
                if sim >= threshold:
                    duplicates.append({"report_1": reports[i].get("id", str(i)), "report_2": reports[j].get("id", str(j)), "similarity": round(sim, 3), "text_1": reports[i].get("text", "")[:80], "text_2": reports[j].get("text", "")[:80]})
        return duplicates

    def extract_worker_id(self, text):
        for pat in [r"(?:worker|employee|operator)\s*(?:id|no)?\s*:?\s*(\w+)", r"EMP[-_]?(\d+)"]:
            m = re.search(pat, text, re.IGNORECASE)
            if m: return m.group(1).upper()
        return "UNKNOWN"


nlp_engine = None
def get_nlp_engine():
    global nlp_engine
    if nlp_engine is None: nlp_engine = NLPEngine()
    return nlp_engine
