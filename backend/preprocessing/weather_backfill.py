"""
Weather Backfill Script  (Open-Meteo — free, no API key required)
─────────────────────────────────────────────────────────────────
Fetches hourly historical weather for Manila from the Open-Meteo
Archive API and saves to data/raw/weather_raw.csv so the pipeline
has real temperature, humidity, and rainfall features.

Endpoint:
  https://archive-api.open-meteo.com/v1/archive
  ?latitude={lat}&longitude={lon}
  &start_date={YYYY-MM-DD}&end_date={YYYY-MM-DD}
  &hourly=temperature_2m,relative_humidity_2m,precipitation
  &timezone=Asia/Manila
─────────────────────────────────────────────────────────────────
"""

import os
import pandas as pd
import requests
from dotenv import load_dotenv

# Manila coordinates
LAT = 14.5995
LON = 120.9842

def backfill_weather(start_date_override=None, end_date_override=None):
    load_dotenv()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../../"))
    raw_dir = os.path.join(project_root, "data/raw")

    if start_date_override and end_date_override:
        start_date = start_date_override
        end_date = end_date_override
    else:
        # Read existing smartplug data to get the date range
        sp_path = os.path.join(raw_dir, "smartplug_raw.csv")
        if not os.path.exists(sp_path):
            print("Error: smartplug_raw.csv not found. Run the extractor first.")
            return

        df_sp = pd.read_csv(sp_path)
        df_sp["timestamp"] = pd.to_datetime(df_sp["timestamp"], errors="coerce")
        start_date = df_sp["timestamp"].min().date()
        end_date = df_sp["timestamp"].max().date()

    print(f"Energy data range: {start_date} → {end_date}")
    print(f"Location: Manila ({LAT}, {LON})")
    print(f"Fetching hourly weather from Open-Meteo Archive API...\n")

    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={LAT}&longitude={LON}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&hourly=temperature_2m,relative_humidity_2m,precipitation"
        f"&timezone=Asia/Manila"
    )

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {resp.text[:300]}")
        return
    except Exception as e:
        print(f"Request failed: {e}")
        return

    data = resp.json()
    hourly = data.get("hourly", {})

    timestamps = hourly.get("time", [])
    temperatures = hourly.get("temperature_2m", [])
    humidities = hourly.get("relative_humidity_2m", [])
    rainfalls = hourly.get("precipitation", [])

    if not timestamps:
        print("No hourly data returned. The date range may be too recent for the archive.")
        return

    df_wx = pd.DataFrame({
        "timestamp": pd.to_datetime(timestamps),
        "temperature": temperatures,
        "humidity": humidities,
        "rainfall": rainfalls,
    })

    df_wx.sort_values("timestamp", inplace=True)
    df_wx.drop_duplicates(subset=["timestamp"], keep="first", inplace=True)

    # Save
    wx_path = os.path.join(raw_dir, "weather_raw.csv")
    df_wx.to_csv(wx_path, index=False)

    print(f"✅ Saved {len(df_wx)} hourly weather records to {wx_path}")
    print(f"   Date range: {df_wx['timestamp'].min()} → {df_wx['timestamp'].max()}")
    print(f"   Temperature: {df_wx['temperature'].min():.1f}°C — {df_wx['temperature'].max():.1f}°C")
    print(f"   Humidity:    {df_wx['humidity'].min():.0f}% — {df_wx['humidity'].max():.0f}%")
    print(f"   Rainfall:    {df_wx['rainfall'].min():.1f} mm — {df_wx['rainfall'].max():.1f} mm")
    print(f"\nNow re-run the pipeline to include weather features:")
    print(f"  python backend/preprocessing/TH2_Pipeline_Runner.py")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Backfill historical weather data")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    args = parser.parse_args()

    backfill_weather(args.start, args.end)
