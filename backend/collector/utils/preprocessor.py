import logging

logger = logging.getLogger(__name__)

class DataPreprocessor:
    def __init__(self):
        pass

    def normalize(self, appliance_name, raw_data):
        """
        Converts raw Tuya values (centivolts, milliamps, etc.) into standard units.
        Schema:
        - voltage: V (from centivolts)
        - current: A (from milliamps)
        - power: W (usually reported in Watts or deciwatts)
        - total_kwh: kWh
        """
        if not raw_data:
            return None

        # Power (usually code 'cur_power' or 'power')
        # Tuya usually reports in deciwatts (e.g. 150 = 15.0W)
        p_raw = raw_data.get("cur_power")
        if p_raw is None:
            p_raw = raw_data.get("power")
        power_w = float(p_raw) / 10.0 if p_raw is not None else 0.0

        normalized = {
            "is_active": (raw_data.get("switch_1") == True or 
                          raw_data.get("switch") == True or 
                          power_w > 1.0)
        }
        normalized["power_w"] = power_w

        # Voltage (usually code 'cur_voltage' or 'voltage')
        # Tuya usually reports in centivolts (e.g. 2301 = 230.1V)
        v_raw = raw_data.get("cur_voltage")
        if v_raw is None:
            v_raw = raw_data.get("voltage")
        if v_raw is not None:
            normalized["voltage_v"] = float(v_raw) / 10.0
        
        # Current (usually code 'cur_current' or 'current')
        # Tuya usually reports in milliamps (e.g. 150 = 0.150A)
        # Note: Some devices use different scales, but we'll stick to common Tuya smart plug defaults.
        c_raw = raw_data.get("cur_current")
        if c_raw is None:
            c_raw = raw_data.get("current")
        if c_raw is not None:
            normalized["current_a"] = float(c_raw) / 1000.0

        # Power (usually code 'cur_power' or 'power')
        # Tuya usually reports in deciwatts (e.g. 150 = 15.0W)
        p_raw = raw_data.get("cur_power")
        if p_raw is None:
            p_raw = raw_data.get("power")
        if p_raw is not None:
            normalized["power_w"] = float(p_raw) / 10.0

        # Energy (Total consumption)
        kwh_raw = raw_data.get("add_ele")
        if kwh_raw is None:
            kwh_raw = raw_data.get("cur_electricity")
        if kwh_raw is not None:
            normalized["total_kwh_accumulated"] = float(kwh_raw) / 100.0

        return normalized

    def validate_daily_completeness(self, readings):
        """
        Check if we have exactly 144 readings for the day.
        """
        if not readings:
            return False, 0
        
        count = len(readings)
        return count == 144, count
