import pandas as pd
from datetime import datetime
from pymongo import MongoClient, UpdateOne
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
import requests

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_historical_weather(start_date, end_date):
    """Fetch historical weather from Open-Meteo Archive API."""
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        "?latitude=14.5995&longitude=120.9842"
        f"&start_date={start_date}&end_date={end_date}"
        "&hourly=temperature_2m,relative_humidity_2m,precipitation"
        "&timezone=Asia%2FManila"
    )
    logger.info(f"Fetching historical weather from Open-Meteo: {start_date} to {end_date}")
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        hourly = data["hourly"]
        df_weather = pd.DataFrame({
            "timestamp": pd.to_datetime(hourly["time"]),
            "temp": hourly["temperature_2m"],
            "humidity": hourly["relative_humidity_2m"],
            "rainfall": hourly["precipitation"]
        })
        # Set index for easy lookup
        return df_weather.set_index("timestamp")
    except Exception as e:
        logger.error(f"Failed to fetch historical weather: {e}")
        return None

def ingest_data():
    # Load environment variables
    repo_root = Path(__file__).resolve().parents[2]
    load_dotenv(repo_root / ".env")
    
    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DATABASE_NAME", "Sarimax-Thesis")
    
    if not mongo_uri:
        logger.error("MONGODB_URI not found in environment")
        return

    logger.info(f"Connecting to MongoDB: {db_name}")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    coll = db["energybuckets"]

    csv_path = "/Users/geovannyportodo/Sarimax-Thesis/Dataset for Jan 3 to March 15 - Sheet1.csv"
    if not os.path.exists(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        return

    logger.info(f"Reading CSV: {csv_path}")
    df = pd.read_csv(csv_path)

    # Fetch weather for the range
    weather_df = fetch_historical_weather("2026-01-03", "2026-03-15")

    # Appliance mapping
    app_mapping = {
        'Aircon':       {'type': 'aircon',       'device_id': 'a3ed2fe218a724b4fepeni'},
        'Electric Fan': {'type': 'electricfan',  'device_id': 'a3c772d3fde52dbae832bi'},
        'Refrigerator': {'type': 'refrigerator', 'device_id': 'a3986d20c19f33c7c107fw'}
    }

    # Data collection: (iso_date, app_type) -> [readings]
    grouped_data = {}

    logger.info("Parsing CSV rows...")
    current_date_str = None
    
    from zoneinfo import ZoneInfo
    pht = ZoneInfo("Asia/Manila")

    for idx, row in df.iterrows():
        raw_date = row.get('Date')
        if pd.notna(raw_date) and str(raw_date).strip() != "" and str(raw_date).strip() != "TOTAL":
            current_date_str = str(raw_date).strip()
        
        if not current_date_str:
            continue
            
        hour_str = row.get('Hours')
        if pd.isna(hour_str) or str(hour_str).strip() == "" or str(hour_str).strip() == "TOTAL":
            continue

        try:
            dt_base = datetime.strptime(current_date_str, "%B %d, %Y")
            iso_date = dt_base.strftime("%Y-%m-%d")
            
            time_obj = datetime.strptime(str(hour_str).strip(), "%I:%M %p").time()
            timestamp_naive = datetime.combine(dt_base, time_obj)
            timestamp = timestamp_naive.replace(tzinfo=pht)
            
            for csv_col, info in app_mapping.items():
                app_type = info['type']
                device_id = info['device_id']
                
                consumption_raw = row.get(csv_col, 0)
                try:
                    if isinstance(consumption_raw, str):
                        consumption_raw = consumption_raw.replace(',', '.')
                    kwh = float(consumption_raw)
                except:
                    kwh = 0.0
                
                key = (iso_date, app_type)
                if key not in grouped_data:
                    grouped_data[key] = {
                        'device_id': device_id,
                        'readings': []
                    }
                
                grouped_data[key]['readings'].append({
                    'timestamp': timestamp,
                    'kwh': kwh
                })
        except Exception as e:
            logger.warning(f"Failed to parse row {idx}: {e}")
            continue

    logger.info(f"Processed {len(grouped_data)} daily buckets. Preparing MongoDB updates...")
    
    bulk_ops = []
    now = datetime.utcnow()

    for (iso_date, app_type), data in grouped_data.items():
        data['readings'].sort(key=lambda x: x['timestamp'])
        
        total_day_kwh = 0.0
        final_readings = []
        
        for r in data['readings']:
            base_ts = r['timestamp']
            hourly_kwh = r['kwh']
            ten_min_kwh = hourly_kwh / 6.0
            avg_power_w = hourly_kwh * 1000
            
            for i in range(6):
                interval_ts = base_ts + pd.Timedelta(minutes=i*10)
                total_day_kwh += ten_min_kwh
                interval_idx = (interval_ts.hour * 6) + i
                
                # Weather lookup
                # Convert to UTC for weather lookup as weather_df index is likely UTC or matches the API timezone
                # Actually Open-Meteo with timezone Asia/Manila returns PHT timestamps
                lookup_ts = interval_ts.replace(tzinfo=None) # Strip tz for matching if weather_df index is naive
                
                weather_info = {"temp": 0.0, "humidity": 0, "rainfall": 0.0}
                if weather_df is not None:
                    # Find closest hour
                    match_ts = pd.Timestamp(lookup_ts).floor('h')
                    if match_ts in weather_df.index:
                        w_row = weather_df.loc[match_ts]
                        weather_info = {
                            "temp": float(w_row["temp"]),
                            "humidity": int(w_row["humidity"]),
                            "rainfall": float(w_row["rainfall"])
                        }

                final_readings.append({
                    "timestamp": interval_ts,
                    "interval_index": interval_idx,
                    "processed_data": {
                        "is_active": hourly_kwh > 0.001,
                        "voltage_v": 230.0,
                        "current_a": round(avg_power_w / 230.0, 3) if hourly_kwh > 0 else 0,
                        "power_w": round(avg_power_w, 2),
                        "total_kwh_accumulated": round(total_day_kwh, 4)
                    },
                    "weather": weather_info,
                    "processed_at": now
                })
            
        bulk_ops.append(UpdateOne(
            {"date": iso_date, "appliance_type": app_type},
            {
                "$set": {
                    "device_id": data['device_id'],
                    "readings": final_readings,
                    "reading_count": len(final_readings),
                    "daily_summary": {"total_kwh": round(total_day_kwh, 4)},
                    "last_updated": now,
                    "created_at": now,
                    "status": "completed"
                }
            },
            upsert=True
        ))

    if bulk_ops:
        logger.info(f"Executing {len(bulk_ops)} bulk operations...")
        result = coll.bulk_write(bulk_ops)
        logger.info(f"Upserted: {result.upserted_count}, Modified: {result.modified_count}")
    else:
        logger.warning("No data found to ingest.")

    client.close()
    logger.info("Ingestion complete.")

if __name__ == "__main__":
    ingest_data()
