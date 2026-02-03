import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient

# Load configuration
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "sarimax_thesis")

def verify_data():
    if not MONGODB_URI:
        print("Error: MONGODB_URI not found in .env")
        return

    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    appliances = ["aircon", "refrigerator", "electric_fan"]

    # Target Energy for verification (Jan 12 - Jan 25)
    TARGET_ENERGY = {
        "aircon": [3.88, 3.76, 3.75, 4.10, 3.33, 3.90, 3.79, 3.58, 3.73, 3.63, 2.99, 3.17, 3.44, 4.19],
        "refrigerator": [2.42, 2.34, 2.25, 2.25, 2.33, 2.21, 2.46, 2.25, 2.42, 2.21, 2.14, 2.00, 1.09, 2.24],
        "electric_fan": [0.29, 0.33, 0.30, 0.27, 0.27, 0.33, 0.46, 0.30, 0.32, 0.40, 0.33, 0.33, 0.39, 0.48]
    }

    print("\n--- MongoDB Data Verification (Jan 12 - Jan 25 Targets) ---\n")
    for app in appliances:
        print(f"Collection: {app}")
        collection = db[app]
        for i in range(14):
            date_str = f"2026-01-{12 + i:02d}"
            target = TARGET_ENERGY[app][i]
            doc = collection.find_one({"date": date_str})
            if doc:
                summary = doc.get("daily_summary", {})
                actual = summary.get("total_kwh", 0)
                reading_count = doc.get("reading_count", 0)
                status_icon = "✅" if abs(actual - target) < 0.05 else "❌"
                print(f"[{status_icon}] {date_str} | Target: {target:.2f} | Actual: {actual:.3f} | Count: {reading_count}/144")
            else:
                print(f"[MISSING] {date_str}")
        print("-" * 50)

    print("\n--- MongoDB Data Verification (Jan 26 - Feb 2 Investigation) ---\n")
    investigation_range = [
        "2026-01-26", "2026-01-27", "2026-01-28", "2026-01-29", "2026-01-30", "2026-01-31",
        "2026-02-01", "2026-02-02"
    ]

    for app in appliances:
        print(f"Collection: {app}")
        collection = db[app]
        for date_str in investigation_range:
            doc = collection.find_one({"date": date_str})
            if doc:
                summary = doc.get("daily_summary", {})
                actual = summary.get("total_kwh", 0)
                reading_count = doc.get("reading_count", 0)
                status = doc.get("status", "unknown")
                print(f"[{status}] {date_str} | Actual: {actual:.3f} kWh | Count: {reading_count}/144")
            else:
                print(f"[MISSING] {date_str}")
        print("-" * 50)

    client.close()

if __name__ == "__main__":
    verify_data()
