def calculate_risk(report_id: str, current_report: dict, related_reports: list):
    base_severity = current_report["entities"].get("severity", 1)
    
    # Initialize point buckets
    points_frequency = 0
    points_recency = 0
    points_severity_trend = 0
    points_semantic = 0
    points_equipment = 0
    points_location = 0
    points_unresolved = 0
    points_sif = 0
    
    evidence_log = []
    deltas = {}
    
    if len(related_reports) > 0:
        # Frequency
        points_frequency = min(len(related_reports) * 5, 20)
        evidence_log.append(f"{len(related_reports)} related events")
        deltas["Frequency"] = points_frequency
        
        # Recency (dummy calculation based on array index for demo)
        points_recency = 10
        deltas["Recency"] = points_recency
        
        # Severity Trend
        prev_severity = related_reports[0]["severity"]
        if base_severity > prev_severity:
            points_severity_trend = 15
            # NOTE: this string must stay in sync with the substring llm_engine.py
            # checks for ("Severity increased"). It previously said "increasing"
            # which meant the LLM explanation could never detect this signal.
            evidence_log.append("Severity increased from previous report")
            deltas["Severity Trend"] = points_severity_trend
            
        # Semantic Similarity
        # Checked in get_related_reports, if they are here they are related
        points_semantic = 5
        deltas["Semantic Similarity"] = points_semantic
        
        # Unresolved Corrective Action
        open_actions = sum(1 for r in related_reports if r.get("action_status") == "Open")
        if open_actions > 0:
            points_unresolved = 15
            evidence_log.append("Corrective action unresolved")
            deltas["Unresolved Actions"] = points_unresolved
            
    # Equipment Recurrence
    shared_equipment = set()
    for rep in related_reports:
        for ev in rep["evidence"]:
            if "Same equipment" in ev:
                shared_equipment.add(ev)
    if shared_equipment:
        points_equipment = 10
        evidence_log.append("Same equipment recurrence")
        deltas["Equipment Recurrence"] = points_equipment
        
    # Location Recurrence
    shared_location = set()
    for rep in related_reports:
        for ev in rep["evidence"]:
            if "Same location" in ev:
                shared_location.add(ev)
    if shared_location:
        points_location = 5
        deltas["Location Recurrence"] = points_location
        
    # SIF Pathway Severity
    # NOTE: nlp_engine.py always normalizes hazards to UPPERCASE before storing
    # them (e.g. "pressure" -> "PRESSURE"), so these comparisons must be against
    # the normalized uppercase forms, not lowercase demo strings. The lowercase
    # versions here previously meant "Energy Release" could never be detected.
    hazards = current_report["entities"].get("hazards", [])
    sif_category = "None"
    if any(h in ["OIL_LEAK", "GAS_LEAK", "BLOWOUT", "H2S_EXPOSURE"] for h in hazards):
        sif_category = "Loss of Control"
        points_sif = 10
    elif any(h in ["SLIP_HAZARD", "CONFINED_SPACE", "CHEMICAL_EXPOSURE"] for h in hazards):
        sif_category = "Exposure"
        points_sif = 10
    elif any(h in ["PRESSURE", "VIBRATION", "ELECTRICAL", "FIRE", "CRANE_HAZARD", "STRUCTURAL"] for h in hazards):
        sif_category = "Energy Release"
        points_sif = 15
        
    if points_sif > 0:
        evidence_log.append(f"SIF Pathway detected ({sif_category})")
        deltas["SIF Pathway"] = points_sif
        
    # Calculate Risk
    risk_score = (base_severity * 10) + points_frequency + points_recency + points_severity_trend + points_semantic + points_equipment + points_location + points_unresolved + points_sif
    
    # Cap at 100
    risk_score = min(risk_score, 100)
    
    # Trajectory
    trajectory = "STABLE"
    if risk_score > 70 and base_severity >= (related_reports[0]["severity"] if related_reports else 1):
        trajectory = "ESCALATING"
    elif risk_score < 40:
        trajectory = "DECREASING"
        
    return {
        "score": risk_score,
        "trajectory": trajectory,
        "evidence": evidence_log,
        "sif_category": sif_category,
        "deltas": deltas
    }

def get_intervention_recommendation(risk_data, entities):
    if risk_data["score"] >= 75:
        eq = ", ".join(entities.get("equipment", ["the equipment"])) if entities.get("equipment") else "the equipment"
        loc = ", ".join(entities.get("locations", ["the area"])) if entities.get("locations") else "the area"
        return [
            f"Inspect {eq} immediately.",
            f"Restrict access to {loc}.",
            "Verify floor contamination and clean up.",
            "Close any previous unresolved corrective actions."
        ]
    elif risk_data["score"] >= 50:
        return [
            "Schedule maintenance check within 48 hours.",
            "Monitor area for further hazards."
        ]
    else:
        return ["Log report for routine review."]