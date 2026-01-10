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
ACCESS_ID = "trfs5ycjmhh4cs9sehnr"  # Replace with your full ACCESS_ID
ACCESS_SECRET = "367f3cd4abf8457a8116de9b2ed28f70"  # Replace with your full SECRET
ENDPOINT = "https://openapi-sg.iotbing.com"


# ==================================================
# CONFIGURATION
# ==================================================
DEVICES = {
    "Aircon": "a3ed2fe218a724b4fepeni",
    "Refrigerator": "a3986d20c19f33c7c107fw",
    "Electric_Fan": "a3c772d3fde52dbae832bi"
}

# Logging settings
LOG_INTERVAL = 600  # Log every 5 minutes (300 seconds)
CSV_FOLDER = "energy_data"  # Folder to store CSV files
CSV_FILE = os.path.join(CSV_FOLDER, f"energy_log_{datetime.now().strftime('%Y%m%d')}.csv")


# ==================================================
# Setup CSV folder
# ==================================================
if not os.path.exists(CSV_FOLDER):
    os.makedirs(CSV_FOLDER)
    print(f"✅ Created folder: {CSV_FOLDER}\n")


# ==================================================
# Generate HMAC-SHA256 signature
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


# ==================================================
# Get access token
# ==================================================
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
        response = requests.get(f"{ENDPOINT}{path}", headers=headers, timeout=10)
        data = response.json()
        
        if data.get("success"):
            return data["result"]["access_token"]
        else:
            print(f"❌ Token error: {data.get('msg', 'Unknown')}")
            return None
    except Exception as e:
        print(f"❌ Token request failed: {e}")
        return None


# ==================================================
# Get device status
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
        response = requests.get(f"{ENDPOINT}{path}", headers=headers, timeout=10)
        data = response.json()
        
        if data.get("success") and data.get("result"):
            # Convert list of {code, value} to dictionary
            status_dict = {item['code']: item['value'] for item in data['result']}
            return status_dict
        else:
            return None
    except Exception as e:
        print(f"❌ Error fetching device {device_id}: {e}")
        return None


# ==================================================
# Write data to CSV
# ==================================================
def log_to_csv(timestamp, device_name, status_data):
    file_exists = os.path.isfile(CSV_FILE)
    
    try:
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header if file is new
            if not file_exists:
                writer.writerow(['timestamp', 'device', 'property', 'value'])
            
            # Write each property as a separate row
            if status_data:
                for key, value in status_data.items():
                    writer.writerow([timestamp, device_name, key, value])
                return True
            else:
                writer.writerow([timestamp, device_name, 'ERROR', 'No data'])
                return False
                
    except Exception as e:
        print(f"❌ CSV write error: {e}")
        return False


# ==================================================
# Main logging loop
# ==================================================
def start_logging():
    print("=" * 60)
    print("🔌 TUYA ENERGY DATA LOGGER")
    print("=" * 60)
    print(f"📁 Saving to: {CSV_FILE}")
    print(f"⏱️  Log interval: {LOG_INTERVAL} seconds ({LOG_INTERVAL//60} minutes)")
    print(f"📊 Devices: {', '.join(DEVICES.keys())}")
    print("=" * 60)
    print("Press Ctrl+C to stop\n")
    
    token = None
    token_expiry = 0
    log_count = 0
    
    try:
        while True:
            # Refresh token every hour (tokens expire after 2 hours)
            current_time = time.time()
            if token is None or current_time > token_expiry:
                print("🔄 Refreshing access token...")
                token = get_token()
                if token:
                    token_expiry = current_time + 3600  # Valid for 1 hour
                    print("✅ Token refreshed\n")
                else:
                    print("⚠️  Failed to get token. Retrying in 60 seconds...")
                    time.sleep(60)
                    continue
            
            # Get current timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"[{timestamp}] Logging data...")
            
            # Fetch and log data for each device
            success_count = 0
            for device_name, device_id in DEVICES.items():
                status = get_device_status(token, device_id)
                
                if status:
                    if log_to_csv(timestamp, device_name, status):
                        success_count += 1
                        print(f"  ✅ {device_name}: {len(status)} properties logged")
                    else:
                        print(f"  ⚠️  {device_name}: Failed to write to CSV")
                else:
                    log_to_csv(timestamp, device_name, None)
                    print(f"  ❌ {device_name}: No data (subscription may be expired)")
                
                time.sleep(0.5)  # Small delay between devices
            
            log_count += 1
            print(f"📝 Log entry #{log_count} complete ({success_count}/{len(DEVICES)} devices)\n")
            
            # Wait for next interval
            time.sleep(LOG_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print(f"🛑 Logging stopped by user")
        print(f"📊 Total log entries: {log_count}")
        print(f"📁 Data saved to: {CSV_FILE}")
        print("=" * 60)


# ==================================================
# Run logger
# ==================================================
if __name__ == "__main__":
    start_logging()
