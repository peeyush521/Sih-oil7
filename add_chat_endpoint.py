import re

with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# The chat endpoint to insert
chat_endpoint = '''
# --- Chat endpoint ---
from pydantic import BaseModel as PydanticBaseModel

class ChatRequest(PydanticBaseModel):
    question: str

@app.post("/api/chat")
def chat_with_system(request: ChatRequest):
    """Conversational chatbot that answers questions about safety data."""
    question = request.question.strip().lower()
    
    if not all_processed_reports:
        return {"answer": "No reports have been loaded yet. Please load some reports first by clicking 'Load next report'."}
    
    # Build context from all loaded reports
    total = len(all_processed_reports)
    precursors = [r for r in all_processed_reports if r.get("is_precursor")]
    non_precursors = [r for r in all_processed_reports if not r.get("is_precursor")]
    
    # Location stats
    loc_counts = {}
    loc_risk = {}
    for r in all_processed_reports:
        for loc in r["extracted_entities"].get("locations", []):
            loc_counts[loc] = loc_counts.get(loc, 0) + 1
            if loc not in loc_risk:
                loc_risk[loc] = []
            loc_risk[loc].append(r["risk_data"]["score"])
    
    # Equipment stats
    equip_counts = {}
    equip_risk = {}
    for r in all_processed_reports:
        for eq in r["extracted_entities"].get("equipment", []):
            equip_counts[eq] = equip_counts.get(eq, 0) + 1
            if eq not in equip_risk:
                equip_risk[eq] = []
            equip_risk[eq].append(r["risk_data"]["score"])
    
    # Hazard stats
    hazard_counts = {}
    for r in all_processed_reports:
        for haz in r["extracted_entities"].get("hazards", []):
            hazard_counts[haz] = hazard_counts.get(haz, 0) + 1
    
    # Build structured context
    context = {
        "total_reports": total,
        "precursors_detected": len(precursors),
        "locations": {k: {"count": v, "avg_risk": round(sum(loc_risk.get(k, [0])) / max(len(loc_risk.get(k, [1])), 1))} for k, v in sorted(loc_counts.items(), key=lambda x: x[1], reverse=True)},
        "equipment": {k: {"count": v, "avg_risk": round(sum(equip_risk.get(k, [0])) / max(len(equip_risk.get(k, [1])), 1))} for k, v in sorted(equip_counts.items(), key=lambda x: x[1], reverse=True)},
        "hazards": dict(sorted(hazard_counts.items(), key=lambda x: x[1], reverse=True)),
        "precursor_reports": [{"id": r["report"]["id"], "text": r["report"]["text"], "score": r["risk_data"]["score"], "trajectory": r["risk_data"]["trajectory"], "equipment": r["extracted_entities"].get("equipment", []), "locations": r["extracted_entities"].get("locations", [])} for r in precursors],
        "latest_report": all_processed_reports[-1]["report"] if all_processed_reports else None,
        "latest_risk": all_processed_reports[-1]["risk_data"]["score"] if all_processed_reports else 0,
    }
    
    # Try Gemini API
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if GEMINI_AVAILABLE and api_key:
        try:
            answer = _chat_with_gemini(question, context)
            return {"answer": answer}
        except Exception as e:
            print(f"[Chat] Gemini failed: {e}, using rule-based fallback")
    
    # Rule-based fallback
    answer = _chat_rule_based(question, context)
    return {"answer": answer}


def _chat_with_gemini(question: str, context: dict) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    prompt = f"""You are SAFEGUARD AI, an industrial safety chatbot for Oil India Limited's Duliajan facility in Assam.

You have access to the following safety data from the facility:

{json.dumps(context, indent=2, default=str)}

A safety officer or plant manager is asking you a question. Answer it using the data above.

Rules:
- Be specific — use actual equipment names (PUMP_104, FORKLIFT, etc.), location names, and risk scores from the data
- If asked about danger zones, list the locations with highest incident counts and risk scores
- If asked about what to do next, give 2-3 actionable recommendations based on the precursor data
- If asked about most hazardous equipment or location, rank them by incident count and average risk score
- Keep answers under 100 words
- Use plain language, not jargon
- Be direct and action-oriented
- Do NOT use markdown formatting
"""
    try:
        client = google_genai.Client(api_key=api_key)
        response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
        return response.text.strip()
    except NameError:
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=api_key)
        model = legacy_genai.GenerativeModel("gemini-3.6-flash")
        response = model.generate_content(prompt)
        return response.text.strip()


def _chat_rule_based(question: str, context: dict) -> str:
    """Rule-based chatbot fallback when Gemini is unavailable."""
    q = question.lower()
    
    # Most hazardous location
    if any(w in q for w in ["hazardous", "danger", "dangerous", "risk", "worst", "unsafe"]):
        if "location" in q or "zone" in q or "area" in q or "place" in q:
            locs = context.get("locations", {})
            if not locs:
                return "No location data available yet."
            lines = []
            for loc, data in list(locs.items())[:5]:
                risk_level = "HIGH" if data["avg_risk"] >= 70 else "MEDIUM" if data["avg_risk"] >= 40 else "LOW"
                lines.append(f"- {loc}: {data['count']} incidents, avg risk {data['avg_risk']}/100 ({risk_level})")
            return f"The most dangerous locations at Duliajan facility are:\\n" + "\\n".join(lines) + "\\n\\nRecommendation: Increase safety inspections and deploy additional PPE at HIGH risk locations."
        
        if "equipment" in q or "machine" in q or "pump" in q:
            equips = context.get("equipment", {})
            if not equips:
                return "No equipment data available yet."
            lines = []
            for eq, data in list(equips.items())[:5]:
                risk_level = "HIGH" if data["avg_risk"] >= 70 else "MEDIUM" if data["avg_risk"] >= 40 else "LOW"
                lines.append(f"- {eq}: {data['count']} incidents, avg risk {data['avg_risk']}/100 ({risk_level})")
            return f"The most hazardous equipment identified:\\n" + "\\n".join(lines) + "\\n\\nRecommendation: Schedule immediate maintenance for HIGH risk equipment."
        
        # General most hazardous
        precursors = context.get("precursor_reports", [])
        if precursors:
            lines = []
            for p in precursors[:3]:
                lines.append(f"- {p['id']}: Risk {p['score']}/100 ({p['trajectory']}) — {p['text'][:80]}")
            return f"The most hazardous incidents detected (precursors):\\n" + "\\n".join(lines) + f"\\n\\n{context['precursors_detected']} precursor(s) detected out of {context['total_reports']} reports. Immediate intervention required."
        return f"No precursors detected yet from {context['total_reports']} reports."
    
    # What to do next
    if any(w in q for w in ["what to do", "next", "action", "recommend", "should", "prevent"]):
        precursors = context.get("precursor_reports", [])
        actions = []
        
        # Check for high-risk equipment
        equips = context.get("equipment", {})
        for eq, data in equips.items():
            if data["avg_risk"] >= 70:
                actions.append(f"URGENT: Shut down and inspect {eq} immediately (avg risk {data['avg_risk']}/100)")
            elif data["avg_risk"] >= 40:
                actions.append(f"Schedule maintenance for {eq} within 48 hours (avg risk {data['avg_risk']}/100)")
        
        # Check for high-risk locations
        locs = context.get("locations", {})
        for loc, data in locs.items():
            if data["avg_risk"] >= 70:
                actions.append(f"Restrict access to {loc} — {data['count']} incidents with high risk")
            elif data["count"] >= 3:
                actions.append(f"Increase safety patrols at {loc} ({data['count']} incidents)")
        
        # Check for unresolved precursors
        if precursors:
            actions.append(f"Investigate {len(precursors)} active precursor alert(s)")
        
        if not actions:
            actions.append("Continue routine monitoring — no immediate actions required")
            actions.append("Review closed corrective actions for effectiveness")
            actions.append("Update safety training based on recent incident patterns")
        
        return "Recommended actions based on current data:\\n" + "\\n".join(f"{i+1}. {a}" for i, a in enumerate(actions[:6]))
    
    # Danger zones
    if any(w in q for w in ["danger", "zone", "where", "hotspot", "cluster"]):
        locs = context.get("locations", {})
        if not locs:
            return "No location data available yet."
        
        danger = []
        watch = []
        safe = []
        for loc, data in locs.items():
            if data["avg_risk"] >= 70 or data["count"] >= 4:
                danger.append(f"RED ZONE: {loc} — {data['count']} incidents, avg risk {data['avg_risk']}/100")
            elif data["avg_risk"] >= 40 or data["count"] >= 2:
                watch.append(f"YELLOW ZONE: {loc} — {data['count']} incidents, avg risk {data['avg_risk']}/100")
            else:
                safe.append(f"{loc} — {data['count']} incident(s), low risk")
        
        result = "Facility Danger Zone Assessment:\\n\\n"
        if danger:
            result += "CRITICAL ZONES (immediate action):\\n" + "\\n".join(f"  {d}" for d in danger) + "\\n\\n"
        if watch:
            result += "WATCH ZONES (increased monitoring):\\n" + "\\n".join(f"  {w}" for w in watch) + "\\n\\n"
        if safe:
            result += "LOW RISK ZONES:\\n" + "\\n".join(f"  {s}" for s in safe[:3])
        return result
    
    # Stats / summary
    if any(w in q for w in ["summary", "stats", "overview", "status", "how many", "total"]):
        return f"Facility Safety Summary:\\n- Total reports analyzed: {context['total_reports']}\\n- Precursors detected: {context['precursors_detected']}\\n- Unique locations: {len(context.get('locations', {}))}\\n- Equipment types tracked: {len(context.get('equipment', {}))}\\n- Hazard types found: {len(context.get('hazards', {}))}\\n- Latest risk score: {context.get('latest_risk', 0)}/100"
    
    # Default
    return f"I can help you with safety data questions. Try asking:\\n- Which location is most hazardous?\\n- What are the danger zones?\\n- What should I do next?\\n- Give me a summary of the current status\\n- Which equipment is most dangerous?\\n\\nCurrently analyzing {context['total_reports']} reports with {context['precursors_detected']} precursor alert(s)."
'''

# Insert before DIST_DIR
marker = 'DIST_DIR = Path("frontend/dist")'
if marker in code:
    code = code.replace(marker, chat_endpoint + '\n\n\n' + marker)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print('Chat endpoint added successfully')
else:
    print('ERROR: DIST_DIR marker not found')
