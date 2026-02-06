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
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
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

# Daily Target Energy (kWh) for Jan 12 to Jan 25 (14 days)
TARGET_ENERGY = {
    "Aircon": [3.88, 3.76, 3.75, 4.10, 3.33, 3.90, 3.79, 3.58, 3.73, 3.63, 2.99, 3.17, 3.44, 4.19],
    "Refrigerator": [2.42, 2.34, 2.25, 2.25, 2.33, 2.21, 2.46, 2.25, 2.42, 2.21, 2.14, 2.00, 1.09, 2.24],
    "Electric_Fan": [0.29, 0.33, 0.30, 0.27, 0.27, 0.33, 0.46, 0.30, 0.32, 0.40, 0.33, 0.33, 0.39, 0.48]
}

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
                        raw_sums[device_name][idx].append(processed)
            
            current += timedelta(days=1)

        # Calculate averages for the profile
        for name in DEVICES:
            for idx in range(144):
                if raw_sums[name][idx]:
                    # We take the representative (median or average) reading for this interval
                    avg_power = statistics.mean([r["power_w"] for r in raw_sums[name][idx]])
                    avg_voltage = statistics.mean([r.get("voltage_v", 230) for r in raw_sums[name][idx]])
                    avg_current = statistics.mean([r.get("current_a", 0) for r in raw_sums[name][idx]])
                    
                    self.profiles[name][idx] = {
                        "power_w": avg_power,
                        "voltage_v": avg_voltage,
                        "current_a": avg_current,
                        "is_active": any([r.get("is_active") for r in raw_sums[name][idx]])
                    }
                else:
                    # Fallback if no data at all for an interval
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
                    ts_str_raw = row['timestamp']
                    device_name = row['device']
                    prop = row['property']
                    value = row['value']
                    
                    if device_name not in DEVICES or prop == "NO_DATA":
                        continue
                    
                    # Normalize timestamp to the nearest 10-minute mark (floor)
                    dt_obj = datetime.strptime(ts_str_raw, "%Y-%m-%d %H:%M:%S")
                    normalized_minute = (dt_obj.minute // 10) * 10
                    normalized_dt = dt_obj.replace(minute=normalized_minute, second=0, microsecond=0)
                    ts_str_normalized = normalized_dt.strftime("%Y-%m-%d %H:%M:%S")

                    if ts_str_normalized not in device_readings[device_name]:
                        device_readings[device_name][ts_str_normalized] = {
                            "raw": {},
                            "weather": {
                                "temp": float(row['temp_C']) if row['temp_C'] else None,
                                "humidity": float(row['humidity']) if row['humidity'] else None,
                                "pressure": float(row['pressure']) if row['pressure'] else None
                            }
                        }
                        logger.debug(f"[{device_name}] Parsed weather: {device_readings[device_name][ts_str_normalized]['weather']}")
                    device_readings[device_name][ts_str_normalized]["raw"][prop] = value
        except Exception as e:
            logger.error(f"Error parsing {filepath}: {e}")
        return device_readings

    def process_day(self, date_obj):
        date_str = date_obj.strftime("%Y-%m-%d")
        csv_filename = f"energy_log_{date_obj.strftime('%Y%m%d')}.csv"
        filepath = os.path.join(self.folder_path, csv_filename)
        
        logger.info(f"--- Reconstructing Day: {date_str} ---")
        
        logger.debug(f"[process_day] Checking CSV file: {filepath}")
        csv_exists = os.path.exists(filepath)
        logger.debug(f"[process_day] CSV file exists: {csv_exists}")
        
        # Load real data if available
        real_day_data = self._parse_csv_file(filepath) if csv_exists else {}

        for name, dev_id in DEVICES.items():
            if self.drop and self.db:
                self.db.drop_daily_data(name, date_str)

            daily_readings = []
            
            # --- Scaling Logic for Jan 12 - Jan 25 ---
            scaling_factor = 1.0
            target_range_start = datetime(2026, 1, 12).date()
            target_range_end = datetime(2026, 1, 25).date()
            
            if target_range_start <= date_obj <= target_range_end:
                day_offset = (date_obj - target_range_start).days
                target_kwh = TARGET_ENERGY[name][day_offset]
                
                # Calculate baseline energy for the pattern
                baseline_energy = sum([p["power_w"] for p in self.profiles[name]]) / 6000.0 # (P/6) / 1000
                if baseline_energy > 0:
                    scaling_factor = target_kwh / baseline_energy
                    logger.info(f"Day {date_str} {name}: Target={target_kwh}kWh, Baseline={baseline_energy:.3f}kWh, Scaling={scaling_factor:.3f}")
            
            # Generate 144 intervals
            base_time = datetime.combine(date_obj, time.min) # Naive
            base_time_aware = MANILA_TZ.localize(base_time)  # Aware
            accumulated_kwh = 0.0
            
            for i in range(144):
                target_time = base_time_aware + timedelta(minutes=i * 10)
                ts_key = target_time.strftime("%Y-%m-%d %H:%M:%S")
                
                # 1. Try to find real data in the window
                found_data = None
                use_real_data = False
                
                if name in real_day_data:
                    if ts_key in real_day_data[name]:
                        found_data = real_day_data[name][ts_key]
                
                if found_data:
                    processed = self.preprocessor.normalize(name, found_data["raw"])
                    if processed:
                        use_real_data = True
                        weather = found_data["weather"]
                        raw = found_data["raw"]
                        
                        # Energy Handling: Prefer direct CSV reading (add_ele)
                        # Only use integral if add_ele/total_kwh is missing
                        energy_in_interval = (processed.get("power_w", 0) / 6.0) / 1000.0
                        accumulated_kwh += energy_in_interval
                        
                        if processed.get("total_kwh_accumulated") is None or processed.get("total_kwh_accumulated") == 0:
                             processed["total_kwh_accumulated"] = round(accumulated_kwh, 3) 
                    else:
                         logger.warning(f"Normalization failed for {name} at {ts_key}. raw={found_data['raw']}")

                if not use_real_data:
                    # 2. Use Pattern-Based Smart Fill + Scaling
                    base_profile = self.profiles[name][i].copy()
                    weather = {"temp": None, "humidity": None, "pressure": None}
                    
                    # Scale properties
                    scaled_power = base_profile["power_w"] * scaling_factor
                    scaled_current = (scaled_power / base_profile["voltage_v"]) if base_profile["voltage_v"] > 0 else 0
                    
                    processed = {
                        "power_w": round(scaled_power, 2),
                        "voltage_v": round(base_profile["voltage_v"], 2),
                        "current_a": round(scaled_current, 3),
                        "is_active": base_profile["is_active"],
                        # "total_kwh_accumulated" will be added below after accumulated_kwh is updated
                    }
                    
                    energy_in_interval = (scaled_power / 6.0) / 1000.0
                    accumulated_kwh += energy_in_interval
                    processed["total_kwh_accumulated"] = round(accumulated_kwh, 3)

                    # Generate realistic Tuya raw values (Matches the device's extended schema)
                    raw = {
                        "switch_1": True,
                        "countdown_1": 0,
                        "add_ele": int(accumulated_kwh * 100), # 1 unit = 0.01 kWh
                        "cur_current": int(scaled_current * 1000),
                        "cur_power": int(scaled_power * 10),
                        "cur_voltage": int(base_profile["voltage_v"] * 10),
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
                
                logger.debug(f"[process_day] {name} {ts_key} Final weather before DB: {weather}") # <--- Debug log

                reading = {
                    "timestamp": target_time,
                    "interval_index": i,
                    "raw_data": raw,
                    "processed_data": processed,
                    "weather": weather
                }
                
                if self.db:
                    existing_mongo_reading = self.db.get_reading(name, date_str, i)
                    
                    if existing_mongo_reading:
                        # If a reading exists, update weather if there's new weather data available (not all None)
                        # The 'weather' variable here comes from either found_data (CSV) or pattern fill.
                        # If it came from found_data, it contains values. If pattern, it's all None.
                        if weather and any(v is not None for k,v in weather.items() if k != "timestamp"): # Check if 'weather' contains actual data
                            self.db.update_reading_weather(name, date_str, i, weather)
                            logger.debug(f"[process_day] {name} {ts_key} calling update_reading_weather with: {weather}") # <--- Debug log
                        
                        # Use the existing reading (potentially with updated weather) for export list and accumulated_kwh
                        final_reading_for_export = existing_mongo_reading.copy()
                        if weather and any(v is not None for k,v in weather.items() if k != "timestamp"):
                            final_reading_for_export["weather"] = weather # Overlay new weather
                        
                        daily_readings.append(final_reading_for_export)

                        if "processed_data" in final_reading_for_export and "total_kwh_accumulated" in final_reading_for_export["processed_data"]:
                            accumulated_kwh = final_reading_for_export["processed_data"]["total_kwh_accumulated"]
                    else:
                        # No existing reading, so push a new one
                        self.db.store_reading(name, dev_id, target_time, raw, weather, processed_data=processed)
                        logger.debug(f"[process_day] {name} {ts_key} calling store_reading with: {weather}") # <--- Debug log
                        daily_readings.append(reading)
                else:
                    # If DB is not enabled, just append the locally constructed reading for export
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
