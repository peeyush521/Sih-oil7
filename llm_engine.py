import os
import json

# Try to import google-genai (new SDK); fall back gracefully
try:
    from google import genai as google_genai
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        import google.generativeai as genai
        GEMINI_AVAILABLE = True
    except ImportError:
        GEMINI_AVAILABLE = False


def generate_llm_explanation(evidence: dict, equipment_list: list, related_reports: list):
    """
    Generates a natural-language explanation of why the risk score changed.
    Uses Google Gemini API if GEMINI_API_KEY is set; otherwise falls back to
    deterministic template-based explanations.
    """
    score = evidence.get("score", 0)
    evidence_logs = evidence.get("evidence", [])
    deltas = evidence.get("deltas", {})
    trajectory = evidence.get("trajectory", "STABLE")
    sif_category = evidence.get("sif_category", "None")

    eq_name = equipment_list[0].upper() if equipment_list else "the area"

    # Build structured context for the LLM
    context = {
        "risk_score": score,
        "trajectory": trajectory,
        "sif_pathway": sif_category,
        "equipment": equipment_list,
        "num_related_events": len(related_reports),
        "evidence": evidence_logs,
        "risk_factors": deltas,
        "recent_reports": [
            {"id": r.get("id", ""), "text": r.get("text", ""), "severity": r.get("severity", 1)}
            for r in related_reports[:5]
        ],
    }

    # Try Gemini API
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if GEMINI_AVAILABLE and api_key:
        try:
            return _generate_with_gemini(context, eq_name, score)
        except Exception as e:
            print(f"[LLM] Gemini API failed ({e}), falling back to template")

    # Fallback: deterministic template
    return _generate_template(score, evidence_logs, equipment_list, related_reports, deltas, trajectory, sif_category)


def _generate_with_gemini(context: dict, eq_name: str, score: int) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")

    prompt = f"""You are a safety risk analysis AI for an oil & gas industrial facility.

Given the following structured risk data, write a clear 2-3 sentence explanation for a safety officer.
Explain WHY the risk score is {context['risk_score']}, what the key factors are, and what should be done.

Risk Data:
{json.dumps(context, indent=2)}

Rules:
- Be specific about the equipment and events
- Use the risk factor names (e.g., "3 related events", "severity increasing")
- If SIF pathway is detected, emphasize urgency
- Keep it under 60 words
- Do NOT use markdown formatting
"""

    # Try new SDK first
    try:
        client = google_genai.Client(api_key=api_key)
        response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
        return response.text.strip()
    except NameError:
        # Fall back to deprecated SDK
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=api_key)
        model = legacy_genai.GenerativeModel("gemini-3.6-flash")
        response = model.generate_content(prompt)
        return response.text.strip()


def _generate_template(score, evidence_logs, equipment_list, related_reports, deltas, trajectory, sif_category):
    eq_name = equipment_list[0].upper() if equipment_list else "the area"

    if score >= 70:
        reasoning = f"Why is {eq_name} high risk?\n\n"
        reasoning += f"{len(related_reports)} related safety events have been recorded. "

        if any("Same equipment" in e for e in evidence_logs):
            reasoning += "Multiple reports involve the exact same equipment. "

        if any("Severity" in e and "increas" in e for e in evidence_logs):
            reasoning += "Reported severity has escalated significantly. "

        if sif_category and sif_category != "None":
            reasoning += f"SIF Pathway detected ({sif_category}) — this indicates conditions that could lead to serious injury or fatality. "

        if trajectory == "ESCALATING":
            reasoning += "The trajectory is ESCALATING — the pattern is worsening over time. "

        reasoning += f"These combined signals caused the precursor score to rise to {score}. Immediate intervention required."
        return reasoning

    elif score >= 40:
        parts = [f"Risk is elevating for {eq_name}."]
        parts.append(f"We detected {len(related_reports)} related events recently.")
        if deltas:
            top_factors = sorted(deltas.items(), key=lambda x: x[1], reverse=True)[:2]
            factor_text = ", ".join([f"{k} (+{v})" for k, v in top_factors])
            parts.append(f"Top contributors: {factor_text}.")
        parts.append(f"The precursor score is {score}. Monitor closely and consider preventive action.")
        return " ".join(parts)

    else:
        return f"Risk is low.\n\nThis appears to be an isolated incident with a precursor score of {score}. Routine logging is sufficient."
