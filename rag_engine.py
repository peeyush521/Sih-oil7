"""
RAG Pipeline — LLM-Powered Root Cause Analysis (Upgraded)
Uses retrieval-augmented generation with similar incident retrieval
to provide deep root cause analysis + corrective actions + regulatory references.
"""
import os
import json


REGULATORY_REFERENCES = {
    "Electrical": {
        "osha": "OSHA 29 CFR 1910.303 — General Requirements for Electrical",
        "dgms": "DGMS Circular 07/2018 — Electrical Safety in Mines",
        "oil_india": "OIL HSE Manual §4.3 — Electrical Isolation & LOTO",
        "action": "Implement LOTO procedures before maintenance",
        "penalty": "Non-compliance can result in work stoppage and penalty under Factories Act §36"
    },
    "Chemical/Gas Release": {
        "osha": "OSHA 29 CFR 1910.1200 — Hazard Communication Standard",
        "dgms": "DGMS Circular 04/2019 — Gas Testing & Monitoring",
        "oil_india": "OIL HSE Manual §5.1 — Hazardous Substance Handling",
        "action": "Install continuous gas monitoring and auto-shutdown systems",
        "penalty": "Mandatory reporting under Environment Protection Act §6"
    },
    "Fall/Slip": {
        "osha": "OSHA 29 CFR 1926.501 — Fall Protection Requirements",
        "dgms": "DGMS Circular 12/2017 — Working at Heights",
        "oil_india": "OIL HSE Manual §6.2 — Work at Height Procedure",
        "action": "Install guardrails, deploy fall-arrest systems, mandatory harness",
        "penalty": "Stop-work authority invoked under OIL Safety Protocol §2.4"
    },
    "Thermal/Burn": {
        "osha": "OSHA 29 CFR 1910.132 — General PPE Requirements",
        "dgms": "DGMS Circular 03/2020 — Thermal Protection Standards",
        "oil_india": "OIL HSE Manual §7.1 — Heat Stress & Burn Prevention",
        "action": "Provide heat-resistant PPE, install thermal barriers",
        "penalty": "Medical surveillance required under Factories Act §48A"
    },
    "Mechanical/Crush": {
        "osha": "OSHA 29 CFR 1910.212 — Machine Guarding",
        "dgms": "DGMS Circular 09/2019 — Mechanical Equipment Safety",
        "oil_india": "OIL HSE Manual §8.3 — Machinery Guarding Standards",
        "action": "Install machine guards, proximity sensors, emergency stops",
        "penalty": "Equipment seizure under DGMS inspection powers"
    },
    "Cut/Abrasion": {
        "osha": "OSHA 29 CFR 1910.138 — Hand Protection",
        "dgms": "DGMS Circular 05/2018 — Personal Protective Equipment",
        "oil_india": "OIL HSE Manual §9.1 — PPE Selection & Usage",
        "action": "Provide cut-resistant gloves, tool inspection program",
        "penalty": "PPE non-compliance under General Safety Rules §3.2"
    },
    "Manual/Mechanical": {
        "osha": "OSHA 29 CFR 1910.176 — Materials Handling",
        "dgms": "DGMS Circular 08/2020 — Manual Handling Ergonomics",
        "oil_india": "OIL HSE Manual §10.2 — Lifting & Handling Procedure",
        "action": "Implement mechanical lifting aids, weight assessment SOP",
        "penalty": "Ergonomic assessment mandatory under Factories Act §45B"
    },
}


CAUSAL_CHAIN_TEMPLATE = {
    "immediate_cause": "Direct action or condition that led to the incident",
    "contributing_factors": [
        "Equipment condition or failure mode",
        "Human factors (fatigue, training, complacency)",
        "Organizational factors (procedures, supervision, culture)",
        "Environmental factors (weather, lighting, noise)"
    ],
    "root_cause": "The deepest systemic reason — if fixed, would prevent recurrence"
}


def generate_rag_analysis(report_text, classification, entities, risk_data, related_reports, graph_engine):
    """Generate a comprehensive root cause analysis using RAG pipeline."""
    similar_cases = _retrieve_similar_cases(report_text, entities, related_reports)
    context = _build_rag_context(report_text, classification, entities, risk_data, similar_cases)
    analysis = _generate_with_llm(context)
    
    report_class = classification.get("class", "Unknown")
    regulation = REGULATORY_REFERENCES.get(report_class, {
        "osha": "OSHA General Duty Clause — Section 5(a)(1)",
        "dgms": "DGMS General Safety Requirements",
        "oil_india": "OIL HSE Manual — General Safety Provisions",
        "action": "Conduct site-specific safety assessment",
        "penalty": "Non-compliance reportable under General Safety Rules"
    })
    
    # Build the causal chain
    causal_chain = _build_causal_chain(entities, risk_data, similar_cases, classification)
    
    # Build action priority matrix
    action_matrix = _build_action_priority(analysis.get("corrective_actions", []), risk_data, entities)
    
    return {
        "root_cause": analysis["root_cause"],
        "corrective_actions": analysis["corrective_actions"],
        "regulatory_reference": regulation,
        "similar_cases_count": len(similar_cases),
        "similar_cases": similar_cases[:5],
        "confidence": analysis.get("confidence", "Medium"),
        "contributing_factors": analysis.get("contributing_factors", []),
        "causal_chain": causal_chain,
        "action_priority_matrix": action_matrix,
        "sif_pathway_analysis": _analyze_sif_pathway(entities, risk_data),
        "recurrence_risk": _assess_recurrence_risk(similar_cases, risk_data),
    }


def _retrieve_similar_cases(report_text, entities, related_reports):
    """Retrieve and rank similar historical cases."""
    similar = []
    for rep in related_reports:
        score = 0
        evidence_details = []
        for ev in rep.get("evidence", []):
            if "semantic similarity" in ev.lower():
                try:
                    s = float(ev.split("(")[1].split("%")[0]) / 100 * 0.4
                    score += s
                    evidence_details.append(f"Text similarity: {ev}")
                except:
                    score += 0.2
            elif "Same equipment" in ev:
                score += 0.3
                evidence_details.append(ev)
            elif "Same location" in ev:
                score += 0.2
                evidence_details.append(ev)
        if score > 0.1:
            similar.append({
                "id": rep.get("id", "Unknown"),
                "date": rep.get("date", ""),
                "text": rep.get("text", "")[:300],
                "severity": rep.get("severity", 1),
                "similarity_score": round(score, 2),
                "evidence": rep.get("evidence", []),
                "evidence_details": evidence_details,
                "risk_score": rep.get("risk_score", 0)
            })
    similar.sort(key=lambda x: x["similarity_score"], reverse=True)
    return similar[:8]


def _build_rag_context(report_text, classification, entities, risk_data, similar_cases):
    """Build a rich context for the LLM."""
    similar_text = ""
    for i, case in enumerate(similar_cases[:5], 1):
        similar_text += (
            f"\nCase {i}: {case['id']} (Date: {case['date']}, Severity: {case['severity']}, "
            f"Similarity: {case['similarity_score']})"
            f"\n  Report: {case['text'][:200]}"
        )
    
    return {
        "incident_report": report_text,
        "classification": classification.get("class", "Unknown"),
        "confidence": classification.get("confidence", 0),
        "is_novel": classification.get("is_novel", False),
        "equipment": entities.get("equipment", []),
        "locations": entities.get("locations", []),
        "hazards": entities.get("hazards", []),
        "unsafe_acts": entities.get("unsafe_acts", []),
        "severity": entities.get("severity", 1),
        "risk_score": risk_data.get("score", 0),
        "risk_level": risk_data.get("risk_level", "NORMAL"),
        "sif_pathway": risk_data.get("sif_category", "None"),
        "trajectory": risk_data.get("trajectory", "STABLE"),
        "evidence": risk_data.get("evidence", []),
        "deltas": risk_data.get("deltas", {}),
        "similar_cases": similar_text if similar_text else "No similar historical cases found.",
        "num_similar": len(similar_cases),
    }


def _generate_with_llm(context):
    """Generate root cause analysis using Gemini LLM or fallback to template."""
    try:
        from google import genai as google_genai
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            client = google_genai.Client(api_key=api_key)
            prompt = f"""You are a senior safety analyst at Oil India Limited's Duliajan facility in Assam.
Analyze this incident report and provide a detailed root cause analysis.

INCIDENT REPORT: "{context['incident_report']}"

CONTEXT:
- Classification: {context['classification']} (confidence: {context['confidence']}%)
- Equipment involved: {context['equipment']}
- Location: {context['locations']}
- Hazards identified: {context['hazards']}
- Unsafe acts: {context.get('unsafe_acts', [])}
- Severity: {context['severity']}/5
- Risk Score: {context['risk_score']}/100 ({context['risk_level']})
- SIF Pathway: {context['sif_pathway']}
- Trajectory: {context['trajectory']}
- Evidence factors: {context['evidence']}
- Similar historical cases: {context['num_similar']}
{context['similar_cases']}

Provide a JSON response with exactly these keys:
{{
  "root_cause": "A detailed 3-5 sentence root cause analysis identifying the deepest systemic reason, not just the immediate cause. Reference the specific equipment, location, and conditions.",
  "immediate_cause": "The direct action or condition that caused the incident (1-2 sentences)",
  "contributing_factors": ["Factor 1 (equipment/system)", "Factor 2 (human/organizational)", "Factor 3 (environmental/procedural)"],
  "corrective_actions": ["Immediate action (within 24hrs)", "Short-term fix (within 1 week)", "Long-term prevention (within 1 month)", "Systemic improvement (policy/procedure change)"],
  "confidence": "High/Medium/Low",
  "sif_prevention_priority": "Explain why this needs immediate attention for SIF prevention (1-2 sentences)"
}}"""
            response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
            text = response.text.strip()
            if "```" in text:
                text = text.split("```")[1].split("```")[0]
            if "json" in text.lower():
                text = text.split("\n", 1)[1] if text.startswith("json") else text
            return json.loads(text)
    except Exception as e:
        print(f"[RAG] LLM failed: {e}, using template analysis")
    
    return _generate_template_analysis(context)


def _generate_template_analysis(context):
    """Generate a detailed template-based analysis when LLM is unavailable."""
    eq = context["equipment"][0] if context["equipment"] else "equipment"
    loc = context["locations"][0] if context["locations"] else "area"
    haz = context["hazards"][0] if context["hazards"] else "unidentified hazard"
    sev = context["severity"]
    score = context["risk_score"]
    traj = context["trajectory"]
    
    # Build root cause based on context
    rc = f"The incident at {loc} involving {eq} was caused by "
    
    if context["is_novel"]:
        rc += f"an unusual combination of factors resulting in a novel {haz} pattern. "
    elif sev >= 4:
        rc += f"critical failure in safety controls designed to prevent {haz}. "
    elif sev >= 3:
        rc += f"insufficient safety barriers against {haz} at {loc}. "
    else:
        rc += f"routine operational hazard ({haz}) that was not adequately controlled. "
    
    rc += f"The root cause is systemic: safety procedures for {eq} at {loc} did not account for "
    
    if "night" in context.get("report_text", "").lower() or any(s.get("is_night_shift") for s in [{}] if False):
        rc += "heightened risks during night-shift operations. "
    elif "contractor" in context.get("report_text", "").lower():
        rc += "third-party contractor supervision gaps. "
    else:
        rc += "cumulative exposure patterns that increase SIF probability over time. "
    
    if traj == "ESCALATING":
        rc += f"CRITICAL: Escalating trajectory ({context.get('report_text', '')[:50]}) indicates systemic degradation. "
    
    # Contributing factors
    cf = []
    if context["hazards"]:
        cf.append(f"Hazard exposure: {context['hazards'][0]} at {loc}")
    if context["equipment"]:
        cf.append(f"Equipment condition: {context['equipment'][0]} — requires inspection")
    if traj == "ESCALATING":
        cf.append("Escalating trend pattern — indicates systemic issue")
    if sev >= 3:
        cf.append(f"High severity ({sev}/5) — potential SIF pathway active")
    if context["unsafe_acts"]:
        cf.append(f"Unsafe act: {context['unsafe_acts'][0]}")
    if not cf:
        cf = [
            f"Equipment maintenance gap at {loc}",
            "Procedural compliance deficiency",
            "Environmental conditions contributing to hazard",
        ]
    
    # Corrective actions by priority
    if sev >= 4:
        ca = [
            f"IMMEDIATE: Stop all work involving {eq} at {loc}. Isolate and lock out.",
            f"Within 24hrs: Complete inspection of {eq}. Deploy additional safety personnel at {loc}.",
            f"Week 1: Review and update SOPs for {eq}. Conduct root cause investigation team meeting.",
            f"Month 1: Install additional safety controls at {loc}. Update risk register and HSE training materials.",
        ]
    elif sev >= 3:
        ca = [
            f"IMMEDIATE: Conduct safety stand-down at {loc}. Brief all personnel on {haz} risk.",
            f"Within 24hrs: Inspect {eq}. Verify PPE compliance and safety barriers.",
            f"Week 1: Update corrective action log. Conduct toolbox talk on {haz} prevention.",
            f"Month 1: Review {eq} maintenance schedule. Update location-specific risk assessment.",
        ]
    else:
        ca = [
            f"Monitor {eq} at {loc} for further incidents. Document in daily safety log.",
            f"Within 48hrs: Verify PPE and barriers at {loc}. Brief shift supervisor.",
            f"Week 1: Review {eq} condition. Update near-miss register.",
            f"Month 1: Incorporate into routine safety audit checklist.",
        ]
    
    # Confidence based on risk score
    if score >= 70:
        conf = "High"
    elif score >= 40:
        conf = "Medium"
    else:
        conf = "Low-Medium"
    
    return {
        "root_cause": rc,
        "corrective_actions": ca,
        "contributing_factors": cf,
        "confidence": conf,
    }


def _build_causal_chain(entities, risk_data, similar_cases, classification):
    """Build a structured causal chain analysis."""
    hazards = entities.get("hazards", [])
    equipment = entities.get("equipment", [])
    locations = entities.get("locations", [])
    unsafe_acts = entities.get("unsafe_acts", [])
    
    immediate_cause = f"Exposure to {hazards[0] if hazards else 'hazard'} involving {equipment[0] if equipment else 'equipment'} at {locations[0] if locations else 'location'}"
    
    contributing = []
    if unsafe_acts:
        contributing.append({"factor": "Human Error", "detail": unsafe_acts[0], "impact": "HIGH"})
    if equipment:
        contributing.append({"factor": "Equipment", "detail": f"{equipment[0]} condition/failure", "impact": "MEDIUM"})
    if risk_data.get("trajectory") == "ESCALATING":
        contributing.append({"factor": "Systemic Pattern", "detail": "Escalating trend detected across multiple reports", "impact": "HIGH"})
    
    similar_count = len(similar_cases)
    if similar_count >= 3:
        contributing.append({"factor": "Historical Pattern", "detail": f"{similar_count} similar incidents found", "impact": "HIGH"})
    
    root = f"The root cause is a combination of equipment and human factors at {locations[0] if locations else 'this location'}. "
    if risk_data.get("score", 0) >= 70:
        root += "This represents a CRITICAL SIF precursor — immediate systemic intervention required."
    elif risk_data.get("score", 0) >= 40:
        root += "Moderate risk level — corrective actions should be prioritized within the week."
    else:
        root += "Lower risk — monitor and incorporate into routine safety management."
    
    return {
        "immediate_cause": immediate_cause,
        "contributing_factors": contributing,
        "root_cause": root,
        "level": "HIGH" if risk_data.get("score", 0) >= 70 else "MEDIUM" if risk_data.get("score", 0) >= 40 else "LOW"
    }


def _build_action_priority(corrective_actions, risk_data, entities):
    """Create a prioritized action matrix with owners and deadlines."""
    priority_map = []
    deadlines = ["Within 4 hours", "Within 24 hours", "Within 1 week", "Within 1 month"]
    owners = ["Shift Supervisor", "Safety Officer", "Maintenance Lead", "Plant Manager"]
    
    for i, action in enumerate(corrective_actions[:4]):
        priority_map.append({
            "action": action,
            "priority": ["CRITICAL", "HIGH", "MEDIUM", "LOW"][min(i, 3)],
            "deadline": deadlines[min(i, 3)],
            "owner": owners[min(i, 3)],
            "status": "OPEN"
        })
    
    return priority_map


def _analyze_sif_pathway(entities, risk_data):
    """Analyze the Serious Injury/Fatality pathway."""
    score = risk_data.get("score", 0)
    hazards = entities.get("hazards", [])
    
    if score >= 70:
        pathway = "ACTIVE — High probability of SIF without immediate intervention"
        severity_potential = "CRITICAL — Uncontrolled energy source or exposure"
    elif score >= 40:
        pathway = "POTENTIAL — SIF pathway could activate if controls degrade"
        severity_potential = "ELEVATED — Degraded safety barriers"
    else:
        pathway = "CONTROLLED — Current controls appear adequate"
        severity_potential = "NORMAL — Standard operational hazard"
    
    return {
        "pathway_status": pathway,
        "severity_potential": severity_potential,
        "immediate_action_required": score >= 70,
        "hazard_type": hazards[0] if hazards else "Unknown"
    }


def _assess_recurrence_risk(similar_cases, risk_data):
    """Assess the risk of recurrence based on similar historical cases."""
    count = len(similar_cases)
    trajectory = risk_data.get("trajectory", "STABLE")
    
    if count >= 5 and trajectory == "ESCALATING":
        return {"level": "VERY HIGH", "message": f"{count} similar incidents with escalating trend — systemic issue confirmed", "recommended": "Immediate root cause investigation and systemic corrective action"}
    elif count >= 3:
        return {"level": "HIGH", "message": f"{count} similar incidents detected — pattern emerging", "recommended": "Review all related incidents and implement preventive measures"}
    elif count >= 1:
        return {"level": "MODERATE", "message": f"{count} similar incident(s) found — monitor closely", "recommended": "Track for further recurrence within 30 days"}
    else:
        return {"level": "LOW", "message": "No similar historical incidents found", "recommended": "Continue standard monitoring and document in risk register"}
