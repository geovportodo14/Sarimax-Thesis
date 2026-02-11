import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "sarimax_thesis_db")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print("--- Verifying Reversion ---")
doc = db.aircon.find_one({"date": "2026-02-11"})
if doc:
    r = doc["readings"][-1]
    raw = r.get("raw_data", {})
    proc = r.get("processed_data", {})
    add_ele = raw.get("add_ele")
    total_kwh = proc.get("total_kwh")
    acc = proc.get("total_kwh_accumulated")
    
    print(f"Raw add_ele: {add_ele}")
    print(f"Processed total_kwh: {total_kwh}")
    print(f"Processed accumulated: {acc}")
    
    if add_ele is not None and acc is not None:
        expected = float(add_ele)/100.0
        if abs(acc - expected) < 1e-6:
             print("SUCCESS: total_kwh_accumulated matches raw/100")
        else:
             print(f"FAILURE: Expected {expected}, got {acc}")
else:
    print("No doc found for 2026-02-11")
