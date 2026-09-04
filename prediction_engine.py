"""Time-Series Prediction Engine"""
import math
from datetime import datetime, timedelta
from collections import defaultdict

def predict_next_incidents(all_processed_reports, equipment_list=None):
    if not all_processed_reports or len(all_processed_reports) < 3:
        return {"predictions": [], "message": "Need at least 3 reports"}
    equipment_ts = defaultdict(list)
    location_ts = defaultdict(list)
    for r in all_processed_reports:
        report = r.get("report", {})
        entities = r.get("extracted_entities", {})
        risk = r.get("risk_data", {})
        date_str = report.get("date", "")
        try:
            if " " in date_str: dt = datetime.strptime(date_str[:19], "%Y-%m-%d %H:%M:%S")
            else: dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        except: continue
        score = risk.get("score", 0)
        sev = entities.get("severity", 1)
        entry = {"date": dt, "score": score, "severity": sev}
        for eq in entities.get("equipment", []): equipment_ts[eq].append(entry)
        for loc in entities.get("locations", []): location_ts[loc].append(entry)
    predictions = []
    for name, entries in {**equipment_ts, **location_ts}.items():
        if len(entries) < 2: continue
        entries.sort(key=lambda x: x["date"])
        pred = _analyze_series(name, entries)
        if pred: predictions.append(pred)
    predictions.sort(key=lambda x: x["risk_probability"], reverse=True)
    return {"predictions": predictions[:10], "total_analyzed": len(all_processed_reports), "forecast_horizon_days": 7}

def _analyze_series(name, entries):
    scores = [e["score"] for e in entries]
    sevs = [e["severity"] for e in entries]
    dates = [e["date"] for e in entries]
    avg = sum(scores)/len(scores)
    latest = scores[-1]
    trend = scores[-1] - scores[0]
    now = datetime.now()
    days_since = (now - dates[-1]).days if dates else 999
    freq = len(entries) / max((dates[-1]-dates[0]).days/30, 0.5) if len(dates)>=2 else 0
    rp = min(latest*0.3, 30)
    rp += 25 if trend>20 else 15 if trend>10 else 8 if trend>0 else 0
    rp += min(freq*5, 20)
    rp += 15 if days_since<=3 else 10 if days_since<=7 else 5 if days_since<=14 else 0
    rp += min(sum(sevs)/len(sevs)*2, 10)
    rp = min(round(rp), 95)
    avg_int = sum((dates[i+1]-dates[i]).days for i in range(len(dates)-1))/(len(dates)-1) if len(dates)>=2 else 7
    pred_date = dates[-1] + timedelta(days=max(avg_int, 1))
    rl = "CRITICAL" if rp>=70 else "WARNING" if rp>=40 else "LOW"
    conf = "High" if len(entries)>=5 else "Medium" if len(entries)>=3 else "Low"
    factors = []
    if latest>=70: factors.append("High current risk")
    if trend>15: factors.append("Rapidly escalating")
    elif trend>5: factors.append("Increasing trend")
    if freq>2: factors.append(f"Frequent ({freq:.1f}/mo)")
    if days_since<=3: factors.append("Very recent")
    if not factors: factors.append("Baseline monitoring")
    return {"entity_name": name, "risk_probability": rp, "risk_level": rl, "confidence": conf, "predicted_next_date": pred_date.strftime("%Y-%m-%d"), "days_until_predicted": max((pred_date-now).days, 0), "historical_incidents": len(entries), "avg_risk_score": round(avg,1), "latest_risk_score": latest, "trend": "ESCALATING" if trend>10 else "STABLE" if abs(trend)<=10 else "DECREASING", "key_factors": factors}

def get_prediction_summary(predictions):
    crit = [p for p in predictions if p["risk_level"]=="CRITICAL"]
    warn = [p for p in predictions if p["risk_level"]=="WARNING"]
    msg = ""
    if crit: msg = f"HIGHEST RISK: {crit[0]['entity_name']} ({crit[0]['risk_probability']}%)"
    elif warn: msg = f"ELEVATED: {warn[0]['entity_name']} ({warn[0]['risk_probability']}%)"
    else: msg = "All within normal parameters"
    return {"total": len(predictions), "critical": len(crit), "warning": len(warn), "message": msg}
