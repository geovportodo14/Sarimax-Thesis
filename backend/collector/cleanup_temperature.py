import os
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "sarimax_thesis")
WEATHER_RAW_PATH = "data/raw/weather_raw.csv"
MANILA_TZ = pytz.timezone("Asia/Manila")

def cleanup_temperature():
    if not MONGODB_URI:
        logger.error("MONGODB_URI not found.")
        return

    if not os.path.exists(WEATHER_RAW_PATH):
        logger.error(f"{WEATHER_RAW_PATH} not found.")
        return

    # Load weather data
    logger.info("Loading weather data from CSV...")
    df_wx = pd.read_csv(WEATHER_RAW_PATH)
    df_wx["timestamp"] = pd.to_datetime(df_wx["timestamp"]).dt.tz_localize("Asia/Manila")
    df_wx.set_index("timestamp", inplace=True)

    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    collection = db["energybuckets"]

    logger.info("Searching for documents with null weather data...")
    cursor = collection.find({"readings.weather.temp": None})
    
    doc_count = 0
    update_count = 0
    
    for doc in cursor:
        doc_updated = False
        updated_readings = []
        
        for r in doc.get("readings", []):
            # Check if temp is null
            if "weather" in r and (r["weather"].get("temp") is None or r["weather"].get("temp") == ""):
                ts = r["timestamp"]
                if ts.tzinfo is None:
                    ts = pytz.utc.localize(ts).astimezone(MANILA_TZ)
                else:
                    ts = ts.astimezone(MANILA_TZ)
                
                # Round to nearest hour for backfill
                target_ts = ts.replace(minute=0, second=0, microsecond=0)
                
                if target_ts in df_wx.index:
                    row = df_wx.loc[target_ts]
                    r["weather"]["temp"] = float(row["temperature"])
                    r["weather"]["humidity"] = float(row["humidity"])
                    # Ensure rainfall is also present
                    if "rainfall" not in r["weather"] or r["weather"]["rainfall"] is None:
                        r["weather"]["rainfall"] = float(row.get("rainfall", 0.0))
                    
                    doc_updated = True
                    update_count += 1
            
            updated_readings.append(r)
        
        if doc_updated:
            collection.update_one({"_id": doc["_id"]}, {"$set": {"readings": updated_readings, "last_updated": datetime.now()}})
            doc_count += 1

    logger.info(f"Updated {update_count} individual readings across {doc_count} documents.")
    client.close()

if __name__ == "__main__":
    logger.info("--- Starting Temperature Cleanup ---")
    cleanup_temperature()
    logger.info("--- Cleanup Completed ---")
