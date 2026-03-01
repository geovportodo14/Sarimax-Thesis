import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

# ─────────────────────────────────────────────────────────────
# TH2_Mongo_Extractor  (v2 — reads from unified 'energybuckets')
# ─────────────────────────────────────────────────────────────
# The EnergyBucket schema stores:
#   date, device_id, appliance_type,
#   readings[]: { timestamp, processed_data: { power_w, total_kwh_accumulated } }
#
# Stage A expects these smartplug columns:
#   timestamp, device_id, switch,
#   voltage_raw, current_raw, power_raw, kwh_raw,
#   voltage_v, current_a, power_w, kwh_total, pf
#
# Since the bucket schema only stores power_w and total_kwh,
# we derive the other electrical fields using PH nominal values:
#   voltage = 230 V,  pf = 1.0,  current = power / (voltage * pf)
# ─────────────────────────────────────────────────────────────

NOMINAL_VOLTAGE = 230.0   # Philippines nominal voltage
NOMINAL_PF = 1.0          # Assume unity power factor

def extract_mongo_data():
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DATABASE_NAME", "sarimax_thesis")

    if not uri:
        print("Error: MONGODB_URI not found in .env")
        return

    client = MongoClient(uri)
    db = client[db_name]

    # Read from the unified 'energybuckets' collection
    collection = db["energybuckets"]
    target_appliances = ["aircon", "refrigerator", "electricfan"]

    all_smartplug_readings = []
    all_weather_readings = []
    seen_weather_ts = set()

    print(f"Fetching from 'energybuckets' collection (appliances: {target_appliances})...")
    cursor = collection.find({"appliance_type": {"$in": target_appliances}})

    doc_count = 0
    for doc in cursor:
        doc_count += 1
        device_id = doc.get("device_id")
        readings = doc.get("readings", [])

        for r in readings:
            ts = r.get("timestamp")
            processed = r.get("processed_data", {})

            power_w = processed.get("power_w", 0)
            kwh_total = processed.get("total_kwh_accumulated", 0)

            # Derive electrical fields from power_w
            current_a = power_w / (NOMINAL_VOLTAGE * NOMINAL_PF) if NOMINAL_VOLTAGE > 0 else 0

            # The 'raw' fields use Tuya scaling conventions:
            #   voltage_raw = voltage * 10  (centivolts)
            #   current_raw = current * 1000 (milliamps)
            #   power_raw   = power * 10    (deciwatts)
            #   kwh_raw     = kwh * 100
            voltage_raw = round(NOMINAL_VOLTAGE * 10)
            current_raw = round(current_a * 1000)
            power_raw = round(power_w * 10)
            kwh_raw = round(kwh_total * 100)

            reading_data = {
                "timestamp": ts,
                "device_id": device_id,
                "switch": power_w > 0,  # Infer ON/OFF from power
                "voltage_raw": voltage_raw,
                "current_raw": current_raw,
                "power_raw": power_raw,
                "kwh_raw": kwh_raw,
                "voltage_v": NOMINAL_VOLTAGE,
                "current_a": round(current_a, 6),
                "power_w": round(power_w, 4),
                "kwh_total": round(kwh_total, 4),
                "pf": NOMINAL_PF,
            }
            all_smartplug_readings.append(reading_data)

            # Weather — energybuckets don't store weather data,
            # so we create a minimal placeholder row per unique timestamp
            # to prevent Stage A from crashing on an empty weather CSV.
            if ts and ts not in seen_weather_ts:
                all_weather_readings.append({
                    "timestamp": ts,
                    "temperature": None,
                    "humidity": None,
                    "pressure": None,
                })
                seen_weather_ts.add(ts)

    client.close()

    print(f"Scanned {doc_count} bucket documents.")

    if not all_smartplug_readings:
        print("No readings found in 'energybuckets'. Nothing to export.")
        return

    # Create DataFrames
    df_sp = pd.DataFrame(all_smartplug_readings)
    df_wx = pd.DataFrame(all_weather_readings)

    # Get project paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../../"))
    raw_data_dir = os.path.join(project_root, "data/raw")
    os.makedirs(raw_data_dir, exist_ok=True)

    # Sort and save
    df_sp.sort_values(["device_id", "timestamp"], inplace=True)
    df_wx.sort_values("timestamp", inplace=True)

    sp_path = os.path.join(raw_data_dir, "smartplug_raw.csv")
    wx_path = os.path.join(raw_data_dir, "weather_raw.csv")

    df_sp.to_csv(sp_path, index=False)

    # Only write weather CSV if no real backfilled data already exists
    # (weather_backfill.py writes real Open-Meteo data here)
    should_write_weather = True
    if os.path.exists(wx_path):
        try:
            existing_wx = pd.read_csv(wx_path)
            if not existing_wx.empty and "temperature" in existing_wx.columns and existing_wx["temperature"].notna().any():
                print(f"Skipping weather_raw.csv — already contains {existing_wx['temperature'].notna().sum()} real weather records from backfill.")
                should_write_weather = False
        except Exception:
            pass  # If we can't read it, just overwrite

    if should_write_weather:
        df_wx.to_csv(wx_path, index=False)
        print(f"Wrote {len(df_wx)} weather placeholder records (run weather_backfill.py for real data).")

    print(f"Successfully extracted {len(df_sp)} smartplug readings and {len(df_wx)} weather records to {raw_data_dir}")

if __name__ == "__main__":
    extract_mongo_data()
