from datetime import datetime, timedelta
import math

# --- ADJUSTABLE THRESHOLDS ---
# Safety officers can tune these without code changes
THRESHOLDS = {
    "precursor_critical": 70,    # Score >= this = CRITICAL precursor
    "precursor_warning": 40,     # Score >= this = WARNING
    "night_shift_bonus": 8,      # Extra points for night shift incidents
    "shift_change_bonus": 5,     # Extra points for shift-change incidents
    "cross_equipment_bonus": 12, # Bonus for multiple equipment types failing
    "quantity_threshold": 5,     # Bonus if dangerous quantities detected
    "max_score": 100,
    "time_decay_halflife_days": 14,  # Reports older than this count half as much
}


def _time_decay_weight(report_date_str, current_date=None):
    """Calculate time-decay weight. Recent reports matter more.
    Weight = 2^(-age_days / halflife)
    A report from yesterday = ~1.0, from 14 days ago = ~0.5, from 30 days ago = ~0.25
    """
    if current_date is None:
        current_date = datetime.now()

    try:
        if "T" in str(report_date_str):
            report_date = datetime.fromisoformat(str(report_date_str).replace("Z", "+00:00"))
        else:
            report_date = datetime.strptime(str(report_date_str)[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return 0.5  # Default weight if date is unparseable

    age_days = max((current_date - report_date).days, 0)
    halflife = THRESHOLDS["time_decay_halflife_days"]
    weight = math.pow(2, -age_days / halflife)
    return round(weight, 3)


def _cross_equipment_correlation(current_entities, related_reports):
    """Detect if multiple DIFFERENT equipment types are failing — systemic issue."""
    current_eq = set(current_entities.get("equipment", []))
    all_equipment = set()
    for rep in related_reports:
        for ev in rep.get("evidence", []):
            if "Same equipment" in ev:
                eq_name = ev.split("(")[1].rstrip(")") if "(" in ev else ""
                if eq_name:
                    all_equipment.add(eq_name)

    # Count distinct equipment types across all related events
    distinct_equipment = set(all_equipment) | current_eq
    if len(distinct_equipment) >= 3:
        return {
            "correlated": True,
            "count": len(distinct_equipment),
            "equipment": list(distinct_equipment)[:5],
            "message": f"{len(distinct_equipment)} different equipment types showing issues — possible systemic degradation",
        }
    return {"correlated": False, "count": len(distinct_equipment), "equipment": [], "message": ""}


def calculate_risk(report_id, current_report, related_reports):
    base_severity = current_report["entities"].get("severity", 1)
    urgency_score = current_report["entities"].get("urgency_score", 0)
    shift_info = current_report["entities"].get("shift_info", {})
    quantities = current_report["entities"].get("quantities", [])

    points_frequency = 0
    points_recency = 0
    points_severity_trend = 0
    points_semantic = 0
    points_equipment = 0
    points_location = 0
    points_unresolved = 0
    points_sif = 0
    points_urgency = 0
    points_night_shift = 0
    points_shift_change = 0
    points_cross_equipment = 0
    points_quantity = 0

    evidence_log = []
    deltas = {}

    if len(related_reports) > 0:
        # --- TIME-DECAY WEIGHTED FREQUENCY ---
        # Instead of raw count, weight each report by recency
        weighted_count = 0
        report_date_str = current_report.get("date", "")
        for rep in related_reports:
            rep_date = rep.get("date", "")
            weight = _time_decay_weight(rep_date)
            weighted_count += weight

        # Score frequency based on weighted count
        points_frequency = min(round(weighted_count * 5), 20)
        if weighted_count > 1:
            evidence_log.append(f"{len(related_reports)} related events (recency-weighted: {weighted_count:.1f})")
        else:
            evidence_log.append(f"{len(related_reports)} related event(s)")
        deltas["Frequency"] = points_frequency

        # --- TIME-DECAY RECENCY ---
        most_recent_weight = _time_decay_weight(related_reports[0].get("date", ""))
        points_recency = round(most_recent_weight * 15)  # Max 15 for most recent
        deltas["Recency"] = points_recency

        prev_severity = related_reports[0]["severity"]
        if base_severity > prev_severity:
            points_severity_trend = 15
            evidence_log.append(f"Severity escalating ({prev_severity} -> {base_severity})")
            deltas["Severity Trend"] = points_severity_trend
        elif base_severity == prev_severity and len(related_reports) >= 2:
            points_severity_trend = 5
            deltas["Severity Trend"] = points_severity_trend

        points_semantic = 5
        deltas["Semantic Similarity"] = points_semantic

        open_actions = sum(1 for r in related_reports if r.get("action_status") == "Open")
        if open_actions > 0:
            points_unresolved = 15
            evidence_log.append(f"{open_actions} unresolved corrective action(s)")
            deltas["Unresolved Actions"] = points_unresolved

    # Equipment recurrence
    shared_equipment = set()
    for rep in related_reports:
        for ev in rep["evidence"]:
            if "Same equipment" in ev:
                shared_equipment.add(ev)
    if shared_equipment:
        points_equipment = 10
        evidence_log.append("Same equipment recurrence")
        deltas["Equipment Recurrence"] = points_equipment

    # Location recurrence
    shared_location = set()
    for rep in related_reports:
        for ev in rep["evidence"]:
            if "Same location" in ev:
                shared_location.add(ev)
    if shared_location:
        points_location = 5
        evidence_log.append("Location recurrence")
        deltas["Location Recurrence"] = points_location

    # SIF Pathway detection
    hazards = current_report["entities"].get("hazards", [])
    sif_category = "None"
    if any(h in ["OIL_LEAK", "METHANE_HAZARD", "GAS_HAZARD", "spill", "leak", "hydrocarbon release"] for h in hazards):
        sif_category = "Loss of Control"
        points_sif = 10
    elif any(h in ["SLIP_HAZARD", "fall", "trip"] for h in hazards):
        sif_category = "Exposure"
        points_sif = 10
    elif any(h in ["PRESSURE_HAZARD", "vibration", "ELECTRICAL_HAZARD", "FIRE_HAZARD"] for h in hazards):
        sif_category = "Energy Release"
        points_sif = 15

    if points_sif > 0:
        evidence_log.append(f"SIF Pathway detected ({sif_category})")
        deltas["SIF Pathway"] = points_sif

    # Urgency score from NLP sentiment analysis
    if urgency_score > 0:
        points_urgency = min(urgency_score, 10)
        if points_urgency >= 6:
            evidence_log.append("High urgency language detected")
        deltas["Urgency Score"] = points_urgency

    # --- NEW: NIGHT SHIFT BONUS ---
    if shift_info.get("is_night_shift"):
        points_night_shift = THRESHOLDS["night_shift_bonus"]
        evidence_log.append("Night shift incident (higher statistical risk)")
        deltas["Night Shift"] = points_night_shift

    # --- NEW: SHIFT CHANGE BONUS ---
    if shift_info.get("is_shift_change"):
        points_shift_change = THRESHOLDS["shift_change_bonus"]
        evidence_log.append("Shift change period (handover risk)")
        deltas["Shift Change"] = points_shift_change

    # --- NEW: CROSS-EQUIPMENT CORRELATION ---
    cross_eq = _cross_equipment_correlation(current_report["entities"], related_reports)
    if cross_eq["correlated"]:
        points_cross_equipment = THRESHOLDS["cross_equipment_bonus"]
        evidence_log.append(cross_eq["message"])
        deltas["Cross-Equipment"] = points_cross_equipment

    # --- NEW: QUANTITY-BASED ALERTING ---
    dangerous_quantities = []
    for q in quantities:
        # High LEL percentage
        if q["type"] == "percent" and q["value"] >= 10:
            dangerous_quantities.append(q)
        # High vibration
        if q["type"] == "vibration_mm_s" and q["value"] >= 4.0:
            dangerous_quantities.append(q)
        # High temperature
        if q["type"] == "temperature_c" and q["value"] >= 80:
            dangerous_quantities.append(q)
        # Large spills
        if q["type"] == "volume" and q["value"] >= 20:
            dangerous_quantities.append(q)

    if dangerous_quantities:
        points_quantity = THRESHOLDS["quantity_threshold"]
        qty_summary = ", ".join([f"{q['raw']}" for q in dangerous_quantities[:3]])
        evidence_log.append(f"Dangerous quantities detected: {qty_summary}")
        deltas["Quantity Alert"] = points_quantity

    # --- CALCULATE FINAL SCORE ---
    risk_score = (
        (base_severity * 10)
        + points_frequency
        + points_recency
        + points_severity_trend
        + points_semantic
        + points_equipment
        + points_location
        + points_unresolved
        + points_sif
        + points_urgency
        + points_night_shift
        + points_shift_change
        + points_cross_equipment
        + points_quantity
    )
    risk_score = min(risk_score, THRESHOLDS["max_score"])

    # --- TRAJECTORY ---
    trajectory = "STABLE"
    if risk_score >= THRESHOLDS["precursor_critical"]:
        if len(related_reports) > 0 and base_severity >= related_reports[0]["severity"]:
            trajectory = "ESCALATING"
        else:
            trajectory = "STABLE"
    elif risk_score < THRESHOLDS["precursor_warning"]:
        trajectory = "DECREASING"

    # --- RISK LEVEL ---
    if risk_score >= THRESHOLDS["precursor_critical"]:
        risk_level = "CRITICAL"
    elif risk_score >= THRESHOLDS["precursor_warning"]:
        risk_level = "WARNING"
    else:
        risk_level = "NORMAL"

    return {
        "score": risk_score,
        "trajectory": trajectory,
        "risk_level": risk_level,
        "evidence": evidence_log,
        "sif_category": sif_category,
        "deltas": deltas,
        "quantities_detected": quantities,
        "dangerous_quantities": dangerous_quantities,
        "shift_info": shift_info,
        "thresholds": THRESHOLDS,
    }


def get_intervention_recommendation(risk_data, entities):
    score = risk_data["score"]
    shift = risk_data.get("shift_info", {})
    quantities = risk_data.get("dangerous_quantities", [])

    if score >= 75:
        eq = ", ".join(entities.get("equipment", ["the equipment"])) if entities.get("equipment") else "the equipment"
        loc = ", ".join(entities.get("locations", ["the area"])) if entities.get("locations") else "the area"
        actions = [
            f"Inspect {eq} immediately.",
            f"Restrict access to {loc}.",
            "Verify floor contamination and clean up.",
            "Close any previous unresolved corrective actions.",
        ]
        if shift.get("is_night_shift"):
            actions.append("Consider additional night-shift supervision.")
        if quantities:
            actions.append(f"Verify quantity readings: {', '.join(q['raw'] for q in quantities[:3])}")
        return actions
    elif score >= 50:
        return [
            "Schedule maintenance check within 48 hours.",
            "Monitor area for further hazards.",
        ]
    else:
        return ["Log report for routine review."]
