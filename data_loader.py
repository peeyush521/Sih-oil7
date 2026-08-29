import pandas as pd
import random
from datetime import datetime, timedelta
import os


def generate_ihm_stefanini_mock_dataset(file_path="real_industrial_safety_data.csv", num_records=100):
    """
    Generates a realistic industrial safety dataset mimicking Oil India's
    Duliajan facility operations. Includes diverse incident types:
    - Hydraulic equipment failures
    - Chemical exposure events
    - Electrical hazards
    - Working at height incidents
    - Confined space events
    - Environmental spills
    - Manual handling injuries
    """

    # ── Precursor Chain: P-104 Hydraulic Leak Escalation ──
    precursor_chain = [
        {"type": "noise", "risk": "Cut", "desc": "Worker suffered minor paper cut in admin office. Bandage applied.", "location": "Local_01", "action": "First aid", "status": "Closed"},
        {"type": "noise", "risk": "Fall", "desc": "Tripped over loose cable in server room. No injury.", "location": "Local_02", "action": "Cable tidied", "status": "Closed"},

        # Pattern: P-104 escalation begins
        {"type": "pattern", "risk": "Slip/Fall", "desc": "Pump P-104 has minor hydraulic leakage. Area cleaned and inspected.", "location": "Local_03", "action": "Monitor pump", "status": "Closed"},
        {"type": "noise", "risk": "Chemical Spill", "desc": "Small cleaning chemical spill in cafeteria. Mopped up immediately.", "location": "Local_01", "action": "Cleaned", "status": "Closed"},
        {"type": "noise", "risk": "Manual Tools", "desc": "Dropped wrench on foot. Steel toe boots prevented injury.", "location": "Local_04", "action": "Tool inspection", "status": "Closed"},

        {"type": "pattern", "risk": "Slip/Fall", "desc": "Maintenance issue reported on P-104. Seal appears degraded and leaking fluid.", "location": "Local_03", "action": "Replace seal", "status": "Open"},
        {"type": "noise", "risk": "Electrical Shock", "desc": "Static shock from ungrounded metal railing. Maintenance notified.", "location": "Local_02", "action": "Grounding check", "status": "Closed"},

        {"type": "pattern", "risk": "Slip/Fall", "desc": "Worker reports slippery surface near P-104. Oil spreading across main walkway.", "location": "Local_03", "action": "Clean spill and barricade", "status": "Open"},
        {"type": "noise", "risk": "Crush", "desc": "Finger pinched in heavy door. First aid applied.", "location": "Local_05", "action": "Door maintenance", "status": "Closed"},

        {"type": "pattern", "risk": "Slip/Fall", "desc": "Worker nearly slips and falls heavily near P-104 due to massive hydraulic oil pool.", "location": "Local_03", "action": "Emergency shutdown and full seal replacement", "status": "Open"},
        {"type": "noise", "risk": "Manual Tools", "desc": "Hammer handle splintered during use. Tool discarded.", "location": "Local_04", "action": "Tool replaced", "status": "Closed"},

        # Noise buffer
        {"type": "noise", "risk": "Fall", "desc": "Slipped on ice in parking lot outside facility. Minor bruising.", "location": "Local_05", "action": "De-icing applied", "status": "Closed"},
        {"type": "noise", "risk": "Cut", "desc": "Minor paper cut processing safety forms in control room.", "location": "Local_01", "action": "First aid", "status": "Closed"},

        # Pattern escalation: P-104 reaching critical
        {"type": "pattern", "risk": "Chemical Spill", "desc": "Major hydraulic fluid release from P-104. Entire Unit A floor covered in oil. Evacuation initiated.", "location": "Local_03", "action": "EMERGENCY: Full unit shutdown, environmental containment deployed", "status": "Open"},
    ]

    # ── Scenario B: Electrical Panel Overheating at Warehouse C ──
    electrical_chain = [
        {"type": "noise", "risk": "Fall", "desc": "Worker tripped on uneven flooring in warehouse B. No injury.", "location": "Local_02", "action": "Floor repair scheduled", "status": "Closed"},
        {"type": "pattern", "risk": "Electrical Shock", "desc": "Warm smell detected near electrical panel WB-07 in Warehouse C during night shift.", "location": "Local_04", "action": "Electrician dispatched", "status": "Closed"},
        {"type": "noise", "risk": "Manual Tools", "desc": "Socket wrench dropped from height during scaffold work. Below area clear.", "location": "Local_03", "action": "Tool tethering reminder", "status": "Closed"},
        {"type": "pattern", "risk": "Electrical Shock", "desc": "Electrical panel WB-07 showing discoloration and heat marks. Thermographic scan requested.", "location": "Local_04", "action": "Thermal scan ordered", "status": "Open"},
        {"type": "noise", "risk": "Cut", "desc": "Minor laceration from sharp pipe edge in maintenance shop. Steri-strips applied.", "location": "Local_05", "action": "Edge deburring", "status": "Closed"},
        {"type": "pattern", "risk": "Electrical Shock", "desc": "Spark observed from WB-07 panel. Two workers in vicinity reported mild shock sensation.", "location": "Local_04", "action": "Immediate isolation, lockout/tagout", "status": "Open"},
    ]

    # ── Scenario C: Working at Height — Scaffolding Issues ──
    height_chain = [
        {"type": "noise", "risk": "Fall", "desc": "Routine housekeeping inspection completed. Minor debris cleared from walkway.", "location": "Local_01", "action": "Housekeeping", "status": "Closed"},
        {"type": "pattern", "risk": "Fall", "desc": "Scaffold guardrail found loose on Tower Unit 3 platform during pre-use inspection.", "location": "Local_03", "action": "Guardrail repaired", "status": "Closed"},
        {"type": "noise", "risk": "Manual Tools", "desc": "Drill bit broken during concrete anchor installation. Replacement used.", "location": "Local_04", "action": "Tool replaced", "status": "Closed"},
        {"type": "pattern", "risk": "Fall", "desc": "Worker reported wobbly scaffold plank at 8m height on Tower Unit 3. Plank replaced.", "location": "Local_03", "action": "Plank replaced, full scaffold re-inspection", "status": "Open"},
        {"type": "pattern", "risk": "Fall", "desc": "Harness lanyard found with worn stitching during high-angle rescue drill at Tower Unit 3.", "location": "Local_03", "action": "ALL harnesses pulled from service for inspection", "status": "Open"},
        {"type": "noise", "risk": "Burn", "desc": "Minor hot surface contact during valve maintenance. Cool water applied.", "location": "Local_05", "action": "First aid", "status": "Closed"},
    ]

    # ── Isolated incidents (noise for other locations) ──
    isolated_incidents = [
        {"type": "noise", "risk": "Chemical Spill", "desc": "Small methanol spill during well testing. Contained within bund.", "location": "Local_02", "action": "Cleanup and bund inspection", "status": "Closed"},
        {"type": "noise", "risk": "Burn", "desc": "Steam leak from valve V-203 during pigging operation. Minor steam burn to hand.", "location": "Local_05", "action": "Valve replaced, PPE review", "status": "Closed"},
        {"type": "noise", "risk": "Crush", "desc": "Forklift proximity incident at loading bay. No contact made.", "location": "Local_01", "action": "Traffic management review", "status": "Closed"},
        {"type": "noise", "risk": "Cut", "desc": "Abrasion from handling rusty pipe section in laydown area. Tetanus booster given.", "location": "Local_04", "action": "Laydown area cleanup", "status": "Closed"},
        {"type": "noise", "risk": "Fall", "desc": "Worker slipped on wet surface in shower area. Handrail prevented fall.", "location": "Local_02", "action": "Anti-slip mat installed", "status": "Closed"},
        {"type": "noise", "risk": "Electrical Shock", "desc": "Portable RCD tripped during equipment test. No personnel contact.", "location": "Local_05", "action": "RCD replaced", "status": "Closed"},
        {"type": "noise", "risk": "Manual Tools", "desc": "Grease gun under pressure released unexpectedly. Minor contamination.", "location": "Local_03", "action": "Tool inspection", "status": "Closed"},
        {"type": "noise", "risk": "Chemical Spill", "desc": "Drum of cooling agent tipped during storage rotation. Bund contained spill.", "location": "Local_01", "action": "Drum repositioned", "status": "Closed"},
    ]

    # Build the full dataset by interleaving chains with noise
    raw_sequence = []

    # P-104 chain (primary demo)
    raw_sequence.extend(precursor_chain[:3])
    raw_sequence.extend(isolated_incidents[:2])
    raw_sequence.extend(precursor_chain[3:5])
    raw_sequence.extend(isolated_incidents[2:4])
    raw_sequence.extend(precursor_chain[5:8])
    raw_sequence.extend(isolated_incidents[4:6])
    raw_sequence.extend(precursor_chain[8:10])
    raw_sequence.extend(isolated_incidents[6:8])
    raw_sequence.extend(precursor_chain[10:])

    # Electrical chain (shorter, for variety)
    raw_sequence.extend(electrical_chain[:2])
    raw_sequence.extend(isolated_incidents[0:1])
    raw_sequence.extend(electrical_chain[2:4])
    raw_sequence.extend(electrical_chain[4:])

    # Height chain
    raw_sequence.extend(height_chain[:2])
    raw_sequence.extend(height_chain[2:4])
    raw_sequence.extend(height_chain[4:])

    # Generate timestamps
    current_date = datetime(2024, 8, 1, 9, 0, 0)
    records = []

    for item in raw_sequence:
        current_date += timedelta(hours=random.randint(12, 48))

        if item["type"] == "pattern":
            records.append({
                "Data": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                "Countries": "Country_01",
                "Local": item["location"],
                "Industry Sector": "Oil & Gas",
                "Accident Level": "II" if item["status"] == "Open" else "I",
                "Potential Accident Level": "IV",
                "Genre": random.choice(["Male", "Female"]),
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
                "Local": item.get("location", random.choice(["Local_01", "Local_02", "Local_04", "Local_05"])),
                "Industry Sector": "Oil & Gas",
                "Accident Level": "I",
                "Potential Accident Level": "II",
                "Genre": random.choice(["Male", "Female"]),
                "Employee or Third Party": random.choice(["Employee", "Third Party"]),
                "Critical Risk": item["risk"],
                "Description": item["desc"],
                "Corrective Action": item.get("action", "None required"),
                "Action Status": item.get("status", "Closed")
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
