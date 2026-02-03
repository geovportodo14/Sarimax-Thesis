import csv
import os
import logging
from datetime import datetime
import pytz
from dotenv import load_dotenv

from collector.storage.db_client import MongoDBClient
from collector.utils.preprocessor import DataPreprocessor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "sarimax_thesis")
MANILA_TZ = pytz.timezone("Asia/Manila")

DEVICES = {
    "Aircon": "a3ed2fe218a724b4fepeni",
    "Refrigerator": "a3986d20c19f33c7c107fw",
    "Electric_Fan": "a3c772d3fde52dbae832bi"
}

def migrate_csv_folder(folder_path):
    if not MONGODB_URI:
        logger.error("MONGODB_URI not found in environment")
        return

    db = MongoDBClient(MONGODB_URI, DATABASE_NAME)
    preprocessor = DataPreprocessor()

    files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    files.sort()

    for filename in files:
        filepath = os.path.join(folder_path, filename)
        logger.info(f"Processing {filename}...")
        
        # Group by (timestamp, device) because CSV is flattened
        readings = {}

        try:
            with open(filepath, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ts_str = row['timestamp']
                    device_name = row['device']
                    prop = row['property']
                    value = row['value']
                    
                    if device_name not in DEVICES:
                        continue
                    
                    key = (ts_str, device_name)
                    if key not in readings:
                        readings[key] = {
                            "raw": {},
                            "weather": {
                                "temp": float(row['temp_C']) if row['temp_C'] else None,
                                "humidity": float(row['humidity']) if row['humidity'] else None,
                                "pressure": float(row['pressure']) if row['pressure'] else None
                            }
                        }
                    
                    readings[key]["raw"][prop] = value

            # Store grouped readings
            for (ts_str, device_name), data in readings.items():
                ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=MANILA_TZ)
                dev_id = DEVICES[device_name]
                
                # Normalize
                processed = preprocessor.normalize(device_name, data["raw"])
                
                # Store
                db.store_reading(device_name, dev_id, ts, data["raw"], data["weather"], processed_data=processed)
            
            # After importing the file, trigger a daily validation to create the summary
            date_from_file = filename.split('_')[-1].split('.')[0]
            formatted_date = f"{date_from_file[:4]}-{date_from_file[4:6]}-{date_from_file[6:8]}"
            
            for device_name in DEVICES:
                db.final_daily_validation(device_name, formatted_date)
                
            logger.info(f"Finished migrating {filename}")

        except Exception as e:
            logger.exception(f"Error processing {filename}")

if __name__ == "__main__":
    import sys
    folder = sys.argv[1] if len(sys.argv) > 1 else "data/energy_data"
    migrate_csv_folder(folder)
