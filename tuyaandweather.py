import csv
import time
from datetime import datetime, timezone
from dateutil import tz
from tuya_connector import TuyaOpenAPI

# ====== PROJECT CREDENTIALS (update per household if needed) ======
ACCESS_ID = "vx4k44cpq3phqne9mtcu"
ACCESS_SECRET = "f67e664bb4a547989b1f592cf0fa3521"
DEVICE_ID = "a3c772d3fde52dbae832bi"
BASE_URL = "https://openapi-sg.iotbing.com"  # Singapore Data Center
CSV_PATH = "tuya_energy_log.csv"
MANILA_TZ = tz.gettz("Asia/Manila")

# ------------------------------------------------------------------
def fetch_dp_scales(api):
    """Get scaling factors for each DP code"""
    try:
        r = api.get(f"/v1.0/iot-03/devices/{DEVICE_ID}/functions")
        if not r.get("success"):
            # Fallback scales if API call fails
            return {'cur_voltage':0.1,'cur_current':0.001,'cur_power':0.1,'add_ele':0.01}
        scales = {}
        for f in r["result"]["functions"]:
            scales[f["code"]] = 10 ** (-f.get("scale", 0))
        return scales
    except Exception:
        # Fallback scales on connection error
        return {'cur_voltage':0.1,'cur_current':0.001,'cur_power':0.1,'add_ele':0.01}

def parse_status(result):
    """Parses the status response into a simple code:value dictionary."""
    res = result.get("result")
    items = res.get("status", []) if isinstance(res, dict) else (res or [])
    return {it.get("code"): it.get("value") for it in items if it.get("code")}

def normalize_values(dp, scale):
    """Applies scaling factors to raw Tuya values."""
    return {
        "voltage_v": dp.get("cur_voltage", 0) * scale.get("cur_voltage", 1),
        "current_a": dp.get("cur_current", 0) * scale.get("cur_current", 1),
        "power_w":   dp.get("cur_power", 0)   * scale.get("cur_power", 1),
        "kwh_total": dp.get("add_ele", 0)     * scale.get("add_ele", 1),
        "switch_1":  dp.get("switch_1", False)
    }

def append_csv(row):
    """Appends a row of Tuya data to the CSV, creating the file and header if necessary."""
    header_needed = False
    try:
        # Check if file exists and has content (to decide if header is needed)
        open(CSV_PATH, "r", encoding="utf-8").close()
    except FileNotFoundError:
        header_needed = True
    
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if header_needed:
            writer.writeheader()
        writer.writerow(row)

def log_once(api, scale):
    """Fetches and logs the Tuya energy data."""
    result = api.get(f"/v1.0/iot-03/devices/{DEVICE_ID}/status")
    
    # Check for *any* API error before proceeding
    if not result.get("success"):
        # This will be caught by the outer loop and trigger a reconnect if 1010
        print("⚠️  API error:", result)
        # Raise an exception to break the flow and signal the need for a token refresh
        if result.get('code') == 1010:
            raise ConnectionRefusedError("Token Invalid (Code 1010)")
        return
        
    dp = parse_status(result)
    metrics = normalize_values(dp, scale)
    now_local = datetime.now(timezone.utc).astimezone(MANILA_TZ)
    
    row = {
        "timestamp": now_local.isoformat(timespec="seconds"),
        "device_id": DEVICE_ID,
        "voltage_v": metrics["voltage_v"],
        "current_a": metrics["current_a"],
        "power_w": metrics["power_w"],
        "kwh_total": metrics["kwh_total"],
        "switch_1": metrics["switch_1"]
    }
    print("[OK]", row)
    append_csv(row)

def main():
    api = TuyaOpenAPI(BASE_URL, ACCESS_ID, ACCESS_SECRET)
    
    # Initial connection
    print("Attempting initial connection...")
    api.connect()
    
    # Initial scale fetch (requires a valid token)
    scale = fetch_dp_scales(api)
    
    print("✅ Logging every 10 minutes. Press Ctrl+C to stop.")
    
    try:
        while True:
            try:
                # 1. Attempt to log data
                log_once(api, scale)
            
            except ConnectionRefusedError as e:
                # 2. Handle specific "Token Invalid" error
                print(f"🔴 Error: {e}. Attempting to reconnect and refresh token...")
                api.connect() # Reconnect to get a new token
                # Re-fetch scale after reconnect (optional, but safe)
                scale = fetch_dp_scales(api)
                # Continue the loop to log data in the next iteration
                
            except Exception as e:
                # 3. Handle any other unexpected errors
                print(f"❌ An unexpected error occurred: {e}. Will retry in 10 minutes.")

            # 4. Wait for the next interval (10 minutes)
            time.sleep(600)
            
    except KeyboardInterrupt:
        print("\n🟢 Logging stopped by user. Data safely saved to CSV.")

if __name__ == "__main__":
    main()