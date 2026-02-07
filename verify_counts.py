from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "sarimax_thesis")

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

def check_counts():
    appliances = ["aircon", "refrigerator", "electric_fan"]
    dates = ["2026-02-04", "2026-02-05", "2026-02-06"]
    
    for app in appliances:
        print(f"--- {app.upper()} ---")
        for date in dates:
            doc = db[app].find_one({"date": date})
            if doc:
                count = len(doc.get("readings", []))
                stored_count = doc.get("reading_count", 0)
                print(f"Date: {date} | Readings in array: {count} | stored_count field: {stored_count}")
            else:
                print(f"Date: {date} | No document found")

if __name__ == "__main__":
    check_counts()
