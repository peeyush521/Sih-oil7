import datetime

def generate_synthetic_incident_chain():
    base_date = datetime.date.today() - datetime.timedelta(days=15)
    
    return [
        {
            "id": "RPT-001",
            "date": (base_date + datetime.timedelta(days=1)).isoformat(),
            "text": "Operator slipped near Pump P-104 due to small oil spill. Area cleaned.",
        },
        {
            "id": "RPT-002",
            "date": (base_date + datetime.timedelta(days=5)).isoformat(),
            "text": "Minor oil leakage observed around Pump P-104 during routine inspection.",
        },
        {
            "id": "RPT-003",
            "date": (base_date + datetime.timedelta(days=9)).isoformat(),
            "text": "Worker almost fell while inspecting Pump P-104. Floor is slippery.",
        },
        {
            "id": "RPT-004",
            "date": (base_date + datetime.timedelta(days=12)).isoformat(),
            "text": "Maintenance team reported repeated oil leakage in the same area around Pump P-104. Hazard.",
        }
    ]
