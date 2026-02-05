import os
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

def extract_mongo_data():
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DATABASE_NAME", "sarimax_thesis")
    
    if not uri:
        print("Error: MONGODB_URI not found in .env")
        return

    client = MongoClient(uri)
    db = client[db_name]
    
    appliance_collections = ["aircon", "refrigerator", "electric_fan"]
    
    all_smartplug_readings = []
    all_weather_readings = []
    
    # Track seen weather timestamps to avoid duplicates in weather_raw.csv
    seen_weather_ts = set()

    for app in appliance_collections:
        print(f"Fetching data from collection: {app}")
        cursor = db[app].find({})
        
        for doc in cursor:
            device_id = doc.get("device_id")
            readings = doc.get("readings", [])
            
            for r in readings:
                ts = r.get("timestamp")
                raw = r.get("raw_data", {})
                weather = r.get("weather", {})
                
                # Smartplug Reading
                # We normalize slightly here to match Stage A required columns
                # but keep 'raw' values as well just in case.
                
                # Tuya values are often scaled:
                # cur_voltage: centivolts (e.g. 2300 = 230V) -> / 10
                # cur_current: milliamps (e.g. 1000 = 1A) -> / 1000
                # cur_power: deciwatts (e.g. 500 = 50W) -> / 10
                # add_ele: cumulative energy (often / 100 for kWh)
                
                v_raw = raw.get("cur_voltage") or raw.get("voltage")
                i_raw = raw.get("cur_current") or raw.get("current")
                p_raw = raw.get("cur_power") or raw.get("power")
                k_raw = raw.get("add_ele") or raw.get("cur_electricity")
                
                reading_data = {
                    "timestamp": ts,
                    "device_id": device_id,
                    "switch": raw.get("switch_1") or raw.get("switch") or False,
                    "voltage_raw": v_raw,
                    "current_raw": i_raw,
                    "power_raw": p_raw,
                    "kwh_raw": k_raw,
                    "voltage_v": float(v_raw)/10.0 if v_raw is not None else None,
                    "current_a": float(i_raw)/1000.0 if i_raw is not None else None,
                    "power_w": float(p_raw)/10.0 if p_raw is not None else None,
                    "kwh_total": float(k_raw)/100.0 if k_raw is not None else None,
                    "pf": raw.get("pf") or 1.0 # Default PF to 1.0 if not reported
                }
                all_smartplug_readings.append(reading_data)
                
                # Weather Reading (usually openweather data)
                if ts and ts not in seen_weather_ts:
                    weather_reading = {
                        "timestamp": ts,
                        "temperature": weather.get("temp") or weather.get("temp_C"),
                        "humidity": weather.get("humidity"),
                        "rainfall": weather.get("rain", 0.0) # Default to 0 if not present
                    }
                    all_weather_readings.append(weather_reading)
                    seen_weather_ts.add(ts)

    client.close()
    
    if not all_smartplug_readings:
        print("No readings found in MongoDB.")
        return

    # Create DataFrames
    df_sp = pd.DataFrame(all_smartplug_readings)
    df_wx = pd.DataFrame(all_weather_readings)
    
    # Get project root (2 levels up from backend/preprocessing/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../../"))
    raw_data_dir = os.path.join(project_root, "data/raw")
    
    # Ensure directories exist
    os.makedirs(raw_data_dir, exist_ok=True)
    
    # Sort and save
    df_sp.sort_values(["device_id", "timestamp"], inplace=True)
    df_wx.sort_values("timestamp", inplace=True)
    
    df_sp.to_csv(os.path.join(raw_data_dir, "smartplug_raw.csv"), index=False)
    df_wx.to_csv(os.path.join(raw_data_dir, "weather_raw.csv"), index=False)
    
    print(f"Successfully extracted {len(df_sp)} smartplug readings and {len(df_wx)} weather records to {raw_data_dir}")

if __name__ == "__main__":
    extract_mongo_data()
