import time, hmac, hashlib, requests, json, sys
from datetime import datetime

ACCESS_ID     = "vx4k44cpq3phqne9mtcu"
ACCESS_SECRET = "f67e664bb4a547989b1f592cf0fa3521"
DEVICE_ID     = "a3c772d3fde52dbae832bi"   # e.g. a3c772d3fde52dbae832bi
BASE_URL = "https://openapi-sg.iotbing.com"

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def millis() -> str:
    return str(int(time.time() * 1000))

def sign_msg(msg: str, key: str) -> str:
    return hmac.new(key.encode("utf-8"), msg=msg.encode("utf-8"), digestmod=hashlib.sha256).hexdigest().upper()

def headers(client_id: str, t: str, sign: str, access_token: str | None = None):
    h = {
        "client_id": client_id,
        "t": t,
        "sign": sign,
        "sign_method": "HMAC-SHA256",
        "Content-Type": "application/json"
    }
    if access_token:
        h["access_token"] = access_token
    return h

def get_token():
    url = f"{BASE_URL}/v1.0/token?grant_type=1"
    t = millis()
    sig = sign_msg(ACCESS_ID + t, ACCESS_SECRET)
    print(f"[{now()}] STEP 1: Request token…")
    try:
        r = requests.get(url, headers=headers(ACCESS_ID, t, sig), timeout=20)
        print(f"[HTTP {r.status_code}] {r.text[:200]}")
        r.raise_for_status()
        res = r.json()
        if not res.get("success"):
            print("[ERROR] Token response success=false:", res)
            sys.exit(1)
        return res["result"]["access_token"]
    except Exception as e:
        print("[EXCEPTION getting token]", e)
        sys.exit(1)

def get_status(access_token: str):
    url = f"{BASE_URL}/v1.0/devices/{DEVICE_ID}/status"
    t = millis()
    sig = sign_msg(ACCESS_ID + access_token + t, ACCESS_SECRET)
    print(f"\n[{now()}] STEP 2: Get device status for {DEVICE_ID}…")
    try:
        r = requests.get(url, headers=headers(ACCESS_ID, t, sig, access_token), timeout=20)
        print(f"[HTTP {r.status_code}] {r.text[:400]}")
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("[EXCEPTION getting status]", e)
        sys.exit(1)

def main():
    if "YOUR_ACCESS_ID" in ACCESS_ID or "YOUR_DEVICE_ID" in DEVICE_ID:
        print("⚠️  Please edit ACCESS_ID / ACCESS_SECRET / DEVICE_ID at the top of this file.")
        sys.exit(1)

    token = get_token()
    print(f"[{now()}] ✓ Got access_token:", token[:12], "…")
    status = get_status(token)

    # Try to parse common DPs
    items = status.get("result") or {}
    if isinstance(items, dict):
        items = items.get("status", [])
    dp = {it.get("code"): it.get("value") for it in items}

    print("\n---- Parsed values (if present) ----")
    for k in ("cur_voltage","cur_current","cur_power","add_ele","switch_1"):
        print(f"{k:>12}: {dp.get(k)}")
    print("------------------------------------")

if __name__ == "__main__":
    main()
