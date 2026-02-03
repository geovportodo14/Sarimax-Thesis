import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "sarimax_thesis")

def debug_day(date_str):
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    
    for app in ["aircon", "refrigerator", "electric_fan"]:
        doc = db[app].find_one({"date": date_str})
        if doc:
            print(f"--- {app} ({date_str}) ---")
            print(f"Reading count: {len(doc.get('readings', []))}")
            if doc['readings']:
                # Print first and last reading
                print(f"First reading: {doc['readings'][0]}")
                print(f"Last reading: {doc['readings'][-1]}")
            print(f"Daily Summary: {doc.get('daily_summary')}")
        else:
            print(f"--- {app} ({date_str}) NOT FOUND ---")
    client.close()

if __name__ == "__main__":
    debug_day("2026-01-26")
