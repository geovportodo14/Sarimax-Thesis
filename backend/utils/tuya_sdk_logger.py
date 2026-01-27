import csv
import time
from datetime import datetime, timezone
from dateutil import tz
from tuya_connector import TuyaOpenAPI

# ====== PROJECT CREDENTIALS (update per household if needed) ======
ACCESS_ID = "pxxc44xdm4snmjhs84sp"
ACCESS_SECRET = "2421aea5a6c04dba9b4deaa7e6a60285"
DEVICE_ID = "sg1759585107699T8GaO"
BASE_URL = "https://openapi-sg.iotbing.com"   # Singapore Data Center
CSV_PATH = "tuya_energy_log.csv"

# ------------------------------------------------------------------
def fetch_dp_scales(api):
    """Get scaling factors for each DP code"""
    try:
        r = api.get(f"/v1.0/iot-03/devices/{DEVICE_ID}/functions")
        if not r.get("success"):
            return {'cur_voltage':0.1,'cur_current':0.001,'cur_power':0.1,'add_ele':0.01}
        scales = {}
        for f in r["result"]["functions"]:
            scales[f["code"]] = 10 ** (-f.get("scale", 0))
        return scales
    except Exception:
        return {'cur_voltage':0.1,'cur_current':0.001,'cur_power':0.1,'add_ele':0.01}

def parse_status(result):
    res = result.get("result")
    items = res.get("status", []) if isinstance(res, dict) else (res or [])
    return {it.get("code"): it.get("value") for it in items if it.get("code")}

def normalize_values(dp, scale):
    return {
        "voltage_v": dp.get("cur_voltage", 0) * scale.get("cur_voltage", 1),
        "current_a": dp.get("cur_current", 0) * scale.get("cur_current", 1),
        "power_w":   dp.get("cur_power", 0)   * scale.get("cur_power", 1),
        "kwh_total": dp.get("add_ele", 0)     * scale.get("add_ele", 1),
        "switch_1":  dp.get("switch_1", False)
    }

def append_csv(row):
    header_needed = False
    try:
        open(CSV_PATH, "r", encoding="utf-8").close()
    except FileNotFoundError:
        header_needed = True
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if header_needed:
            writer.writeheader()
        writer.writerow(row)

def log_once(api, scale):
    result = api.get(f"/v1.0/iot-03/devices/{DEVICE_ID}/status")
    if not result.get("success"):
        print("⚠️  API error:", result)
        return
    dp = parse_status(result)
    metrics = normalize_values(dp, scale)
    now_local = datetime.now(timezone.utc).astimezone(tz.gettz("Asia/Manila"))
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
    api.connect()
    scale = fetch_dp_scales(api)
    print("✅ Logging every 10 minutes. Press Ctrl+C to stop.")
    try:
        while True:
            log_once(api, scale)
            time.sleep(600)   # 10 minutes = 600 seconds
    except KeyboardInterrupt:
        print("\n🟢 Logging stopped by user. Data safely saved to CSV.")

if __name__ == "__main__":
    main()
