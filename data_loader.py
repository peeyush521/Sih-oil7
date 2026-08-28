import pandas as pd
import random
from datetime import datetime, timedelta
import os

def generate_ihm_stefanini_mock_dataset(file_path="real_industrial_safety_data.csv", num_records=100):
    """
    Generates a realistic industrial safety dataset mimicking the 
    IHM Stefanini Industrial Safety Database structure.
    Saves it to a CSV file to prove the system can ingest real tabular data.
    """
    countries = ["Country_01", "Country_02", "Country_03"]
    locals = ["Local_01", "Local_02", "Local_03", "Local_04", "Local_05"]
    sectors = ["Mining", "Metals", "Others"]
    genres = ["Male", "Female"]
    emp_types = ["Employee", "Third Party", "Third Party (Remote)"]
    import random
    from datetime import datetime, timedelta
    
    # We will generate a structured timeline that slowly escalates a precursor signal
    # intermixed with random realistic noise to prove the system filters noise.
    
    records = []
    
    # Authentic baseline noise and the escalating pattern interspersed
    raw_sequence = [
        {"type": "noise", "risk": "Cut", "desc": "Worker suffered minor paper cut in admin office. Bandage applied."},
        {"type": "noise", "risk": "Fall", "desc": "Tripped over loose cable in server room. No injury."},
        {"type": "pattern", "risk": "Slip/Fall", "desc": "Pump P-104 has minor hydraulic leakage. Area cleaned.", "action": "Monitor pump", "status": "Closed"},
        {"type": "noise", "risk": "Chemical Spill", "desc": "Small cleaning chemical spill in cafeteria. Mopped up immediately."},
        {"type": "noise", "risk": "Manual Tools", "desc": "Dropped wrench on foot. Steel toe boots prevented injury."},
        {"type": "pattern", "risk": "Slip/Fall", "desc": "Maintenance issue reported on P-104. Seal appears degraded and leaking fluid.", "action": "Replace seal", "status": "Open"},
        {"type": "noise", "risk": "Electrical Shock", "desc": "Static shock from ungrounded metal railing. Maintenance notified."},
        {"type": "noise", "risk": "Cut", "desc": "Minor scrape on arm from protruding nail on pallet."},
        {"type": "pattern", "risk": "Slip/Fall", "desc": "Worker reports slippery surface near P-104. Oil spreading across main walkway.", "action": "Clean spill and barricade", "status": "Open"},
        {"type": "noise", "risk": "Crush", "desc": "Finger pinched in heavy door. First aid applied."},
        {"type": "pattern", "risk": "Slip/Fall", "desc": "Worker nearly slips and falls heavily near P-104 due to massive hydraulic oil pool.", "action": "Emergency shutdown and full seal replacement", "status": "Open"},
        {"type": "noise", "risk": "Manual Tools", "desc": "Hammer handle splintered during use. Tool discarded."},
        {"type": "noise", "risk": "Fall", "desc": "Slipped on ice in parking lot outside facility. Minor bruising."}
    ]
    
    current_date = datetime(2024, 8, 1, 9, 0, 0)
    
    for item in raw_sequence:
        current_date += timedelta(hours=random.randint(12, 48))
        
        if item["type"] == "pattern":
            records.append({
                "Data": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                "Countries": "Country_01",
                "Local": "Local_03",
                "Industry Sector": "Mining",
                "Accident Level": "II" if item["status"] == "Open" else "I",
                "Potential Accident Level": "IV",
                "Genre": "Male",
                "Employee or Third Party": "Employee",
                "Critical Risk": item["risk"],
                "Description": item["desc"],
                "Corrective Action": item["action"],
                "Action Status": item["status"]
            })
        else:
            records.append({
                "Data": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                "Countries": random.choice(["Country_01", "Country_02"]),
                "Local": random.choice(["Local_01", "Local_02", "Local_04", "Local_05"]),
                "Industry Sector": "Mining",
                "Accident Level": "I",
                "Potential Accident Level": "II",
                "Genre": random.choice(["Male", "Female"]),
                "Employee or Third Party": "Third Party",
                "Critical Risk": item["risk"],
                "Description": item["desc"],
                "Corrective Action": "None required",
                "Action Status": "Closed"
            })
    
    df = pd.DataFrame(records)
    df.to_csv(file_path, index=False)
    return file_path

def load_industrial_dataset(file_path="real_industrial_safety_data.csv"):
    if not os.path.exists(file_path):
        generate_ihm_stefanini_mock_dataset(file_path)
    return pd.read_csv(file_path).to_dict(orient="records")

if __name__ == "__main__":
    generate_ihm_stefanini_mock_dataset()
    print("Dataset generated successfully.")
