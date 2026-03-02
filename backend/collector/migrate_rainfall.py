import os
import csv
import logging
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "sarimax_thesis")
CSV_ARCHIVE_DIR = "data/archive/energy_data"

def migrate_mongodb():
    if not MONGODB_URI:
        logger.error("MONGODB_URI not found. Skipping MongoDB migration.")
        return

    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    collection = db["energybuckets"]

    logger.info("Migrating MongoDB collection: energybuckets")
    
    # Update documents to rename 'pressure' to 'rainfall' in the readings array
    # MongoDB doesn't easily allow renaming fields inside arrays in one go across all docs with $rename
    # We'll use a script to iterate or a complex update.
    
    cursor = collection.find({"readings.weather.pressure": {"$exists": True}})
    count = 0
    for doc in cursor:
        updated_readings = []
        for r in doc.get("readings", []):
            if "weather" in r and "pressure" in r["weather"]:
                r["weather"]["rainfall"] = r["weather"].pop("pressure")
            updated_readings.append(r)
        
        collection.update_one({"_id": doc["_id"]}, {"$set": {"readings": updated_readings}})
        count += 1
    
    logger.info(f"Updated {count} documents in MongoDB.")
    client.close()

def migrate_csv_files():
    if not os.path.exists(CSV_ARCHIVE_DIR):
        logger.warning(f"CSV archive directory {CSV_ARCHIVE_DIR} not found.")
        return

    logger.info(f"Relabeling 'pressure' column to 'rainfall' in {CSV_ARCHIVE_DIR}")
    for filename in os.listdir(CSV_ARCHIVE_DIR):
        if filename.endswith(".csv"):
            filepath = os.path.join(CSV_ARCHIVE_DIR, filename)
            try:
                df = pd.read_csv(filepath)
                if "pressure" in df.columns:
                    df.rename(columns={"pressure": "rainfall"}, inplace=True)
                    df.to_csv(filepath, index=False)
                    logger.info(f"Updated {filename}")
            except Exception as e:
                logger.error(f"Failed to update {filename}: {e}")

if __name__ == "__main__":
    logger.info("--- Starting Migration: Pressure -> Rainfall ---")
    migrate_mongodb()
    migrate_csv_files()
    logger.info("--- Migration Completed ---")
