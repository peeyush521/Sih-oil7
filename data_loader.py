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
    # For the SIH 1-minute demo, we want EXACTLY the 4 reports that show the perfect escalation
    # without making the presenter click through 90 random noise reports first.
    
    records = [
        {
            "Data": "2024-08-01 09:00:00",
            "Countries": "Country_01",
            "Local": "Local_03",
            "Industry Sector": "Mining",
            "Accident Level": "I",
            "Potential Accident Level": "II",
            "Genre": "Male",
            "Employee or Third Party": "Employee",
            "Critical Risk": "Slip/Fall",
            "Description": "Pump P-104 has minor hydraulic leakage. Area cleaned.",
            "Corrective Action": "Monitor pump",
            "Action Status": "Closed"
        },
        {
            "Data": "2024-08-04 14:30:00",
            "Countries": "Country_01",
            "Local": "Local_03",
            "Industry Sector": "Mining",
            "Accident Level": "II",
            "Potential Accident Level": "III",
            "Genre": "Male",
            "Employee or Third Party": "Third Party",
            "Critical Risk": "Slip/Fall",
            "Description": "Maintenance issue reported on P-104. Seal appears degraded and leaking fluid.",
            "Corrective Action": "Replace seal",
            "Action Status": "Open"
        },
        {
            "Data": "2024-08-07 11:15:00",
            "Countries": "Country_01",
            "Local": "Local_03",
            "Industry Sector": "Mining",
            "Accident Level": "II",
            "Potential Accident Level": "IV",
            "Genre": "Female",
            "Employee or Third Party": "Employee",
            "Critical Risk": "Slip/Fall",
            "Description": "Worker reports slippery surface near P-104. Oil spreading across main walkway.",
            "Corrective Action": "Clean spill and barricade",
            "Action Status": "Open"
        },
        {
            "Data": "2024-08-10 16:45:00",
            "Countries": "Country_01",
            "Local": "Local_03",
            "Industry Sector": "Mining",
            "Accident Level": "III",
            "Potential Accident Level": "V",
            "Genre": "Male",
            "Employee or Third Party": "Employee",
            "Critical Risk": "Slip/Fall",
            "Description": "Worker nearly slips and falls heavily near P-104 due to massive hydraulic oil pool.",
            "Corrective Action": "Emergency shutdown and full seal replacement",
            "Action Status": "Open"
        }
    ]
    
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
