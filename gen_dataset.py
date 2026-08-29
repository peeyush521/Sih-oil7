import random, datetime, pandas as pd
random.seed(42)
reports=[]
def add(risk,desc,loc,status):
    reports.append((risk,desc,loc,status))
add("Chemical Spill","Pump P-104 seal failure observed during morning shift. Hydraulic fluid leaking at approximately 2 litres per minute. Area cordoned and spill containment deployed. Seal replacement scheduled for tomorrow.","Unit_A_Processing","Open")
add("Chemical Spill","Minor crude oil seepage from wellhead WH-12 flange gasket during routine well testing operations. Leak clamped temporarily. Gasket replacement ordered from stores.","Well_Pad_WP01","Closed")
add("Electrical Shock","Thermal imaging scan of electrical panel WB-07 revealed hotspot at main busbar connection. Temperature reading 87 degrees Celsius. Panel de-energized.","Warehouse_WH01","Open")
print("Script stub created")
