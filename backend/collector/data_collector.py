import time
import os
import csv
import logging
from datetime import datetime, time as dt_time, timedelta
import pytz
from dotenv import load_dotenv

from tuya_client import TuyaClient
from utils.weather_client import WeatherClient
from storage.db_client import MongoDBClient
from utils.preprocessor import DataPreprocessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/collector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load config
load_dotenv()

# Configuration (Hardcoded for reliability)
ACCESS_ID = os.getenv("TUYA_ACCESS_ID", "trfs5ycjmhh4cs9sehnr")
ACCESS_SECRET = os.getenv("TUYA_ACCESS_SECRET", "367f3cd4abf8457a8116de9b2ed28f70")
ENDPOINT = os.getenv("TUYA_ENDPOINT", "https://openapi-sg.iotbing.com")
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "sarimax_thesis")
ENABLE_INITIAL_BACKFILL = os.getenv("ENABLE_INITIAL_BACKFILL", "false").lower() == "true"

DEVICES = {
    "Aircon": "a3ed2fe218a724b4fepeni",
    "Refrigerator": "a3986d20c19f33c7c107fw",
    "Electric_Fan": "a3c772d3fde52dbae832bi"
}

CSV_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/archive/energy_data"))
MANILA_TZ = pytz.timezone("Asia/Manila")

class DataCollector:
    def __init__(self):
        self.tuya = TuyaClient(ACCESS_ID, ACCESS_SECRET, ENDPOINT)
        self.weather = WeatherClient(WEATHER_API_KEY, "Manila")
        self.db = MongoDBClient(MONGODB_URI, DATABASE_NAME) if MONGODB_URI else None
        self.preprocessor = DataPreprocessor()
        
        # Ensure archive directory exists
        if not os.path.exists(CSV_FOLDER):
            os.makedirs(CSV_FOLDER)

    def _get_csv_file(self):
        """Returns the path to today's CSV file, creating it with headers if missing."""
        filename = f"energy_log_{datetime.now(MANILA_TZ).strftime('%Y%m%d')}.csv"
        filepath = os.path.join(CSV_FOLDER, filename)
        
        if not os.path.isfile(filepath):
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                # Matches legacy schema for compatibility with refined_csv_migrator.py
                csv.writer(f).writerow(["timestamp", "device", "property", "value", "temp_C", "humidity", "pressure"])
        return filepath

    def log_to_csv(self, timestamp, device, status, weather):
        """Appends a reading to the daily CSV file."""
        filepath = self._get_csv_file()
        with open(filepath, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            # Weather fallback handling
            temp = weather.get("temp") if weather else None
            hum = weather.get("humidity") if weather else None
            press = weather.get("pressure") if weather else None

            if status:
                for code, val in status.items():
                    w.writerow([timestamp, device, code, val, temp, hum, press])
            else:
                w.writerow([timestamp, device, "NO_DATA", None, temp, hum, press])

    def collect_once(self):
        now_manila = datetime.now(MANILA_TZ)
        ts_str = now_manila.strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Starting collection at {ts_str}")

        weather_data = self.weather.get_weather()
        
        for name, dev_id in DEVICES.items():
            status = self.tuya.get_device_status(dev_id)
            
            # 1. Log to CSV (backwards compatibility)
            self.log_to_csv(ts_str, name, status, weather_data)
            
            # 2. Store in MongoDB
            if self.db and status:
                processed = self.preprocessor.normalize(name, status)
                self.db.store_reading(name, dev_id, now_manila, status, weather_data, processed_data=processed)
            
            time.sleep(1) # Small delay between devices

    def backfill_appliance_day(self, name, dev_id, date_obj):
        date_str = date_obj.strftime("%Y-%m-%d")
        missing_intervals = self.db.get_missing_intervals(name, date_str)
        
        if not missing_intervals:
            logger.info(f"No missing intervals for {name} on {date_str}. Proceeding to validation.")
        else:
            logger.info(f"Backfilling {len(missing_intervals)} intervals for {name} on {date_str}")
            
            # Calculate which 2-hour chunks are actually needed
            needed_chunks = set()
            for idx in missing_intervals:
                # 144 intervals over 24 hours = 6 intervals per hour
                # Index 0-11 = 0-2am, 12-23 = 2-4am, etc.
                chunk_hour = (idx // 6) // 2 * 2
                needed_chunks.add(chunk_hour)

            all_logs = []
            chunk_size_hours = 2
            
            for hour in sorted(list(needed_chunks)):
                chunk_start = datetime.combine(date_obj, dt_time(hour, 0)).replace(tzinfo=MANILA_TZ)
                if hour + chunk_size_hours >= 24:
                    chunk_end = datetime.combine(date_obj, dt_time(23, 59, 59)).replace(tzinfo=MANILA_TZ)
                else:
                    chunk_end = datetime.combine(date_obj, dt_time(hour + chunk_size_hours, 0)).replace(tzinfo=MANILA_TZ) - timedelta(seconds=1)

                start_ts = int(chunk_start.timestamp() * 1000)
                end_ts = int(chunk_end.timestamp() * 1000)
                
                logger.info(f"Smart Backfill {name}: Chunk {hour:02d}:00 to {chunk_end.strftime('%H:%M:%S')}...")
                logs = self.tuya.get_historical_logs(dev_id, start_ts, end_ts)
                if logs:
                    all_logs.extend(logs)
                else:
                    logger.warning(f"Aborting backfill for {name} for this chunk due to no data or quota.")
                    break
                time.sleep(1)

            if not all_logs:
                logger.warning(f"No historical logs found for {name} on {date_str}")
            
            else:
                for idx in missing_intervals:
                    target_time = datetime.combine(date_obj, dt_time.min).replace(tzinfo=MANILA_TZ) + timedelta(minutes=idx * 10)
                    target_ms = int(target_time.timestamp() * 1000)
                    
                    # Find the closest log entry (within 10 minutes)
                    interval_logs = [l for l in all_logs if abs(l["event_time"] - target_ms) < 300000] 
                    if interval_logs:
                        status = {}
                        for l in interval_logs:
                            status[l["code"]] = l["value"]
                        
                        weather_placeholder = {"temp": None, "humidity": None, "pressure": None}
                        processed = self.preprocessor.normalize(name, status)
                        self.db.store_reading(name, dev_id, target_time, status, weather_placeholder, processed_data=processed)

        # Final check & Summary Generation (Always run this!)
        summary = self.db.final_daily_validation(name, date_str)
        return summary.get("is_complete", False) if summary else False

    def check_and_backfill_previous_day(self):
        yesterday = datetime.now(MANILA_TZ).date() - timedelta(days=1)
        yesterday_str = yesterday.strftime("%Y-%m-%d")
        logger.info(f"Starting completeness check for {yesterday_str}")
        
        all_complete = True
        for name, dev_id in DEVICES.items():
            is_complete = self.backfill_appliance_day(name, dev_id, yesterday)
            if not is_complete:
                all_complete = False
                logger.warning(f"{name} is incomplete ({self.db.get_daily_count(name, yesterday_str)}/144).")
        
        if all_complete:
            logger.info(f"All devices complete (144/144) for {yesterday_str}. Data is ready for local preprocessing.")
            # self.trigger_preprocessing() # Disabled for Azure deployment to save resources
        else:
            logger.info(f"Daily check for {yesterday_str}: Some devices are still incomplete. Collector will keep backfilling.")

    def trigger_preprocessing(self):
        """Triggers the TH2 Preprocessing Pipeline to update modeling datasets."""
        try:
            logger.info("Triggering automated TH2 Preprocessing Pipeline...")
            # Import inside function to handle potential path issues at runtime
            import sys
            root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
            if root_path not in sys.path:
                sys.path.append(root_path)
            
            from backend.preprocessing.TH2_Pipeline_Runner import run_full_pipeline
            run_full_pipeline()
            logger.info("Automated Preprocessing Pipeline completed successfully.")
        except Exception as e:
            logger.exception(f"Failed to run automated preprocessing: {e}")

    def run_forever(self):
        logger.info("Collector started. Waiting for next 10-minute interval...")
        last_check_date = datetime.now(MANILA_TZ).date()
        
        while True:
            now = datetime.now(MANILA_TZ)
            current_date = now.date()
            
            # Day transition check (at midnight)
            if current_date > last_check_date:
                try:
                    self.check_and_backfill_previous_day()
                except Exception as e:
                    logger.exception("Error during daily backfill check")
                last_check_date = current_date

            # Align to next 10-minute mark (:00, :10, :20, etc.)
            minutes_to_wait = 10 - (now.minute % 10)
            seconds_to_wait = (minutes_to_wait * 60) - now.second
            
            if seconds_to_wait <= 0:
                seconds_to_wait = 600

            logger.info(f"Next collection in {seconds_to_wait} seconds")
            if seconds_to_wait > 0:
                time.sleep(seconds_to_wait)
            
            try:
                self.collect_once()
            except Exception as e:
                logger.exception("Error during collection cycle")
                time.sleep(60)

if __name__ == "__main__":
    collector = DataCollector()
    if ENABLE_INITIAL_BACKFILL:
        try:
            collector.check_and_backfill_previous_day()
        except Exception:
            logger.exception("Failed initial smart backfill check")
    else:
        logger.info("Initial backfill skipped (ENABLE_INITIAL_BACKFILL=false)")
    collector.run_forever()
