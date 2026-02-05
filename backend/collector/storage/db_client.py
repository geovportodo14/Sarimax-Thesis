from pymongo import MongoClient
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MongoDBClient:
    def __init__(self, connection_string, database_name):
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Creates indexes for all appliance collections."""
        appliances = ["aircon", "refrigerator", "electric_fan"]
        for app in appliances:
            collection = self.db[app]
            # Index for daily documents
            collection.create_index([("date", 1), ("device_id", 1)], unique=True)
            # Index for individual readings timestamps
            collection.create_index([("readings.timestamp", 1)])
            logger.info(f"Indexes verified for {app}")

    def store_reading(self, appliance_name, device_id, timestamp, raw_data, weather_data, processed_data=None):
        """
        Stores a single 10-minute reading into the correct collection.
        Uses a document-per-day structure as per implementation plan.
        """
        collection = self.db[appliance_name.lower()]
        date_str = timestamp.strftime("%Y-%m-%d")
        
        # Calculate interval index (0 to 143 for 10-minute intervals)
        interval_index = (timestamp.hour * 6) + (timestamp.minute // 10)

        reading = {
            "timestamp": timestamp,
            "interval_index": interval_index,
            "raw_data": raw_data,
            "processed_data": processed_data,
            "weather": weather_data,
            "processed_at": datetime.now()
        }

        try:
            # Update the daily document: push new reading and update metadata
            # We use $set for processed_data to allow partial updates if needed
            collection.update_one(
                {"date": date_str, "device_id": device_id},
                {
                    "$push": {"readings": reading},
                    "$setOnInsert": {
                        "date": date_str,
                        "device_id": device_id,
                        "appliance_type": appliance_name.lower(),
                        "created_at": datetime.now()
                    },
                    "$set": {"last_updated": datetime.now()},
                    "$inc": {"reading_count": 1}
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.exception(f"Failed to store reading for {appliance_name}")
            return False

    def final_daily_validation(self, appliance_name, date_str):
        """
        Calculates daily summary (total kWh, peak power, etc.) once 144 points are confirmed.
        """
        collection = self.db[appliance_name.lower()]
        doc = collection.find_one({"date": date_str})
        
        if not doc or "readings" not in doc:
            return None

        readings = doc["readings"]
        count = len(readings)

        # Calculate metrics from processed_data
        peak_power = 0
        total_energy = 0
        active_intervals = 0
        
        for r in readings:
            p = r.get("processed_data")
            if p:
                peak_power = max(peak_power, p.get("power_w", 0))
                if p.get("is_active"):
                    active_intervals += 1
        
        # Simplified energy estimation if total_kwh wasn't reported sequentially
        # Better: use the Tuya accumulated value if available
        last_reading = readings[-1].get("processed_data")
        total_energy = last_reading.get("total_kwh_accumulated") if last_reading else 0

        summary = {
            "total_readings": count,
            "is_complete": count == 144,
            "peak_power_w": peak_power,
            "total_kwh": total_energy,
            "active_minutes": active_intervals * 10,
            "validated_at": datetime.now()
        }

        collection.update_one(
            {"date": date_str, "device_id": doc["device_id"]},
            {"$set": {"daily_summary": summary, "status": "complete" if count == 144 else "incomplete"}}
        )
        return summary

    def get_daily_count(self, appliance_name, date_str):
        collection = self.db[appliance_name.lower()]
        doc = collection.find_one({"date": date_str})
        if doc:
            return doc.get("reading_count", 0)
        return 0
    def get_missing_intervals(self, appliance_name, date_str):
        """
        Returns a list of interval_indexes (0-143) missing for the given day.
        """
        collection = self.db[appliance_name.lower()]
        doc = collection.find_one({"date": date_str})
        
        existing_indexes = []
        if doc and "readings" in doc:
            existing_indexes = [r["interval_index"] for r in doc["readings"]]
        
        all_indexes = set(range(144))
        missing_indexes = sorted(list(all_indexes - set(existing_indexes)))
        return missing_indexes

    def drop_daily_data(self, appliance_name, date_str):
        """
        Removes the daily document for a specific appliance and date.
        Useful for clean-state backfilling.
        """
        collection = self.db[appliance_name.lower()]
        result = collection.delete_one({"date": date_str})
        if result.deleted_count > 0:
            logger.info(f"Dropped existing data for {appliance_name} on {date_str}")
            return True
        return False
