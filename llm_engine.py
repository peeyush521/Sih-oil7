def generate_llm_explanation(evidence: dict, equipment_list: list, related_reports: list):
    """
    Mock LLM Generator. 
    In production, you would call `google.generativeai.generate_content` here,
    passing the structured JSON evidence as the prompt.
    """
    score = evidence.get("score", 0)
    evidence_logs = evidence.get("evidence", [])
    
    eq_name = "the area"
    if equipment_list:
        eq_name = equipment_list[0].upper()
        
    if score >= 70:
        reasoning = f"**Why is {eq_name} high risk?**\n\n"
        reasoning += f"{len(related_reports)} related safety events have been recorded. "
        
        if any("Same equipment" in e for e in evidence_logs):
            reasoning += "Multiple reports involve the exact same equipment. "
            
        if any("Severity increased" in e for e in evidence_logs):
            reasoning += "Reported severity has escalated significantly. "
            
        reasoning += f"These combined signals caused the precursor score to rise to {score}. Immediate intervention required."
        return reasoning
        
    elif score >= 40:
        return f"**Risk is elevating for {eq_name}**.\n\nWe detected {len(related_reports)} related events recently. The precursor score is {score}. Monitor closely."
    else:
        return f"**Risk is low**.\n\nThis appears to be an isolated incident with a precursor score of {score}. Routine logging is sufficient."
