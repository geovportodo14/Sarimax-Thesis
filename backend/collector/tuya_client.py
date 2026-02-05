import requests
import hashlib
import hmac
import time
import logging

logger = logging.getLogger(__name__)

class TuyaClient:
    def __init__(self, access_id, access_secret, endpoint):
        self.access_id = access_id
        self.access_secret = access_secret
        self.endpoint = endpoint
        self.token = None
        self.token_expiry = 0

    def _generate_sign(self, method, path, token=""):
        t = str(int(time.time() * 1000))
        content_hash = hashlib.sha256(b"").hexdigest()
        string_to_sign = f"{method}\n{content_hash}\n\n{path}"
        sign_str = self.access_id + token + t + string_to_sign
        sign = hmac.new(
            self.access_secret.encode("utf-8"),
            sign_str.encode("utf-8"),
            hashlib.sha256
        ).hexdigest().upper()
        return sign, t

    def get_token(self):
        now = time.time()
        if self.token and now < self.token_expiry:
            return self.token

        path = "/v1.0/token?grant_type=1"
        sign, t = self._generate_sign("GET", path)
        headers = {
            "client_id": self.access_id,
            "sign": sign,
            "t": t,
            "sign_method": "HMAC-SHA256"
        }
        try:
            r = requests.get(f"{self.endpoint}{path}", headers=headers, timeout=10)
            data = r.json()
            if data.get("success"):
                self.token = data["result"]["access_token"]
                self.token_expiry = now + data["result"]["expire_time"] - 60  # Buffer
                return self.token
            logger.error(f"Token error: {data.get('msg', 'unknown')} (code: {data.get('code')})")
            return None
        except Exception as e:
            logger.exception("Token request failed")
            return None

    def get_device_status(self, device_id):
        token = self.get_token()
        if not token:
            return None

        path = f"/v1.0/devices/{device_id}/status"
        sign, t = self._generate_sign("GET", path, token)
        headers = {
            "client_id": self.access_id,
            "access_token": token,
            "sign": sign,
            "t": t,
            "sign_method": "HMAC-SHA256"
        }
        try:
            r = requests.get(f"{self.endpoint}{path}", headers=headers, timeout=10)
            data = r.json()
            if data.get("success") and data.get("result"):
                return {it["code"]: it["value"] for it in data["result"]}
            logger.warning(f"Device status failure for {device_id}: {data.get('msg')}")
            return None
        except Exception as e:
            logger.exception(f"Request failed for device {device_id}")
            return None
    def get_historical_logs(self, device_id, start_time, end_time, codes=None):
        """
        Fetches historical data point reports (type=7) from Tuya with pagination.
        start_time and end_time should be 13-digit Unix timestamps.
        """
        all_logs = []
        has_next = True
        last_row_key = ""

        while has_next:
            token = self.get_token()
            if not token:
                break

            path = f"/v1.0/devices/{device_id}/logs"
            query_params = {
                "type": "7",
                "start_time": start_time,
                "end_time": end_time,
                "size": 100
            }
            if codes:
                query_params["codes"] = codes
            if last_row_key:
                query_params["start_row_key"] = last_row_key

            # Build query string for signing
            query_str = "&".join([f"{k}={v}" for k, v in sorted(query_params.items())])
            full_path = f"{path}?{query_str}"

            sign, t = self._generate_sign("GET", full_path, token)

            headers = {
                "client_id": self.access_id,
                "access_token": token,
                "sign": sign,
                "t": t,
                "sign_method": "HMAC-SHA256"
            }
            
            try:
                r = requests.get(f"{self.endpoint}{full_path}", headers=headers, timeout=15)
                data = r.json()
                if data.get("success"):
                    result = data.get("result", {})
                    logs = result.get("logs", [])
                    all_logs.extend(logs)
                    
                    has_next = result.get("has_next", False)
                    last_row_key = result.get("next_row_key", "")
                    
                    if not has_next or not last_row_key:
                        break
                    
                    time.sleep(0.1) # Small delay to be polite to the API
                else:
                    logger.warning(f"Historical logs failure for {device_id}: {data.get('msg')}")
                    break
            except Exception as e:
                logger.exception(f"Request failed for historical logs {device_id}")
                break
        
        return all_logs if all_logs else None
