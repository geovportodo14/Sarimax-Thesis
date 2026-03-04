import os
import pymongo
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Load config
load_dotenv()
MONGO_URI = "mongodb+srv://Sarimax-Thesis:March142003!@sarimax-thesis.p6tv8ia.mongodb.net/Sarimax-Thesis?appName=Sarimax-Thesis"
DB_NAME = "Sarimax-Thesis"
MANILA_TZ = pytz.timezone("Asia/Manila")

client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["energybuckets"]

def get_profile_weights(appliance_type, start_date_str, end_date_str):
    """Calculates hourly weights (0-1) from clean data."""
    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")

    print(f"Calculating profile for {appliance_type} using {start_date_str} to {end_date_str}...")
    
    query = {"appliance_type": appliance_type}
    cursor = collection.find(query)
    
    hourly_sums = [0.0] * 24
    count = 0
    
    for doc in cursor:
        dt_val = doc.get("date")
        if isinstance(dt_val, str):
            try:
                # Handle YYYY-MM-DD or ISO strings
                if "T" in dt_val:
                   dt_val = datetime.fromisoformat(dt_val.replace("Z", "+00:00")).replace(tzinfo=None)
                else:
                   dt_val = datetime.strptime(dt_val, "%Y-%m-%d")
            except:
                continue
        
        if dt_val and start_dt <= dt_val <= end_dt:
            count += 1
            for r in doc.get("readings", []):
                ts = r.get("timestamp")
                if ts:
                    # ts is likely a datetime object if from pymongo, or string
                    if isinstance(ts, str):
                        ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=pytz.UTC)
                        
                    manila_dt = ts.astimezone(MANILA_TZ)
                    hour = manila_dt.hour
                    power = r.get("processed_data", {}).get("power_w", 0)
                    hourly_sums[hour] += power
    
    total = sum(hourly_sums)
    if total == 0:
        print(f"Warning: No energy found for {appliance_type} profile ({start_date_str} to {end_date_str}).")
        return [1.0/24.0] * 24 
    
    weights = [s / total for s in hourly_sums]
    
    # ENFORCE STRICT 8 PM - 5 AM WINDOW (Manila Time)
    # 8 PM is hour 20. 5 AM is hour 5.
    # Allowed hours: 20, 21, 22, 23, 0, 1, 2, 3, 4
    for h in range(24):
        if not (h >= 20 or h < 5):
            weights[h] = 0.0
            
    # Re-normalize if we zeroed everything out
    new_total = sum(weights)
    if new_total > 0:
        weights = [w / new_total for w in weights]
    else:
        # Fallback to even distribution in the window
        weights = [0.0] * 24
        window_hours = [20, 21, 22, 23, 0, 1, 2, 3, 4]
        for h in window_hours:
            weights[h] = 1.0 / len(window_hours)

    print(f"Profile built from {count} documents (Enforced 8PM-5AM window).")
    return weights

def redistribute_day(doc, weights):
    """Redistributes the total power of a day into the target profile."""
    readings = doc.get("readings", [])
    if not readings:
        return doc

    total_power = sum(r.get("processed_data", {}).get("power_w", 0) for r in readings)
    if total_power == 0:
        return doc

    by_hour = {}
    for r in readings:
        ts = r.get("timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=pytz.UTC)
            
        manila_ts = ts.astimezone(MANILA_TZ)
        h = manila_ts.hour
        if h not in by_hour: by_hour[h] = []
        by_hour[h].append(r)
        
    if doc.get("date") == "2026-01-10":
        print(f"DIAGNOSTIC (Jan 10): total_p={total_power:.2f}")

    for h in range(24):
        hour_readings = by_hour.get(h, [])
        w = weights[h]
        hour_total_power = total_power * w
        avg_p = hour_total_power / len(hour_readings) if len(hour_readings) > 0 else 0
        
        if doc.get("date") == "2026-01-10" and w > 0:
            print(f"  Hour {h}: w={w:.4f}, readings={len(hour_readings)}, avg_p={avg_p:.4f}")

        for r in hour_readings:
            if "processed_data" not in r: r["processed_data"] = {}
            r["processed_data"]["power_w"] = round(avg_p, 4)
            
    return doc

def run_redistribution(appliance_type, profile_weights, start_date_str, end_date_str):
    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
    
    print(f"\nProcessing {appliance_type} from {start_date_str} to {end_date_str}...")
    print(f"Profile Weights (Hours 0-23): {[f'{w:.4f}' for w in profile_weights]}")
    query = {"appliance_type": appliance_type}
    cursor = collection.find(query)
    
    updates = 0
    for doc in cursor:
        dt_val = doc.get("date")
        if isinstance(dt_val, str):
            try:
                if "T" in dt_val:
                   dt_val = datetime.fromisoformat(dt_val.replace("Z", "+00:00")).replace(tzinfo=None)
                else:
                   dt_val = datetime.strptime(dt_val, "%Y-%m-%d")
            except:
                continue
        
        if dt_val and start_dt <= dt_val <= end_dt:
            original_id = doc["_id"]
            updated_doc = redistribute_day(doc, profile_weights)
            collection.replace_one({"_id": original_id}, updated_doc)
            updates += 1
        
    print(f"Successfully updated {updates} daily documents for {appliance_type}.")

if __name__ == "__main__":
    target_appliances = ["aircon", "electricfan"]
    profile_range = ("2026-03-01", "2026-03-04")
    target_range = ("2026-01-03", "2026-02-17")
    
    for app in target_appliances:
        weights = get_profile_weights(app, profile_range[0], profile_range[1])
        run_redistribution(app, weights, target_range[0], target_range[1])

    print("\nRedistribution complete.")
    client.close()
