"""Crew Fatigue & Scheduling Optimization Engine."""
import math
from collections import defaultdict

class FatigueEngine:
    def __init__(self):
        self.crew_schedules = {}

    def calculate_fatigue_risk(self, shift_hours, time_of_day, consecutive_days=1):
        if shift_hours <= 8: dur = 1.0
        elif shift_hours <= 10: dur = 1.0 + (shift_hours - 8) * 0.075
        elif shift_hours <= 12: dur = 1.15 + (shift_hours - 10) * 0.1
        elif shift_hours <= 14: dur = 1.35 + (shift_hours - 12) * 0.125
        else: dur = 1.60 + (shift_hours - 14) * 0.2
        h = time_of_day
        if 6 <= h < 14: circ = 1.0
        elif 14 <= h < 22: circ = 1.1
        elif h >= 22 or h < 2: circ = 1.35
        else: circ = 1.5
        cons = 1.0 + (consecutive_days - 1) * 0.05 if consecutive_days <= 5 else 1.25 + (consecutive_days - 5) * 0.1
        risk = dur * circ * cons
        level = "CRITICAL" if risk >= 1.8 else "HIGH" if risk >= 1.4 else "MODERATE" if risk >= 1.15 else "LOW"
        rec = "STOP WORK" if risk >= 1.8 else "HIGH RISK" if risk >= 1.4 else "Additional breaks" if risk >= 1.15 else "Acceptable"
        return {"fatigue_risk_multiplier": round(risk, 2), "level": level, "duration_risk": round(dur, 2), "circadian_risk": round(circ, 2), "recommendation": rec}

    def apply_fatigue_to_risk(self, base_score, entities):
        shift = entities.get("shift_info", {})
        hour = shift.get("hour") or (22 if shift.get("is_night_shift") else 10)
        hrs = 10 if shift.get("is_night_shift") else 8
        f = self.calculate_fatigue_risk(hrs, hour, 3)
        adj = min(round(base_score * f["fatigue_risk_multiplier"]), 100)
        return {"original_score": base_score, "fatigue_multiplier": f["fatigue_risk_multiplier"], "fatigue_adjusted_score": adj, "fatigue_level": f["level"], "fatigue_contribution": adj - base_score}

    def get_crew_fatigue_dashboard(self, reports):
        night = sum(1 for r in reports if r.get("extracted_entities", {}).get("shift_info", {}).get("is_night_shift"))
        total = len(reports)
        pct = round(night / max(total, 1) * 100, 1)
        demo = [{"name": "Rig Crew A", "recent_shifts": 5, "rest_hours": 8}, {"name": "Maintenance Team", "recent_shifts": 7, "rest_hours": 6}, {"name": "Night Watch", "recent_shifts": 4, "rest_hours": 9}]
        scheds = []
        for m in demo:
            f = self.calculate_fatigue_risk(10 if m["recent_shifts"] >= 5 else 8, 22 if m["recent_shifts"] % 2 == 0 else 6, m["recent_shifts"])
            scheds.append({"crew_member": m["name"], "fatigue_risk": f["fatigue_risk_multiplier"], "level": f["level"], "suggestion": f["recommendation"], "rest_hours": m["rest_hours"]})
        scheds.sort(key=lambda x: x["fatigue_risk"], reverse=True)
        return {"night_incident_pct": pct, "total_reports": total, "crew_schedule": {"schedules": scheds}, "insights": [str(pct) + "% night shift incidents"]}

fatigue_engine = None
def get_fatigue_engine():
    global fatigue_engine
    if fatigue_engine is None: fatigue_engine = FatigueEngine()
    return fatigue_engine