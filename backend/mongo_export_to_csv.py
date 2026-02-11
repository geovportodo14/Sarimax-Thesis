import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

def export_mongodb_to_csv():
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DATABASE_NAME", "sarimax_thesis")
    
    if not uri:
        print("Error: MONGODB_URI not found in .env")
        return

    client = MongoClient(uri)
    db = client[db_name]
    
    # Create export directory
    export_dir = "data/exports"
    os.makedirs(export_dir, exist_ok=True)
    
    appliance_collections = ["aircon", "refrigerator", "electric_fan"]
    
    for coll_name in appliance_collections:
        print(f"Exporting collection: {coll_name}...")
        collection = db[coll_name]
        cursor = collection.find().sort("date", 1)
        
        reading_rows = []
        summary_rows = []
        
        for doc in cursor:
            date_str = doc.get("date")
            device_id = doc.get("device_id")
            
            # 1. Export Readings
            readings = doc.get("readings", [])
            for r in readings:
                row = {
                    "date": date_str,
                    "device_id": device_id,
                    "timestamp": r.get("timestamp"),
                    "interval_index": r.get("interval_index"),
                }
                
                # Flatten raw_data
                raw = r.get("raw_data", {})
                for k, v in raw.items():
                    row[f"raw_{k}"] = v
                
                # Flatten processed_data
                proc = r.get("processed_data", {})
                for k, v in proc.items():
                    row[f"proc_{k}"] = v
                
                # Flatten weather
                wx = r.get("weather", {})
                for k, v in wx.items():
                    row[f"weather_{k}"] = v
                
                reading_rows.append(row)
            
            # 2. Export Daily Summary
            summary = doc.get("daily_summary")
            if summary:
                s_row = {
                    "date": date_str,
                    "device_id": device_id,
                }
                s_row.update(summary)
                summary_rows.append(s_row)
        
        # Save Readings CSV
        if reading_rows:
            df_readings = pd.DataFrame(reading_rows)
            readings_path = os.path.join(export_dir, f"{coll_name}_full_readings.csv")
            df_readings.to_csv(readings_path, index=False)
            print(f"  - Saved {len(reading_rows)} readings to {readings_path}")
        
        # Save Summary CSV
        if summary_rows:
            df_summary = pd.DataFrame(summary_rows)
            summary_path = os.path.join(export_dir, f"{coll_name}_daily_summaries.csv")
            df_summary.to_csv(summary_path, index=False)
            print(f"  - Saved {len(summary_rows)} summaries to {summary_path}")

    client.close()
    print(f"\n✅ All exports completed. Files are located in: {os.path.abspath(export_dir)}")

if __name__ == "__main__":
    export_mongodb_to_csv()
