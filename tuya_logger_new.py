import csv
import time
from datetime import datetime, timezone
from dateutil import tz
from tuya_connector import TuyaOpenAPI

# ====== PROJECT CREDENTIALS (keep private) ======
ACCESS_ID = "pxxc44xdm4snmjhs84sp"
ACCESS_SECRET = "2421aea5a6c04dba9b4deaa7e6a60285"
DEVICE_ID = "a3c772d3fde52dbae832bi"
BASE_URL = "https://openapi-sg.iotbing.com"
CSV_PATH = "tuya_energy_log2.csv"

# ====== SCALING DEFAULTS (verified with PF ≈ 0.9–1.0) ======
SCALE_DEFAULT = {
    "cur_voltage": 0.1,
    "cur_current": 0.01,
    "cur_power": 0.1,
    "add_ele": 0.01
}

# ----------------------------------------------------------
def fetch_dp_scales(api):
    """Fetch scaling factors or fallback to defaults."""
    try:
        r = api.get(f"/v1.0/iot-03/devices/{DEVICE_ID}/functions")
        if not r.get("success"):
            print("⚠️ Using default scaling factors.")
            return SCALE_DEFAULT
        scales = {}
        for f in r["result"]["functions"]:
            code = f.get("code")
            scale = f.get("scale", 0)
            scales[code] = 10 ** (-scale)
        print("✅ Scaling factors:", scales)
        return {**SCALE_DEFAULT, **scales}
    except Exception as e:
        print("⚠️ Scaling fetch failed:", e)
        return SCALE_DEFAULT

def parse_status(result):
    res = result.get("result")
    items = res.get("status", []) if isinstance(res, dict) else (res or [])
    return {it.get("code"): it.get("value") for it in items if it.get("code")}

def normalize_values(dp, scale):
    """Apply scaling and return both raw and scaled readings."""
    voltage_raw = dp.get("cur_voltage", 0)
    current_raw = dp.get("cur_current", 0)
    power_raw = dp.get("cur_power", 0)
    add_ele_raw = dp.get("add_ele", 0)

    voltage_v = voltage_raw * scale.get("cur_voltage", 1)
    current_a = current_raw * scale.get("cur_current", 1)
    power_w = power_raw * scale.get("cur_power", 1)
    kwh_total = add_ele_raw * scale.get("add_ele", 1)

    return {
        # Raw readings
        "voltage_raw": voltage_raw,
        "current_raw": current_raw,
        "power_raw": power_raw,
        "add_ele_raw": add_ele_raw,
        # Scaled values
        "voltage_v": voltage_v,
        "current_a": current_a,
        "power_w": power_w,
        "kwh_total": kwh_total,
        "switch_1": dp.get("switch_1", False)
    }

def append_csv(row):
    """Safe CSV append with header check."""
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

# Track previous cumulative energy and timestamp
last_kwh_total = None
last_timestamp = None

def log_once(api, scale):
    global last_kwh_total, last_timestamp

    result = api.get(f"/v1.0/iot-03/devices/{DEVICE_ID}/status")
    if not result.get("success"):
        print("⚠️ API error:", result)
        return

    dp = parse_status(result)
    m = normalize_values(dp, scale)
    now_local = datetime.now(timezone.utc).astimezone(tz.gettz("Asia/Manila"))

    # --- Compute time interval ---
    interval_seconds = None
    if last_timestamp:
        interval_seconds = (now_local - last_timestamp).total_seconds()
    last_timestamp = now_local

    # --- Compute interval energy ---
    kwh_interval_kwh = None
    energy_fallback_kwh = None
    energy_final_kwh = None

    if last_kwh_total is not None:
        delta = m["kwh_total"] - last_kwh_total
        if delta < 0:  # handle device reset
            print("⚠️ kWh reset detected.")
            delta = 0
        kwh_interval_kwh = delta

        if interval_seconds:
            energy_fallback_kwh = (m["power_w"] * (interval_seconds / 3600)) / 1000
        else:
            energy_fallback_kwh = 0

        # Hybrid rule
        energy_final_kwh = delta if delta > 0 else energy_fallback_kwh

    last_kwh_total = m["kwh_total"]

    # --- Estimate Power Factor ---
    try:
        pf_est = m["power_w"] / (m["voltage_v"] * m["current_a"]) if m["voltage_v"] and m["current_a"] else 0
        pf_est = max(0, min(pf_est, 1))
    except ZeroDivisionError:
        pf_est = 0

    # --- Prepare row ---
    row = {
        "timestamp": now_local.isoformat(timespec="seconds"),
        "device_id": DEVICE_ID,
        "switch_1": m["switch_1"],
        # Raw
        "voltage_raw": m["voltage_raw"],
        "current_raw": m["current_raw"],
        "power_raw": m["power_raw"],
        "add_ele_raw": m["add_ele_raw"],
        # Scaled
        "voltage_v": m["voltage_v"],
        "current_a": m["current_a"],
        "power_w": m["power_w"],
        "kwh_total": m["kwh_total"],
        # Interval metrics
        "interval_seconds": interval_seconds,
        "kwh_interval_kwh": kwh_interval_kwh,
        "energy_fallback_kwh": energy_fallback_kwh,
        "energy_final_kwh": energy_final_kwh,
        # Diagnostics
        "pf_est": pf_est
    }

    print("[OK]", row)
    append_csv(row)

def main():
    api = TuyaOpenAPI(BASE_URL, ACCESS_ID, ACCESS_SECRET)
    api.connect()
    scale = fetch_dp_scales(api)
    print("✅ Logging every 10 minutes. Press Ctrl+C to stop.\n")

    try:
        while True:
            log_once(api, scale)
            time.sleep(600)  # 10 minutes = 600 seconds
    except KeyboardInterrupt:
        print("\n🟢 Logging stopped by user. Data safely saved to CSV.")

if __name__ == "__main__":
    main()
