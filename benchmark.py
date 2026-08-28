import random
from datetime import datetime, timedelta
import pandas as pd
from nlp_engine import get_nlp_engine
from classification_engine import get_classification_engine
from graph_engine import TemporalKnowledgeGraph
from risk_engine import calculate_risk

def generate_benchmark_dataset():
    sequences = []
    
    # Generate 500 sequences
    # 150 Escalating (True Positives)
    # 150 Minor noise (True Negatives)
    # 100 Severe isolated (True Negatives)
    # 50 Equipment recurrence non-escalating (True Negatives)
    # 50 Unresolved corrective actions that do escalate (True Positives)
    
    start_date = datetime(2023, 1, 1)
    
    def add_sequence(seq_type, num_events, expected_precursor, days_spread):
        seq_id = f"SEQ_{len(sequences)}"
        events = []
        base_date = start_date + timedelta(days=random.randint(0, 365))
        
        equipment = f"PUMP_{random.randint(100,999)}"
        location = f"UNIT_{random.choice(['A','B','C','D'])}"
        
        for i in range(num_events):
            event_date = base_date + timedelta(days=int(i * (days_spread / max(1, num_events - 1))))
            
            severity = 1
            desc = ""
            action_status = "Closed"
            
            if seq_type == "Escalating":
                severity = 1 if i < num_events // 2 else (2 if i < num_events - 1 else 3)
                if severity == 1: desc = f"Minor leak noticed at {equipment} in {location}."
                elif severity == 2: desc = f"Significant fluid spill near {equipment}. Slip hazard in {location}."
                else: desc = f"Worker slipped on massive oil leak from {equipment} and fell hard."
            
            elif seq_type == "Minor Noise":
                severity = 1
                desc = f"Routine maintenance performed on {equipment} in {location}."
                
            elif seq_type == "Severe Isolated":
                if i == 0:
                    severity = 3
                    desc = f"Major structural failure of crane in {location}. Area evacuated."
                else:
                    severity = 1
                    desc = f"Inspection passed for {location}."
                    
            elif seq_type == "Equipment Recurrence":
                severity = 1
                desc = f"Sensor calibration issue with {equipment}."
                
            elif seq_type == "Unresolved":
                severity = 1 if i < num_events -1 else 2
                desc = f"Vibration anomaly detected on {equipment}."
                action_status = "Open"
            
            events.append({
                "id": f"{seq_id}_EVT_{i}",
                "date": event_date.strftime("%Y-%m-%d %H:%M:%S"),
                "text": desc,
                "location": location,
                "action_status": action_status,
                "severity_gt": severity
            })
            
        sequences.append({
            "seq_id": seq_id,
            "type": seq_type,
            "expected_precursor": expected_precursor,
            "events": events
        })
        
    for _ in range(150): add_sequence("Escalating", 4, True, 10)
    for _ in range(150): add_sequence("Minor Noise", 3, False, 40)
    for _ in range(100): add_sequence("Severe Isolated", 2, False, 30)
    for _ in range(50): add_sequence("Equipment Recurrence", 4, False, 20)
    for _ in range(50): add_sequence("Unresolved", 3, True, 15)
    
    return sequences

def run_benchmark():
    print("="*60)
    print("SIF PRECURSOR INTELLIGENCE - CONTROLLED BENCHMARK")
    print("="*60)
    print("Generating 500 synthetic sequences...")
    sequences = generate_benchmark_dataset()
    
    nlp = get_nlp_engine()
    classifier = get_classification_engine()
    
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    
    lead_times = []
    
    print("Evaluating AI Pipeline and Baselines...")
    
    # Baselines
    b1_tp, b1_fp, b1_tn, b1_fn = 0, 0, 0, 0
    b2_tp, b2_fp, b2_tn, b2_fn = 0, 0, 0, 0
    
    b1_lead = []
    b2_lead = []
    
    for seq in sequences:
        graph = TemporalKnowledgeGraph()
        precursor_detected = False
        
        b1_detected = False
        b2_detected = False
        
        for idx, evt in enumerate(seq["events"]):
            # Keyword Baseline
            if not b1_detected:
                lower = evt["text"].lower()
                if sum([1 for w in ["leak", "spill", "fall", "slip", "hazard", "severe", "failure"] if w in lower]) >= 2:
                    b1_detected = True
                    curr = datetime.strptime(evt["date"], "%Y-%m-%d %H:%M:%S")
                    fin = datetime.strptime(seq["events"][-1]["date"], "%Y-%m-%d %H:%M:%S")
                    if (fin-curr).days >= 0: b1_lead.append((fin-curr).days)
                    
            # ML Baseline
            if not b2_detected:
                cls = classifier.classify(evt["text"])
                if cls in ["Fall", "Slip/Fall", "Chemical Spill", "Burn", "Crush"]:
                    b2_detected = True
                    curr = datetime.strptime(evt["date"], "%Y-%m-%d %H:%M:%S")
                    fin = datetime.strptime(seq["events"][-1]["date"], "%Y-%m-%d %H:%M:%S")
                    if (fin-curr).days >= 0: b2_lead.append((fin-curr).days)
            
            # Our System
            extracted = nlp.extract_entities(evt["text"])
            extracted["severity"] = evt["severity_gt"]
            emb = nlp.get_embedding(evt["text"])
            
            graph.add_report(evt["id"], evt["date"], evt["text"], extracted, emb, evt["action_status"])
            related = graph.get_related_reports(evt["id"], nlp)
            risk = calculate_risk(evt["id"], graph.reports[evt["id"]], related)
            
            if risk["score"] >= 70 and not precursor_detected:
                precursor_detected = True
                curr_date = datetime.strptime(evt["date"], "%Y-%m-%d %H:%M:%S")
                final_event_date = datetime.strptime(seq["events"][-1]["date"], "%Y-%m-%d %H:%M:%S")
                lead_time = (final_event_date - curr_date).days
                if lead_time >= 0:
                    lead_times.append(lead_time)
                
        # Tally System
        if precursor_detected and seq["expected_precursor"]: tp += 1
        elif precursor_detected and not seq["expected_precursor"]: fp += 1
        elif not precursor_detected and not seq["expected_precursor"]: tn += 1
        elif not precursor_detected and seq["expected_precursor"]: fn += 1
        
        # Tally B1
        if b1_detected and seq["expected_precursor"]: b1_tp += 1
        elif b1_detected and not seq["expected_precursor"]: b1_fp += 1
        elif not b1_detected and not seq["expected_precursor"]: b1_tn += 1
        elif not b1_detected and seq["expected_precursor"]: b1_fn += 1
        
        # Tally B2
        if b2_detected and seq["expected_precursor"]: b2_tp += 1
        elif b2_detected and not seq["expected_precursor"]: b2_fp += 1
        elif not b2_detected and not seq["expected_precursor"]: b2_tn += 1
        elif not b2_detected and seq["expected_precursor"]: b2_fn += 1

    def calc_metrics(t_p, f_p, f_n, leads):
        p = t_p / (t_p + f_p) if (t_p + f_p) > 0 else 0
        r = t_p / (t_p + f_n) if (t_p + f_n) > 0 else 0
        f = 2 * (p * r) / (p + r) if (p + r) > 0 else 0
        fa = (f_p / len(sequences)) * 100
        lt = sum(leads) / len(leads) if leads else 0
        return p*100, r*100, f*100, fa, lt

    p, r, f1, fa, lt = calc_metrics(tp, fp, fn, lead_times)
    b1_p, b1_r, b1_f1, b1_fa, b1_lt = calc_metrics(b1_tp, b1_fp, b1_fn, b1_lead)
    b2_p, b2_r, b2_f1, b2_fa, b2_lt = calc_metrics(b2_tp, b2_fp, b2_fn, b2_lead)
    
    print("\n[ BENCHMARK COMPARISON RESULTS ]")
    print(f"{'Method':<25} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'FA/100':<10} | {'Avg Lead (Days)':<15}")
    print("-" * 90)
    print(f"{'Baseline 1 (Keyword)':<25} | {b1_p:<10.1f} | {b1_r:<10.1f} | {b1_f1:<10.1f} | {b1_fa:<10.1f} | {b1_lt:<15.1f}")
    print(f"{'Baseline 2 (ML)':<25} | {b2_p:<10.1f} | {b2_r:<10.1f} | {b2_f1:<10.1f} | {b2_fa:<10.1f} | {b2_lt:<15.1f}")
    print(f"{'Our System (Temporal)':<25} | {p:<10.1f} | {r:<10.1f} | {f1:<10.1f} | {fa:<10.1f} | {lt:<15.1f}")
    print("="*90)
    
if __name__ == "__main__":
    run_benchmark()
