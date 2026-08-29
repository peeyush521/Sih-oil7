"""
SIH26165 - Data Loader (Oil India Edition)
Loads the real Indian oil & gas safety dataset (oil_safety_dataset_full.json)
and converts it into the same column schema the rest of the pipeline
(classification_engine.py, main.py) already expects:
    Data, Countries, Local, Industry Sector, Accident Level,
    Potential Accident Level, Genre, Employee or Third Party,
    Critical Risk, Description, Corrective Action, Action Status

This replaces the old generate_ihm_stefanini_mock_dataset() generic
mining-sector synthetic data with our actual Oil India field reports.
"""

import json
import os
import re
import pandas as pd


# ---------- Hazard category inference (-> "Critical Risk" column) ----------
# Rule-based labeler: assigns a primary hazard category per report by
# keyword match. Order matters -- more specific / severe categories first.
HAZARD_CATEGORY_RULES = [
    ("Gas Leak / H2S",       [r"\bh2s\b", "gas leak", "gas smell", "gas odor", "hydrocarbon odor", "gas blowout", "dizziness", "inhalation"]),
    ("Fire / Explosion",     ["fire", "explosion", "flashback", "bleve", "ignit", "blast"]),
    ("Blowout / Well Control",["blowout", "bop ", "annular preventer", "well control", "wellhead"]),
    ("Pressure / Temperature Excursion", ["overpressur", "psv", "pressure safety valve", "relief valve", "rupture disc",
                                            "pressure spike", "pressure drop", "pressure gauge", "overtemperature",
                                            "high temperature alarm", "temperature control", "seepage"]),
    ("Electrical",           ["electrical", "shock", "arc flash", "switchgear", "junction box", "earthing"]),
    ("Confined Space",       ["confined space", "oxygen level", "vessel manhole", "gas test"]),
    ("Crane / Lifting",      ["crane", "load swing", "sling", "rigging", "wire rope"]),
    ("Fall / Height",        ["fell", "fall", "scaffold", "platform", "height", "guard rail"]),
    ("Slip / Near Miss",     ["slip", "spill", "leak"]),
    ("Vehicle / Transport",  ["vehicle", "skid", "road", "helicopter", "helideck", "transfer basket", "forklift", "pedestrian", "spotter"]),
    ("Chemical Exposure",    ["chemical", "corrosive", "splash", "skin contact", "crude oil mist"]),
    ("Ergonomic",            ["strain", "manual lifting", "manual handling", "shoulder", "back strain"]),
    ("Weather",              ["weather", "wind", "sea condition", "storm"]),
    ("Structural / Corrosion",["corrosion", "structural", "tube thinning", "seal", "cracked", "worn out", "degraded"]),
    ("PPE Violation",        ["harness", "hard hat", "ppe", "faceshield"]),
    ("Cyber / Security",     ["scada", "remote command", "cyber"]),
    ("Equipment Malfunction",["erratic", "failed", "malfunction", "trip", "anomaly", "vibration"]),
    ("Routine / Observation",["toolbox talk", "muster point", "calibration", "routine", "shift log review",
                                "inspection completed", "stock check", "no abnormalities", "no anomalies",
                                "checked. no issue", "running well", "within tolerance"]),
]


def _infer_critical_risk(text: str) -> str:
    text_lower = text.lower()
    for category, keywords in HAZARD_CATEGORY_RULES:
        for kw in keywords:
            if re.search(kw, text_lower):
                return category
    return "Other Risk"


# ---------- Severity -> Accident Level bands (Roman numerals, I=lowest) ----
def _severity_to_level(severity: int) -> str:
    if severity <= 2:
        return "I"
    elif severity <= 4:
        return "II"
    elif severity <= 6:
        return "III"
    elif severity <= 8:
        return "IV"
    else:
        return "V"


def _potential_level(severity: int, report_type: str) -> str:
    # Near-misses and unsafe-conditions are reports of what COULD have
    # happened -- their potential severity is treated as higher than the
    # actual outcome recorded, matching real safety-science convention
    # (Potential Accident Level >= Accident Level).
    bump = 2 if report_type in ("near-miss", "unsafe-condition") else 0
    bumped = min(severity + bump, 10)
    return _severity_to_level(bumped)


# ---------- Action status inference ----------
CLOSED_SIGNS = [
    "repaired", "replaced", "fixed", "resolved", "restored", "no further",
    "no repeat", "no recurrence", "running normal", "running well",
    "closed", "cleared", "normalized", "no abnormalities", "no anomalies",
    "since repair", "completed", "since replacement", "still not repaired",
]


def _infer_action_status(text: str, report_type: str) -> str:
    text_lower = text.lower()
    if report_type == "observation":
        return "Closed"
    if any(sign in text_lower for sign in CLOSED_SIGNS) and "still not" not in text_lower:
        return "Closed"
    if "still not" in text_lower or "overdue" in text_lower or "not scheduled" in text_lower:
        return "Open"
    if report_type in ("unsafe-condition", "unsafe-act") and any(
        w in text_lower for w in ["fatal", "hospitalized", "critical injury", "explosion", "blowout"]
    ):
        return "Open"
    return "Open" if report_type != "near-miss" else "Closed"


def _convert_record(raw: dict) -> dict:
    """Map one Oil India record (id/date/location/equipment/text/severity/type)
    into the pipeline's expected column schema."""
    severity = raw.get("severity", 1)
    report_type = raw.get("type", "observation")
    text = raw.get("text", "")

    return {
        "Data": f"{raw['date']} 09:00:00",
        "Countries": "India",
        "Local": raw.get("location", "Unknown Location"),
        "Industry Sector": "Oil & Gas",
        "Accident Level": _severity_to_level(severity),
        "Potential Accident Level": _potential_level(severity, report_type),
        "Genre": "Not Specified",
        "Employee or Third Party": "Employee",
        "Critical Risk": raw.get("equipment_hazard_override") or _infer_critical_risk(text),
        "Description": text,
        "Corrective Action": "See report notes",
        "Action Status": _infer_action_status(text, report_type),
        # Extra fields kept for downstream use (ignored by code that doesn't need them)
        "Report ID": raw.get("id"),
        "Equipment": raw.get("equipment", "Unknown"),
        "Severity Raw": severity,
        "Report Type": report_type,
        "Shift": raw.get("shift", "unspecified"),
        "Root Cause Tag": raw.get("root_cause_tag", "unspecified"),
    }


def build_oil_india_dataset(
    json_path: str = "oil_safety_dataset_full.json",
    csv_out_path: str = "real_industrial_safety_data.csv",
) -> str:
    """Reads the merged Oil India JSON dataset and writes it out as a CSV in
    the same column schema the rest of the pipeline (data_loader consumers)
    already expect, so no changes are needed in main.py / classification_engine.py."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(
            f"Could not find {json_path}. Place oil_safety_dataset_full.json "
            f"in the project root (same folder as main.py)."
        )

    with open(json_path, "r", encoding="utf-8") as f:
        raw_records = json.load(f)

    converted = [_convert_record(r) for r in raw_records]
    # Keep chronological order so temporal/graph logic sees reports in
    # a sensible sequence, matching how the demo "Load next report" flow
    # is meant to be experienced.
    converted.sort(key=lambda r: r["Data"])

    df = pd.DataFrame(converted)
    df.to_csv(csv_out_path, index=False)
    return csv_out_path


def load_industrial_dataset(file_path: str = "real_industrial_safety_data.csv") -> list:
    """Drop-in replacement for the old function name/signature used by main.py
    and classification_engine.py. Regenerates the CSV from the Oil India JSON
    if it doesn't exist yet or if the JSON is newer than the CSV."""
    json_path = "oil_safety_dataset_full.json"

    needs_rebuild = (
        not os.path.exists(file_path)
        or (os.path.exists(json_path) and os.path.getmtime(json_path) > os.path.getmtime(file_path))
    )
    if needs_rebuild:
        build_oil_india_dataset(json_path=json_path, csv_out_path=file_path)

    return pd.read_csv(file_path).to_dict(orient="records")


if __name__ == "__main__":
    path = build_oil_india_dataset()
    records = pd.read_csv(path).to_dict(orient="records")
    print(f"Built {path} with {len(records)} records from Oil India dataset.")
    print("\nCritical Risk category distribution:")
    from collections import Counter
    print(Counter(r["Critical Risk"] for r in records))
    print("\nAction Status distribution:")
    print(Counter(r["Action Status"] for r in records))