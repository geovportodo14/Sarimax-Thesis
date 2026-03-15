import csv
import os
import logging
import argparse
import statistics
from datetime import datetime, time, timedelta
import pytz
from dotenv import load_dotenv

from pathlib import Path
from storage.db_client import MongoDBClient
from utils.preprocessor import DataPreprocessor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
repo_root = Path(__file__).resolve().parents[2]
load_dotenv(repo_root / ".env")
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "Sarimax-Thesis")
MANILA_TZ = pytz.timezone("Asia/Manila")

DEVICES = {
    "Aircon": "a3ed2fe218a724b4fepeni",
    "Refrigerator": "a3986d20c19f33c7c107fw",
    "Electric_Fan": "a3c772d3fde52dbae832bi"
}

# Daily Target Energy (kWh) for Jan 12 to Jan 25 (scaled to user-provided maximums)
# User Max: Aircon 4.5, Refrigerator 2.35, Electric Fan 0.64
TARGET_ENERGY = {
    "Aircon": [3.88, 3.76, 3.75, 4.10, 3.33, 3.90, 3.79, 3.58, 3.73, 3.63, 2.99, 3.17, 3.44, 4.19],
    "Refrigerator": [2.35, 2.34, 2.25, 2.25, 2.33, 2.21, 2.35, 2.25, 2.35, 2.21, 2.14, 2.00, 1.09, 2.24],
    "Electric_Fan": [0.29, 0.33, 0.30, 0.27, 0.27, 0.33, 0.46, 0.30, 0.32, 0.40, 0.33, 0.33, 0.39, 0.48]
}

PROCESSED_DATA_DIR = "data/intermediate/processed_readings"

class RefinedCSVMigrator:
    def __init__(self, folder_path, drop=False, export=False):
        self.folder_path = folder_path
        self.db = MongoDBClient(MONGODB_URI, DATABASE_NAME) if MONGODB_URI else None
        self.preprocessor = DataPreprocessor()
        self.drop = drop
        self.export = export
        self.profiles = {name: [None for _ in range(144)] for name in DEVICES}

        if self.export and not os.path.exists(PROCESSED_DATA_DIR):
            os.makedirs(PROCESSED_DATA_DIR)

    def learn_patterns(self, start_date_str, end_date_str):
        """Builds average consumption profiles per appliance per interval."""
        logger.info(f"Learning patterns from {start_date_str} to {end_date_str}...")
        
        raw_sums = {name: [[] for _ in range(144)] for name in DEVICES}
        
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
                        raw_sums[device_name][idx].append({
                            "power_w": processed["power_w"],
                            "voltage_v": processed.get("voltage_v", 230),
                            "current_a": processed.get("current_a", 0),
                            "is_active": processed.get("is_active", False)
                        })
            
            current += timedelta(days=1)

        # Calculate averages for the profile
        num_learning_days = (end_date - start_date).days + 1
        
        for name in DEVICES:
            for idx in range(144):
                if raw_sums[name][idx]:
                    # Statistical is_active: at least 50% frequency to be considered 'active' in pattern
                    active_count = sum([1 for r in raw_sums[name][idx] if r.get("is_active")])
                    is_active_flag = (active_count / num_learning_days) >= 0.5
                    
                    # Mean power over all days (including zero-days)
                    total_p = sum([r["power_w"] for r in raw_sums[name][idx]])
                    avg_power = total_p / num_learning_days
                    
                    avg_voltage = statistics.mean([r.get("voltage_v", 230) for r in raw_sums[name][idx]])
                    avg_current = statistics.mean([r.get("current_a", 0) for r in raw_sums[name][idx]])
                    
                    # Enforce zero if pattern is inactive
                    if not is_active_flag:
                        avg_power = 0.0
                        avg_current = 0.0

                    self.profiles[name][idx] = {
                        "power_w": avg_power,
                        "voltage_v": avg_voltage,
                        "current_a": avg_current,
                        "is_active": is_active_flag
                    }
                else:
                    self.profiles[name][idx] = {
                        "power_w": 0, "voltage_v": 230, "current_a": 0, "is_active": False
                    }
        logger.info("Pattern learning complete.")

    def _parse_csv_file(self, filepath):
        """Groups CSV rows by (device, timestamp)."""
        device_readings = {name: {} for name in DEVICES}
        try:
            with open(filepath, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    device_name = row['device']
                    if device_name not in DEVICES or row['property'] == "NO_DATA":
                        continue
                    
                    dt_obj = datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S")
                    normalized_dt = dt_obj.replace(minute=(dt_obj.minute // 10) * 10, second=0, microsecond=0)
                    ts_str = normalized_dt.strftime("%Y-%m-%d %H:%M:%S")

                    if ts_str not in device_readings[device_name]:
                        device_readings[device_name][ts_str] = {
                            "raw": {},
                            "weather": {
                                "temp": float(row['temp_C']) if row['temp_C'] else None,
                                "humidity": float(row['humidity']) if row['humidity'] else None,
                                "rainfall": float(row['rainfall']) if row.get('rainfall') else float(row.get('pressure')) if row.get('pressure') else None
                            }
                        }
                    device_readings[device_name][ts_str]["raw"][row['property']] = row['value']
        except Exception as e:
            logger.error(f"Error parsing {filepath}: {e}")
        return device_readings

    def process_day(self, date_obj):
        date_str = date_obj.strftime("%Y-%m-%d")
        csv_filename = f"energy_log_{date_obj.strftime('%Y%m%d')}.csv"
        filepath = os.path.join(self.folder_path, csv_filename)
        
        logger.info(f"--- Processing Day: {date_str} ---")
        real_day_data = self._parse_csv_file(filepath) if os.path.exists(filepath) else {}

        for name, dev_id in DEVICES.items():
            if self.drop and self.db:
                self.db.drop_daily_data(name, date_str)

            # --- Scaling Logic for Jan 12 - Jan 25 ---
            scaling_factor = 1.0
            target_range_start = datetime(2026, 1, 12).date()
            target_range_end = datetime(2026, 1, 25).date()
            
            if target_range_start <= date_obj <= target_range_end:
                day_offset = (date_obj - target_range_start).days
                target_kwh = TARGET_ENERGY[name][day_offset]
                baseline_energy = sum([p["power_w"] for p in self.profiles[name]]) / 6000.0
                if baseline_energy > 0:
                    scaling_factor = target_kwh / baseline_energy
            
            accumulated_kwh = 0.0
            daily_readings = []
            base_time_aware = MANILA_TZ.localize(datetime.combine(date_obj, time.min))

            for i in range(144):
                ts_key = (base_time_aware + timedelta(minutes=i * 10)).strftime("%Y-%m-%d %H:%M:%S")
                found_data = real_day_data.get(name, {}).get(ts_key)
                
                if found_data:
                    processed = self.preprocessor.normalize(name, found_data["raw"])
                    if processed:
                        energy_in_interval = (processed.get("power_w", 0) / 6.0) / 1000.0
                        if processed.get("is_active"):
                            accumulated_kwh += energy_in_interval
                        
                        processed["total_kwh_accumulated"] = round(accumulated_kwh, 3)
                        reading = {
                            "timestamp": base_time_aware + timedelta(minutes=i * 10),
                            "interval_index": i,
                            "raw_data": found_data["raw"],
                            "processed_data": processed,
                            "weather": found_data["weather"],
                            "processed_at": datetime.now()
                        }
                    else:
                        found_data = None

                if not found_data:
                    # Pattern-Based Smart Fill
                    p = self.profiles[name][i]
                    scaled_power = p["power_w"] * scaling_factor
                    scaled_curr = (scaled_power / p["voltage_v"]) if p["voltage_v"] > 0 else 0
                    
                    if p["is_active"]:
                        accumulated_kwh += (scaled_power / 6000.0)
                    
                    reading = {
                        "timestamp": base_time_aware + timedelta(minutes=i * 10),
                        "interval_index": i,
                        "raw_data": {
                            "switch_1": p["is_active"],
                            "add_ele": int(accumulated_kwh * 100),
                            "cur_current": int(scaled_curr * 1000),
                            "cur_power": int(scaled_power * 10),
                            "cur_voltage": int(p["voltage_v"] * 10),
                        },
                        "processed_data": {
                            "power_w": round(scaled_power, 2),
                            "voltage_v": round(p["voltage_v"], 2),
                            "current_a": round(scaled_curr, 3),
                            "is_active": p["is_active"],
                            "total_kwh_accumulated": round(accumulated_kwh, 3)
                        },
                        "weather": {"temp": None, "humidity": None, "rainfall": None},
                        "processed_at": datetime.now()
                    }
                daily_readings.append(reading)

            # Single Bulk Update per Day
            if self.db:
                self.db.db[name.lower()].update_one(
                    {"date": date_str, "device_id": dev_id},
                    {"$set": {
                        "readings": daily_readings,
                        "last_updated": datetime.now(),
                        "status": "complete",
                        "reading_count": 144
                    }, "$setOnInsert": {
                        "date": date_str, "device_id": dev_id, "appliance_type": name.lower(), "created_at": datetime.now()
                    }},
                    upsert=True
                )
                self.db.final_daily_validation(name, date_str)

            if self.export:
                self._export_to_csv(name, date_str, daily_readings)

    def _export_to_csv(self, name, date_str, readings):
        target_dir = os.path.join(PROCESSED_DATA_DIR, date_str)
        os.makedirs(target_dir, exist_ok=True)
        with open(os.path.join(target_dir, f"{name.lower()}.csv"), "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "voltage_v", "current_a", "power_w", "total_kwh", "is_active"])
            writer.writeheader()
            for r in readings:
                p = r["processed_data"]
                writer.writerow({
                    "timestamp": r["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                    "voltage_v": p["voltage_v"], "current_a": p["current_a"],
                    "power_w": p["power_w"], "total_kwh": p["total_kwh_accumulated"],
                    "is_active": p["is_active"]
                })

    def run(self, start_date_str, end_date_str):
        self.learn_patterns("20260103", "20260111")
        start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        current = start
        while current <= end:
            self.process_day(current)
            current += timedelta(days=1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--folder", default="data/archive/energy_data")
    parser.add_argument("--drop", action="store_true")
    parser.add_argument("--export", action="store_true")
    args = parser.parse_args()
    
    RefinedCSVMigrator(args.folder, drop=args.drop, export=args.export).run(args.start, args.end)
