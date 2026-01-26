import requests
import hashlib
import hmac
import time
import csv
from datetime import datetime
import os

# ==================================================
# 🔑 CREDENTIALS
# ==================================================
ACCESS_ID = "nrf89gjrxe3wrqjnr5tc"
ACCESS_SECRET = "d170c9dd96204a4cbf79d7bece7a37cb"
ENDPOINT = "https://openapi-sg.iotbing.com"

OPENWEATHER_API_KEY = "12a933cfc49aae1d814dd6407120d524"
OPENWEATHER_CITY = "Manila"
# ==================================================
# CONFIGURATION
# ==================================================
DEVICES = {
    "Aircon": "a3ed2fe218a724b4fepeni",
    "Refrigerator": "a3986d20c19f33c7c107fw",
    "Electric_Fan": "a3c772d3fde52dbae832bi"
}

LOG_INTERVAL = 600  # 10 minutes
CSV_FOLDER = "energy_data"
CSV_FILE = os.path.join(CSV_FOLDER, f"energy_log_{datetime.now().strftime('%Y%m%d')}.csv")

# ==================================================
# FOLDER + CSV HEADER
# ==================================================
if not os.path.exists(CSV_FOLDER):
    os.makedirs(CSV_FOLDER)

if not os.path.isfile(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "timestamp",
            "device",
            "property",
            "value",
            "temp_C",
            "humidity",
            "pressure"
        ])

# ==================================================
# TUYA SIGNING + TOKEN
# ==================================================
def generate_sign(method, path, token=""):
    t = str(int(time.time() * 1000))
    content_hash = hashlib.sha256(b"").hexdigest()
    string_to_sign = f"{method}\n{content_hash}\n\n{path}"
    sign_str = ACCESS_ID + token + t + string_to_sign
    sign = hmac.new(
        ACCESS_SECRET.encode("utf-8"),
        sign_str.encode("utf-8"),
        hashlib.sha256
    ).hexdigest().upper()
    return sign, t

def get_token():
    path = "/v1.0/token?grant_type=1"
    sign, t = generate_sign("GET", path)
    headers = {
        "client_id": ACCESS_ID,
        "sign": sign,
        "t": t,
        "sign_method": "HMAC-SHA256"
    }
    try:
        r = requests.get(f"{ENDPOINT}{path}", headers=headers, timeout=10)
        data = r.json()
        print("TOKEN DEBUG:", data)
        if data.get("success"):
            return data["result"]["access_token"]
        print("Token error:", data.get("msg", "unknown"), data.get("code"))
        return None
    except Exception as e:
        print("Token request failed:", e)
        return None

# ==================================================
# TUYA DEVICE STATUS - WITH DEBUG PRINTS
# ==================================================
def get_device_status(token, device_id):
    path = f"/v1.0/devices/{device_id}/status"
    sign, t = generate_sign("GET", path, token)
    headers = {
        "client_id": ACCESS_ID,
        "access_token": token,
        "sign": sign,
        "t": t,
        "sign_method": "HMAC-SHA256"
    }
    try:
        r = requests.get(f"{ENDPOINT}{path}", headers=headers, timeout=10)
        data = r.json()
        
        # 🔍 DEBUG: Print full Tuya response
        print(f"\nTUYA DEBUG for {device_id}:")
        print(data)
        
        if data.get("success") and data.get("result"):
            return {it["code"]: it["value"] for it in data["result"]}
        
        # Also log error details
        print(f"Device status not OK - success: {data.get('success')}, code: {data.get('code')}, msg: {data.get('msg')}")
        return None
    except Exception as e:
        print("Device request failed:", e)
        return None

# ==================================================
# OPENWEATHER CURRENT WEATHER
# ==================================================
def get_weather():
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={OPENWEATHER_CITY}&appid={OPENWEATHER_API_KEY}&units=metric"
    )
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        print("WEATHER DEBUG:", data)
        
        if r.status_code != 200:
            return {"temp": None, "humidity": None, "pressure": None}
        
        main = data.get("main", {})
        return {
            "temp": main.get("temp"),
            "humidity": main.get("humidity"),
            "pressure": main.get("pressure"),
        }
    except Exception as e:
        print("Weather request failed:", e)
        return {"temp": None, "humidity": None, "pressure": None}

# ==================================================
# CSV LOGGING
# ==================================================
def log_row(timestamp, device, prop, value, weather):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            timestamp,
            device,
            prop,
            value,
            weather.get("temp"),
            weather.get("humidity"),
            weather.get("pressure")
        ])

# ==================================================
# MAIN LOOP
# ==================================================
def start_logging():
    print("TUYA + OPENWEATHER LOGGER (10‑minute interval)")
    token = None
    token_expiry = 0
    entry = 0
    
    try:
        while True:
            now = time.time()
            if token is None or now > token_expiry:
                print("Refreshing Tuya token...")
                token = get_token()
                if not token:
                    print("No token, retry in 60s.")
                    time.sleep(60)
                    continue
                token_expiry = now + 3600
            
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{ts}] Logging...")
            
            weather = get_weather()
            print("  Weather:", weather)
            
            for name, dev_id in DEVICES.items():
                status = get_device_status(token, dev_id)
                if status:
                    for code, val in status.items():
                        log_row(ts, name, code, val, weather)
                    print(f"  {name}: {len(status)} points logged.")
                else:
                    log_row(ts, name, "NO_DATA", None, weather)
                    print(f"  {name}: NO_DATA (offline / no permission).")
                
                time.sleep(0.5)
            
            entry += 1
            print(f"Entry #{entry} complete. Sleeping 10 minutes...\n")
            time.sleep(LOG_INTERVAL)
    
    except KeyboardInterrupt:
        print("\nStopped by user. Data stored in:", CSV_FILE)

if __name__ == "__main__":
    start_logging()
