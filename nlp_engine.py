import spacy
import spacy.cli
from sentence_transformers import SentenceTransformer
import re
import numpy as np
from difflib import get_close_matches


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
            # --- Additional gas-specific hazards ---
            "methane", "lel", "uel", "flammable",
            "detonation", "deflagration",
            "oxygen enrichment", "nitrogen asphyxiation",
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
            "methane": "METHANE_HAZARD", "lel": "GAS_HAZARD",
            "flammable": "GAS_HAZARD",
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

        # --- IMPROVED SEVERITY DETECTION (1-5 scale) ---
        self.severity_5_critical = [
            "fatal", "death", "killed", "died", "fatality",
            "could have been fatal", "life threatening", "life-threatening",
            "catastrophic", "uncontrolled release", "massive explosion",
            "building collapse", "structural failure",
        ]
        self.severity_4_serious = [
            "serious injury", "hospitalization", "hospitalized",
            "major incident", "significant damage", "major spill",
            "emergency shutdown", "full evacuation", "evacuate",
            "toxic exposure", "h2s", "hydrogen sulfide",
            "arc flash", "electrocution", "amputation",
            "confined space rescue", "fire outbreak",
            "immediately", "critical", "danger", "stop work",
        ]
        self.severity_3_moderate = [
            "injury", "first aid", "medical treatment",
            "near miss", "narrowly avoided", "close call",
            "equipment damage", "significant leak", "major leak",
            "alarm triggered", "auto shutdown", "automatic shutdown",
            "ventilation failed", "containment breach",
            "degrading", "worsening", "escalating",
        ]
        self.severity_2_low = [
            "minor injury", "small spill", "minor leak",
            "inspection needed", "maintenance required",
            "repair needed", "monitoring", "observed",
            "slight vibration", "minor damage",
        ]
        self.severity_1_routine = [
            "routine", "normal", "expected", "planned",
            "no injury", "no damage", "contained",
            "minor", "negligible",
        ]

        # --- SHIFT/TIME DETECTION ---
        self.night_shift_keywords = [
            "night shift", "nightshift", "night-time", "midnight",
            "2am", "3am", "4am", "11pm", "12am", "02:00", "03:00",
            "after hours", "off hours", "graveyard",
        ]
        self.shift_change_keywords = [
            "shift change", "handover", "shift handover",
            "start of shift", "end of shift", "handoff",
        ]

        self.similarity_threshold = 0.85

    def extract_entities(self, text):
        self.nlp(text.lower())
        equipment, hazards, locations = [], [], []
        tl = text.lower()

        # --- FUZZY MATCHING: find close matches for misspellings ---
        words = re.findall(r'\b\w+\b', tl)
        for word in words:
            if len(word) >= 4:  # Only fuzz-match words 4+ chars
                # Check equipment
                matches = get_close_matches(word, self.equipment_keywords, n=1, cutoff=0.8)
                if matches and matches[0] not in equipment:
                    equipment.append(matches[0])
                # Check hazards
                matches = get_close_matches(word, self.hazard_keywords, n=1, cutoff=0.8)
                if matches and matches[0] not in hazards:
                    hazards.append(matches[0])
                # Check locations
                matches = get_close_matches(word, self.location_keywords, n=1, cutoff=0.8)
                if matches and matches[0] not in locations:
                    locations.append(matches[0])

        # Also do exact/substring matching (original logic)
        for kw in self.equipment_keywords:
            if kw in tl and kw not in equipment:
                equipment.append(kw)
        for kw in self.hazard_keywords:
            if kw in tl and kw not in hazards:
                hazards.append(kw)
        for kw in self.location_keywords:
            if kw in tl and kw not in locations:
                locations.append(kw)

        if not equipment:
            matches = re.findall(r"[a-zA-Z]-\d{3,}", text)
            if matches:
                equipment.extend([m.lower() for m in matches])

        equipment = self._dedup(equipment)
        hazards = self._dedup(hazards)
        locations = self._dedup(locations)
        equipment = list(set([self.normalization_map.get(e, e.upper()) for e in equipment]))
        hazards = list(set([self.normalization_map.get(e, e.upper()) for e in hazards]))
        locations = list(set([self.normalization_map.get(e, e.upper()) for e in locations]))

        # --- IMPROVED SEVERITY DETECTION (1-5 scale) ---
        severity = self._detect_severity(text, tl)

        # --- URGENCY SCORE (legacy, kept for backward compat) ---
        urgency_high = [
            "immediately", "critical", "emergency", "fatal",
            "could have been fatal", "near miss", "serious injury",
            "severe", "catastrophic", "evacuation", "shutdown",
            "stop work", "danger", "hazardous", "life threatening",
            "major incident", "uncontrolled",
        ]
        urgency_medium = [
            "needs attention", "monitor closely", "repair needed",
            "maintenance required", "inspection needed",
            "degrading", "worsening", "escalating", "recurring", "repeated",
        ]
        urgency = sum(3 if w in tl else 0 for w in urgency_high) + sum(1 if w in tl else 0 for w in urgency_medium)
        urgency = min(urgency, 10)

        # --- QUANTITY EXTRACTION ---
        quantities = self._extract_quantities(text)

        # --- SHIFT/TIME ANALYSIS ---
        shift_info = self._detect_shift(text, tl)

        return {
            "equipment": equipment,
            "hazards": hazards,
            "locations": locations,
            "severity": severity,
            "urgency_score": urgency,
            "quantities": quantities,
            "shift_info": shift_info,
        }

    def _detect_severity(self, text, tl):
        """Detect severity on a 1-5 scale from natural language."""
        # Check from highest to lowest severity
        for phrase in self.severity_5_critical:
            if phrase in tl:
                return 5
        for phrase in self.severity_4_serious:
            if phrase in tl:
                return 4
        for phrase in self.severity_3_moderate:
            if phrase in tl:
                return 3
        for phrase in self.severity_2_low:
            if phrase in tl:
                return 2
        for phrase in self.severity_1_routine:
            if phrase in tl:
                return 1

        # --- Context-based severity boost ---
        # If multiple hazard keywords found, bump severity
        hazard_count = sum(1 for h in self.hazard_keywords if h in tl)
        if hazard_count >= 4:
            return 4
        elif hazard_count >= 3:
            return 3
        elif hazard_count >= 2:
            return 2

        # Default to 2 (slightly above minimum — treat everything as worth noting)
        return 2

    def _extract_quantities(self, text):
        """Extract numerical quantities with units from report text."""
        quantities = []
        patterns = [
            # Percentages: "18% LEL", "4.5 mm/s"
            (r'(\d+(?:\.\d+)?)\s*%', 'percent'),
            # Vibration: "4.5 mm/s"
            (r'(\d+(?:\.\d+)?)\s*mm/s', 'vibration_mm_s'),
            # Temperature: "87C", "87°C", "87 C"
            (r'(\d+(?:\.\d+)?)\s*°?C(?:elsius)?', 'temperature_c'),
            # Volume: "50 litres", "200 gallons", "10 barrels"
            (r'(\d+(?:\.\d+)?)\s*(litres?|liters?|gallons?|barrels?|bbl)', 'volume'),
            # Pressure: "150 psi", "10 bar", "500 kpa"
            (r'(\d+(?:\.\d+)?)\s*(psi|bar|kpa|mpa)', 'pressure'),
            # Length/distance: "3 meters", "10 feet"
            (r'(\d+(?:\.\d+)?)\s*(meters?|metres?|feet|ft|m)\b', 'distance'),
            # Time: "3 minutes", "2 hours"
            (r'(\d+(?:\.\d+)?)\s*(minutes?|mins?|hours?|hrs?|seconds?|secs?)', 'time'),
            # Generic number + word unit
            (r'(\d+(?:\.\d+)?)\s+([a-zA-Z]+)', 'generic'),
        ]

        seen = set()
        for pattern, unit_type in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                value = float(match.group(1))
                unit = match.group(2) if match.lastindex >= 2 else match.group(0)
                key = f"{value}_{unit_type}"
                if key not in seen:
                    seen.add(key)
                    quantities.append({
                        "value": value,
                        "unit": unit.strip(),
                        "type": unit_type,
                        "raw": match.group(0),
                    })

        return quantities

    def _detect_shift(self, text, tl):
        """Detect shift/time-of-day information from report text."""
        is_night = any(kw in tl for kw in self.night_shift_keywords)
        is_shift_change = any(kw in tl for kw in self.shift_change_keywords)

        # Check for time patterns like "02:30", "14:00"
        time_match = re.search(r'\b(\d{1,2}):(\d{2})\b', text)
        hour = None
        if time_match:
            hour = int(time_match.group(1))
            if hour < 6 or hour >= 22:
                is_night = True

        return {
            "is_night_shift": is_night,
            "is_shift_change": is_shift_change,
            "hour": hour,
        }

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
