import csv
from datetime import datetime, timezone
from dateutil import tz
from tuya_connector import TuyaOpenAPI

# ---- Fill with your project creds + device ----
ACCESS_ID = "vx4k44cpq3phqne9mtcu"
ACCESS_SECRET = "f67e664bb4a547989b1f592cf0fa3521"
DEVICE_ID = "a3c772d3fde52dbae832bi"

CSV_PATH = "tuya_energy_log.csv"

# All possible Tuya data center endpoints
ENDPOINTS = [
    "https://openapi.tuyaus.com",      # United States
    "https://openapi.tuyacn.com",      # China
    "https://openapi.tuyaeu.com",      # Central Europe
    "https://openapi.tuyain.com",      # Western Europe / India
    "https://openapi-ueaz.tuyaus.com", # Western America Azure
]

def test_endpoint(base_url: str) -> dict:
    """Test if an endpoint works with your credentials."""
    print(f"\n{'='*60}")
    print(f"Testing: {base_url}")
    print('='*60)
    
    try:
        api = TuyaOpenAPI(base_url, ACCESS_ID, ACCESS_SECRET)
        api.connect()
        print("✓ Connected successfully")
        
        # Try to get device status
        result = api.get(f"/v1.0/devices/{DEVICE_ID}/status")
        
        if result.get("success"):
            print("✓ Successfully retrieved device status!")
            print(f"Result: {result}")
            return {"success": True, "endpoint": base_url, "result": result}
        else:
            print(f"✗ API call failed: {result.get('msg')} (code: {result.get('code')})")
            return {"success": False, "endpoint": base_url, "error": result}
            
    except Exception as e:
        print(f"✗ Exception occurred: {e}")
        return {"success": False, "endpoint": base_url, "error": str(e)}

def parse_energy_status(status_result: dict) -> dict:
    dp = {}
    res = status_result.get("result")
    items = res if isinstance(res, list) else res.get("status", []) if isinstance(res, dict) else []
    
    for it in items:
        code, val = it.get("code"), it.get("value")
        if code is not None:
            dp[code] = val
    
    return {
        "voltage_v": dp.get("cur_voltage"),
        "current_a": dp.get("cur_current"),
        "power_w":   dp.get("cur_power"),
        "kwh_total": dp.get("add_ele"),
        "switch_1":  dp.get("switch_1"),
    }

def append_csv(row: dict, path: str = CSV_PATH):
    need_header = False
    try:
        open(path, "r", encoding="utf-8").close()
    except FileNotFoundError:
        need_header = True
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=row.keys())
        if need_header:
            w.writeheader()
        w.writerow(row)

def find_working_endpoint():
    """Test all endpoints and find the working one."""
    print("\n" + "="*60)
    print("TUYA API ENDPOINT DIAGNOSTIC TOOL")
    print("="*60)
    
    working_endpoints = []
    
    for endpoint in ENDPOINTS:
        result = test_endpoint(endpoint)
        if result["success"]:
            working_endpoints.append(result)
    
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    
    if working_endpoints:
        print(f"\n✓ Found {len(working_endpoints)} working endpoint(s):")
        for ep in working_endpoints:
            print(f"  → {ep['endpoint']}")
            
        # Use the first working endpoint to log data
        print("\n" + "="*60)
        print("LOGGING DATA WITH WORKING ENDPOINT")
        print("="*60)
        
        metrics = parse_energy_status(working_endpoints[0]["result"])
        local_tz = tz.gettz("Asia/Manila")
        now_local = datetime.now(timezone.utc).astimezone(local_tz)
        
        row = {
            "timestamp": now_local.isoformat(timespec="seconds"),
            "device_id": DEVICE_ID,
            "voltage_v": metrics["voltage_v"],
            "current_a": metrics["current_a"],
            "power_w":   metrics["power_w"],
            "kwh_total": metrics["kwh_total"],
            "switch_1":  metrics["switch_1"],
        }
        print("\n[OK]", row)
        append_csv(row)
        
        print(f"\n✓ Data logged to {CSV_PATH}")
        print(f"\n⚠ UPDATE YOUR SCRIPT: Use BASE_URL = \"{working_endpoints[0]['endpoint']}\"")
        
    else:
        print("\n✗ No working endpoints found!")
        print("\nPossible issues:")
        print("1. Data center not enabled in Tuya IoT Platform")
        print("2. Incorrect ACCESS_ID or ACCESS_SECRET")
        print("3. Device not linked to this project")
        print("\nTo fix:")
        print("→ Go to https://iot.tuya.com/")
        print("→ Navigate to: Cloud → Development → Your Project")
        print("→ Go to 'Authorize' or 'API' tab")
        print("→ Enable at least one data center")
        print("→ Make sure your device is added to this project")

if __name__ == "__main__":
    find_working_endpoint()