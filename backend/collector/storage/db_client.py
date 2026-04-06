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
        """Creates compound indexes for the unified energybuckets collection."""
        collection = self.db["energybuckets"]
        # Index for fast daily document lookups by date and device
        collection.create_index([("date", 1), ("device_id", 1)], unique=True)
        # Index for querying appliance specific aggregations
        collection.create_index([("date", 1), ("appliance_type", 1)])
        # Index for individual readings timestamps
        collection.create_index([("readings.timestamp", 1)])
        logger.info("Indexes verified for energybuckets")

    def store_reading(self, appliance_name, device_id, timestamp, raw_data, weather_data, processed_data=None):
        """
        Stores a single 10-minute reading into the correct collection.
        Uses a document-per-day structure as per implementation plan.
        """
        collection = self.db["energybuckets"]
        app_type = appliance_name.lower().replace("_", "")
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
            # 1. Try to update an existing interval in the daily document
            result = collection.update_one(
                {
                    "date": date_str, 
                    "device_id": device_id, 
                    "readings.interval_index": interval_index
                },
                {
                    "$set": {
                        "readings.$": reading,
                        "last_updated": datetime.now()
                    }
                }
            )

            # 2. If no matching interval was found, either push to existing doc or upsert new doc
            if result.matched_count == 0:
                collection.update_one(
                    {"date": date_str, "device_id": device_id},
                    {
                        "$push": {"readings": reading},
                        "$setOnInsert": {
                            "date": date_str,
                            "device_id": device_id,
                            "appliance_type": app_type,
                            "created_at": datetime.now()
                        },
                        "$set": {"last_updated": datetime.now()},
                        "$inc": {"reading_count": 1}
                    },
                    upsert=True
                )
            
            # Recalculate daily summary for live dashboard updates
            self.final_daily_validation(appliance_name, date_str)
            
            return True
        except Exception as e:
            logger.exception(f"Failed to store reading for {appliance_name}")
            return False

    def get_reading(self, appliance_name, date_str, interval_index):
        """
        Retrieves a specific reading from a daily document by interval_index.
        """
        collection = self.db["energybuckets"]
        app_type = appliance_name.lower().replace("_", "")
        # Using $elemMatch to find the document that contains the matching reading in the array
        doc = collection.find_one(
            {"date": date_str, "readings.interval_index": interval_index},
            {"readings.$": 1} # Project only the matched element from the 'readings' array
        )
        if doc and "readings" in doc and len(doc["readings"]) > 0:
            return doc["readings"][0] # Only one should match due to the query and projection
        return None

    def update_reading_weather(self, appliance_name, date_str, interval_index, weather_data):
        """
        Updates only the weather data for a specific reading within a daily document.
        """
        collection = self.db["energybuckets"]
        try:
            # Use positional operator $ to update the matched element in the array
            result = collection.update_one(
                {"date": date_str, "readings.interval_index": interval_index},
                {"$set": {"readings.$.weather": weather_data}}
            )
            if result.matched_count > 0:
                logger.debug(f"Updated weather for {appliance_name} on {date_str}, interval {interval_index}")
                return True
            else:
                logger.debug(f"No matching reading found for weather update: {appliance_name} {date_str}, interval {interval_index}")
                return False
        except Exception as e:
            logger.exception(f"Failed to update weather for reading {appliance_name} on {date_str}, interval {interval_index}")
            return False

    def final_daily_validation(self, appliance_name, date_str):
        """
        Calculates daily summary (total kWh, peak power, etc.) once 144 points are confirmed.
        """
        collection = self.db["energybuckets"]
        doc = collection.find_one({"date": date_str, "appliance_type": appliance_name.lower().replace("_", "")})
        
        if not doc or "readings" not in doc:
            return None

        readings = doc["readings"]
        count = len(readings)

        # Calculate metrics from processed_data
        peak_power = 0
        total_energy_kwh = 0
        active_intervals = 0
        
        # Sort readings by interval_index to ensure temporal order for integration
        sorted_readings = sorted(readings, key=lambda x: x.get("interval_index", 0))
        
        for i, r in enumerate(sorted_readings):
            p = r.get("processed_data")
            if not p:
                continue
                
            curr_p = p.get("power_w", 0)
            peak_power = max(peak_power, curr_p)
            
            # Energy Estimation: (Power * Time)
            # Only count energy if the device is active (Switch is ON)
            if p.get("is_active"):
                active_intervals += 1
                total_energy_kwh += (curr_p / 6.0) / 1000.0

        summary = {
            "total_readings": count,
            "is_complete": count == 144,
            "peak_power_w": round(peak_power, 2),
            "total_kwh": round(total_energy_kwh, 4),
            "active_minutes": active_intervals * 10,
            "validated_at": datetime.now()
        }

        collection.update_one(
            {"date": date_str, "device_id": doc["device_id"]},
            {"$set": {"daily_summary": summary, "status": "complete" if count == 144 else "incomplete"}}
        )
        return summary

    def get_daily_count(self, appliance_name, date_str):
        collection = self.db["energybuckets"]
        doc = collection.find_one({"date": date_str, "appliance_type": appliance_name.lower().replace("_", "")})
        if doc:
            return doc.get("reading_count", 0)
        return 0
    def get_missing_intervals(self, appliance_name, date_str):
        """
        Returns a list of interval_indexes (0-143) missing for the given day.
        """
        collection = self.db["energybuckets"]
        doc = collection.find_one({"date": date_str, "appliance_type": appliance_name.lower().replace("_", "")})
        
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
        collection = self.db["energybuckets"]
        result = collection.delete_one({"date": date_str, "appliance_type": appliance_name.lower().replace("_", "")})
        if result.deleted_count > 0:
            logger.info(f"Dropped existing data for {appliance_name} on {date_str}")
            return True
        return False
