import os
import argparse
import logging
import csv
import time
from datetime import datetime, time as dt_time, timedelta
import pytz
from dotenv import load_dotenv

from tuya_client import TuyaClient
from storage.db_client import MongoDBClient
from utils.preprocessor import DataPreprocessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
ACCESS_ID = os.getenv("TUYA_ACCESS_ID")
ACCESS_SECRET = os.getenv("TUYA_ACCESS_SECRET")
ENDPOINT = os.getenv("TUYA_ENDPOINT")
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "sarimax_thesis")

DEVICES = {
    "Aircon": "a3ed2fe218a724b4fepeni",
    "Refrigerator": "a3986d20c19f33c7c107fw",
    "Electric_Fan": "a3c772d3fde52dbae832bi"
}

MANILA_TZ = pytz.timezone("Asia/Manila")
PROCESSED_DATA_DIR = "data/processed_data"

class HistoricalBackfiller:
    def __init__(self, drop=False, export=False):
        self.tuya = TuyaClient(ACCESS_ID, ACCESS_SECRET, ENDPOINT)
        self.db = MongoDBClient(MONGODB_URI, DATABASE_NAME) if MONGODB_URI else None
        self.preprocessor = DataPreprocessor()
        self.drop = drop
        self.export = export
        
        if self.export and not os.path.exists(PROCESSED_DATA_DIR):
            os.makedirs(PROCESSED_DATA_DIR)

    def generate_day_intervals(self, date_obj):
        """Generates 144 target timestamps for a single day."""
        intervals = []
        base_time = datetime.combine(date_obj, dt_time.min).replace(tzinfo=MANILA_TZ)
        for i in range(144):
            intervals.append(base_time + timedelta(minutes=i * 10))
        return intervals

    def export_to_csv(self, appliance_name, date_str, readings):
        """Exports normalized readings to a CSV file."""
        day_dir = os.path.join(PROCESSED_DATA_DIR, date_str)
        if not os.path.exists(day_dir):
            os.makedirs(day_dir)
        
        filepath = os.path.join(day_dir, f"{appliance_name.lower()}.csv")
        headers = ["timestamp", "voltage_v", "current_a", "power_w", "total_kwh", "is_active"]
        
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for r in readings:
                p = r.get("processed_data") or {}
                row = {
                    "timestamp": r["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                    "voltage_v": p.get("voltage_v"),
                    "current_a": p.get("current_a"),
                    "power_w": p.get("power_w"),
                    "total_kwh": p.get("total_kwh_accumulated"),
                    "is_active": p.get("is_active")
                }
                writer.writerow(row)
        logger.info(f"Exported {appliance_name} to {filepath}")

    def process_day(self, date_obj):
        date_str = date_obj.strftime("%Y-%m-%d")
        logger.info(f"--- Processing Day: {date_str} ---")

        for name, dev_id in DEVICES.items():
            if self.drop and self.db:
                self.db.drop_daily_data(name, date_str)

            intervals = self.generate_day_intervals(date_obj)
            
            # Fetch historical logs in 2-hour chunks to avoid "Data volume too large" and trial limits
            all_logs = []
            chunk_size_hours = 2
            
            for hour in range(0, 24, chunk_size_hours):
                chunk_start = datetime.combine(date_obj, dt_time(hour, 0)).replace(tzinfo=MANILA_TZ)
                # End of chunk is either +2 hours or end of day
                if hour + chunk_size_hours >= 24:
                    chunk_end = datetime.combine(date_obj, dt_time(23, 59, 59)).replace(tzinfo=MANILA_TZ)
                else:
                    chunk_end = datetime.combine(date_obj, dt_time(hour + chunk_size_hours, 0)).replace(tzinfo=MANILA_TZ) - timedelta(seconds=1)

                start_ts = int(chunk_start.timestamp() * 1000)
                end_ts = int(chunk_end.timestamp() * 1000)
                
                logger.info(f"Fetching logs for {name} ({date_str} {hour:02d}:00 - {chunk_end.strftime('%H:%M:%S')})...")
                logs = self.tuya.get_historical_logs(dev_id, start_ts, end_ts)
                
                if logs:
                    all_logs.extend(logs)
                
                # Small sleep between chunks to be polite to the trial quota
                time.sleep(1)

            if not all_logs:
                logger.warning(f"No logs found for {name} on {date_str} after chunked fetching")
                continue

            logs = all_logs

            daily_readings = []
            last_status = {}

            for target_time in intervals:
                target_ms = int(target_time.timestamp() * 1000)
                
                # Find the closest log entry (within 10 minutes)
                # We sort logs by time to find the best match efficiently
                # But for now, we'll just filter
                relevant_logs = [l for l in logs if abs(l["event_time"] - target_ms) < 300000] # 5 mins window
                
                if relevant_logs:
                    # Use the latest log in this window to update state
                    current_status = last_status.copy()
                    for l in relevant_logs:
                        current_status[l["code"]] = l["value"]
                    last_status = current_status
                else:
                    # If no log in window, carry forward last known state
                    current_status = last_status
                
                processed = self.preprocessor.normalize(name, current_status)
                
                reading = {
                    "timestamp": target_time,
                    "interval_index": intervals.index(target_time),
                    "raw_data": current_status,
                    "processed_data": processed
                }
                
                if self.db:
                    # We use a custom insert if we dropped data, or update if we didn't
                    # To keep it simple, we store it via the db_client's method
                    self.db.store_reading(name, dev_id, target_time, reading["raw_data"], 
                                         {"temp": None, "humidity": None, "pressure": None}, 
                                         processed_data=processed)
                
                daily_readings.append(reading)

            if self.export:
                self.export_to_csv(name, date_str, daily_readings)

            if self.db:
                self.db.final_daily_validation(name, date_str)

    def run(self, start_date_str, end_date_str):
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        
        current_date = start_date
        while current_date <= end_date:
            self.process_day(current_date)
            current_date += timedelta(days=1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean historical backfiller for Tuya data")
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--drop", action="store_true", help="Drop existing MongoDB data for these dates")
    parser.add_argument("--export", action="store_true", help="Export processed data to CSV")
    
    args = parser.parse_args()
    
    backfiller = HistoricalBackfiller(drop=args.drop, export=args.export)
    backfiller.run(args.start, args.end)
