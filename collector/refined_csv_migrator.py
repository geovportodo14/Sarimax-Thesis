import csv
import os
import logging
import argparse
from datetime import datetime, time, timedelta
import pytz
from dotenv import load_dotenv
import statistics

from storage.db_client import MongoDBClient
from utils.preprocessor import DataPreprocessor

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

PROCESSED_DATA_DIR = "data/processed_data"

class RefinedCSVMigrator:
    def __init__(self, folder_path, drop=False, export=False):
        self.folder_path = folder_path
        self.db = MongoDBClient(MONGODB_URI, DATABASE_NAME) if MONGODB_URI else None
        self.preprocessor = DataPreprocessor()
        self.drop = drop
        self.export = export
        self.profiles = {name: [[] for _ in range(144)] for name in DEVICES}

        if self.export and not os.path.exists(PROCESSED_DATA_DIR):
            os.makedirs(PROCESSED_DATA_DIR)

    def learn_patterns(self, start_date_str, end_date_str):
        """Builds average consumption profiles per appliance per interval."""
        logger.info(f"Learning patterns from {start_date_str} to {end_date_str}...")
        
        start_date = datetime.strptime(start_date_str, "%Y%m%d").date()
        end_date = datetime.strptime(end_date_str, "%Y%m%d").date()
        
        current = start_date
        while current <= end_date:
            filename = f"energy_log_{current.strftime('%Y%m%d')}.csv"
            filepath = os.path.join(self.folder_path, filename)
            if not os.path.exists(filepath):
                current += timedelta(days=1)
                continue
            
            day_readings = self._parse_csv_file(filepath)
            for device_name, readings in day_readings.items():
                for ts_str, data in readings.items():
                    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=MANILA_TZ)
                    idx = (ts.hour * 6) + (ts.minute // 10)
                    
                    processed = self.preprocessor.normalize(device_name, data["raw"])
                    if processed and processed.get("power_w") is not None:
                        self.profiles[device_name][idx].append(processed)
            
            current += timedelta(days=1)

        # Calculate averages for the profile
        for name in DEVICES:
            for idx in range(144):
                if self.profiles[name][idx]:
                    # We take the representative (median or average) reading for this interval
                    avg_power = statistics.mean([r["power_w"] for r in self.profiles[name][idx]])
                    avg_voltage = statistics.mean([r.get("voltage_v", 230) for r in self.profiles[name][idx]])
                    avg_current = statistics.mean([r.get("current_a", 0) for r in self.profiles[name][idx]])
                    
                    self.profiles[name][idx] = {
                        "power_w": avg_power,
                        "voltage_v": avg_voltage,
                        "current_a": avg_current,
                        "is_active": any([r.get("is_active") for r in self.profiles[name][idx]]),
                        "total_kwh_accumulated": self.profiles[name][idx][-1].get("total_kwh_accumulated", 0) # Fallback
                    }
                else:
                    # Fallback if no data at all for an interval
                    self.profiles[name][idx] = {
                        "power_w": 0, "voltage_v": 230, "current_a": 0, "is_active": False, "total_kwh_accumulated": 0
                    }
        logger.info("Pattern learning complete.")

    def _parse_csv_file(self, filepath):
        """Groups CSV rows by (device, timestamp)."""
        device_readings = {name: {} for name in DEVICES}
        try:
            with open(filepath, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ts_str = row['timestamp']
                    device_name = row['device']
                    prop = row['property']
                    value = row['value']
                    
                    if device_name not in DEVICES or prop == "NO_DATA":
                        continue
                    
                    if ts_str not in device_readings[device_name]:
                        device_readings[device_name][ts_str] = {
                            "raw": {},
                            "weather": {
                                "temp": float(row['temp_C']) if row['temp_C'] else None,
                                "humidity": float(row['humidity']) if row['humidity'] else None,
                                "pressure": float(row['pressure']) if row['pressure'] else None
                            }
                        }
                    device_readings[device_name][ts_str]["raw"][prop] = value
        except Exception as e:
            logger.error(f"Error parsing {filepath}: {e}")
        return device_readings

    def process_day(self, date_obj):
        date_str = date_obj.strftime("%Y-%m-%d")
        csv_filename = f"energy_log_{date_obj.strftime('%Y%m%d')}.csv"
        filepath = os.path.join(self.folder_path, csv_filename)
        
        logger.info(f"--- Reconstructing Day: {date_str} ---")
        
        # Load real data if available
        real_day_data = self._parse_csv_file(filepath) if os.path.exists(filepath) else {}

        for name, dev_id in DEVICES.items():
            if self.drop and self.db:
                self.db.drop_daily_data(name, date_str)

            daily_readings = []
            
            # Generate 144 intervals
            base_time = datetime.combine(date_obj, time.min).replace(tzinfo=MANILA_TZ)
            
            for i in range(144):
                target_time = base_time + timedelta(minutes=i * 10)
                ts_key = target_time.strftime("%Y-%m-%d %H:%M:%S")
                
                # 1. Try to find real data in the window
                found_data = None
                if name in real_day_data:
                    # Look for exact or very close matches
                    # For simplicity, we check the exact 10-minute mark first
                    if ts_key in real_day_data[name]:
                        found_data = real_day_data[name][ts_key]
                
                if found_data:
                    processed = self.preprocessor.normalize(name, found_data["raw"])
                    weather = found_data["weather"]
                    raw = found_data["raw"]
                else:
                    # 2. Use Pattern-Based Smart Fill
                    processed = self.profiles[name][i].copy()
                    weather = {"temp": None, "humidity": None, "pressure": None}
                    
                    # Generate realistic Tuya raw values (Matches the device's extended schema)
                    raw = {
                        "switch_1": True,
                        "countdown_1": 0,
                        "add_ele": int(processed.get("total_kwh_accumulated", 0) * 100),
                        "cur_current": int(processed.get("current_a", 0) * 1000),
                        "cur_power": int(processed.get("power_w", 0) * 10),
                        "cur_voltage": int(processed.get("voltage_v", 230) * 10),
                        "voltage_coe": 567,
                        "electric_coe": 29676,
                        "power_coe": 15976,
                        "electricity_coe": 2610,
                        "fault": 0,
                        "relay_status": "last",
                        "overcharge_switch": False,
                        "light_mode": "relay",
                        "child_lock": False,
                        "cycle_time": "",
                        "random_time": "",
                        "switch_inching": ""
                    }
                
                reading = {
                    "timestamp": target_time,
                    "interval_index": i,
                    "raw_data": raw,
                    "processed_data": processed,
                    "weather": weather
                }
                
                if self.db:
                    self.db.store_reading(name, dev_id, target_time, raw, weather, processed_data=processed)
                
                daily_readings.append(reading)

            if self.export:
                self._export_to_csv(name, date_str, daily_readings)

            if self.db:
                self.db.final_daily_validation(name, date_str)

    def _export_to_csv(self, appliance_name, date_str, readings):
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

    def run(self, start_date_str, end_date_str):
        # 1. Learn from Jan 3-11
        self.learn_patterns("20260103", "20260111")
        
        # 2. Process requested range
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        
        current_date = start_date
        while current_date <= end_date:
            self.process_day(current_date)
            current_date += timedelta(days=1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pattern-based historical CSV recovery")
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--folder", default="data/energy_data", help="Source CSV folder")
    parser.add_argument("--drop", action="store_true", help="Drop existing MongoDB data")
    parser.add_argument("--export", action="store_true", help="Export to processed_data folders")
    
    args = parser.parse_args()
    
    migrator = RefinedCSVMigrator(args.folder, drop=args.drop, export=args.export)
    migrator.run(args.start, args.end)
