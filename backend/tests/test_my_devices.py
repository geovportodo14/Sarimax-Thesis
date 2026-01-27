import requests
import hashlib
import hmac
import time


# ==================================================
# 🔑 PUT YOUR CREDENTIALS HERE
# ==================================================
ACCESS_ID = "trfs5ycjmhh4cs9sehnr"  # Replace with your full ACCESS_ID
ACCESS_SECRET = "367f3cd4abf8457a8116de9b2ed28f70"  # Replace with your full SECRET
ENDPOINT = "https://openapi-sg.iotbing.com"  # Singapore endpoint


# ==================================================
# Safety check
# ==================================================
if "your_actual" in ACCESS_ID or "your_actual" in ACCESS_SECRET:
    print("=" * 60)
    print("❌ ERROR: Replace the placeholder credentials above!")
    print("=" * 60)
    print("\n💡 Edit lines 8-10 in this script with your real:")
    print("   - TUYA_ACCESS_ID")
    print("   - TUYA_ACCESS_SECRET")
    print("   - TUYA_ENDPOINT")
    print("\nGet them from: https://iot.tuya.com/")
    print("=" * 60)
  

print("✅ Credentials found")
print(f"   ACCESS_ID: {ACCESS_ID[:10]}...")
print(f"   ENDPOINT: {ENDPOINT}\n")


# ==================================================
# Your devices
# ==================================================
DEVICES = {
    "Aircon": "a3ed2fe218a724b4fepeni",
    "Refrigerator": "a3986d20c19f33c7c107fw",
    "Electric_Fan": "a3c772d3fde52dbae832bi"
}


# ==================================================
# Generate HMAC-SHA256 signature
# ==================================================
def generate_sign(method, path, token=""):
    """Generate HMAC-SHA256 signature for Tuya API request"""
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


# ==================================================
# Get access token
# ==================================================
def get_token():
    """Retrieve access token from Tuya API"""
    path = "/v1.0/token?grant_type=1"
    sign, t = generate_sign("GET", path)

    headers = {
        "client_id": ACCESS_ID,
        "sign": sign,
        "t": t,
        "sign_method": "HMAC-SHA256"
    }

    try:
        response = requests.get(f"{ENDPOINT}{path}", headers=headers, timeout=10)
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error during token request: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error during token request: {e}")
        return None

    if data.get("success"):
        print("✅ Token acquired successfully\n")
        return data["result"]["access_token"]

    print(f"❌ Token request failed: {data.get('msg', 'Unknown error')}")
    print(f"   Code: {data.get('code', 'N/A')}")
    print(f"   Response: {data}")
    return None


# ==================================================
# Get device status
# ==================================================
def get_device_status(token, device_id, device_name):
    """Fetch and display real-time status of a Tuya device"""
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
        response = requests.get(f"{ENDPOINT}{path}", headers=headers, timeout=10)
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error fetching {device_name}: {e}\n")
        return
    except Exception as e:
        print(f"❌ Unexpected error fetching {device_name}: {e}\n")
        return

    print("=" * 60)
    print(f"⚡ {device_name.upper()}")
    print("=" * 60)

    if not data.get("success"):
        print(f"❌ Failed: {data.get('msg', 'Unknown error')}")
        print(f"   Code: {data.get('code', 'N/A')}")
        
        # Helpful error messages
        if data.get('code') == 28841002:
            print("   💡 Your IoT Core subscription expired or is being reviewed")
            print("   Go to: https://iot.tuya.com/cloud/basic to extend it")
        elif data.get('code') == 1114:
            print("   💡 Your IP is blocked. Disable IP whitelist in Cloud Project settings")
        print()
        return

    if not data.get("result"):
        print("⚠️  No status data available for this device\n")
        return

    # Display all device properties
    for item in data["result"]:
        code = item.get('code', 'unknown')
        value = item.get('value', 'N/A')
        print(f"  {code:25s}: {value}")
    print()


# ==================================================
# Main execution
# ==================================================
if __name__ == "__main__":
    print("\n🔌 Testing Tuya Devices (Singapore Data Center)\n")
    print("=" * 60)

    # Get authentication token
    token = get_token()
    if not token:
        print("\n❌ Cannot proceed without access token")
        print("💡 Troubleshooting:")
        print("   1. Check your credentials are correct")
        print("   2. Verify IP whitelist is disabled")
        print("   3. Ensure IoT Core subscription is active")
        print("   Visit: https://iot.tuya.com/")
        exit(1)

    print("📡 Fetching real-time device data...\n")

    # Fetch status for each device
    for name, device_id in DEVICES.items():
        get_device_status(token, device_id, name)
        time.sleep(1)  # Rate limiting - wait 1 second between requests

    print("=" * 60)
    print("✅ Test complete — All devices checked!")
    print("=" * 60)
