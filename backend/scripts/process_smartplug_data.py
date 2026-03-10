#!/usr/bin/env python3
"""
process_smartplug_data.py
=========================
Processes smartplug_raw.csv into cleaned_energy_data.csv (10-min, per appliance)
and safely upserts records into the MongoDB `energybuckets` collection for
January 3, 2026 → February 17, 2026.

Pipeline Summary
----------------
1. Load & segment smartplug_raw.csv by device_id (Aircon / Fridge / Fan).
2. Trim to start: Jan 3, 2026 19:00 PHT.
3. Derive per-interval kWh from the cumulative kwh_total counter,
   correctly handling daily resets that occur at 16:00 PHT.
4. Enforce the Aircon Gap: Feb 7–15 forced to zero (no interpolation).
5. Fill small gaps (≤3 intervals) via linear interpolation.
6. Redistribute each hour's raw device allocations so their sum matches
   the hourly "total_kwh" ground truth from cleaned_energy_data.csv,
   applying hierarchy weights:  Aircon 70% / Fridge 20% / Fan 10%.
   For the Aircon Gap period, the gap devices get 0; remaining share is
   proportionally split among Fridge and Fan.
7. Export data/processed_data/cleaned_energy_data.csv (one row per
   appliance × 10-min interval, with weather joined from weather_raw.csv).
8. Build energybuckets documents and upsert to MongoDB (Jan 3–Feb 17 only).

Usage
-----
    # Preview only — no DB write, prints summary table
    python backend/scripts/process_smartplug_data.py --dry-run

    # Write cleaned CSV + upsert MongoDB
    python backend/scripts/process_smartplug_data.py --execute
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pytz
from dotenv import load_dotenv

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("process_smartplug")

# ── Config ────────────────────────────────────────────────────────────────
load_dotenv()

MANILA_TZ = pytz.timezone("Asia/Manila")
UTC = pytz.utc

# Project root is two levels up from this script
ROOT = Path(__file__).resolve().parent.parent.parent

RAW_CSV          = ROOT / "data" / "raw" / "smartplug_raw.csv"
GROUND_TRUTH_CSV = ROOT / "data" / "jan3tofeb17" / "cleaned_energy_data.csv"
WEATHER_CSV      = ROOT / "data" / "raw" / "weather_raw.csv"
OUTPUT_CSV       = ROOT / "data" / "processed_data" / "cleaned_energy_data.csv"

# Pipeline boundaries (PHT)
START_PHT = MANILA_TZ.localize(datetime(2026, 1,  3, 19,  0))   # Jan  3 19:00
END_PHT   = MANILA_TZ.localize(datetime(2026, 2, 17, 23, 50))   # Feb 17 23:50

# MongoDB upsert window (strict)
UPSERT_START = "2026-01-03"
UPSERT_END   = "2026-02-17"

# Aircon zero-usage gap (inclusive)
AIRCON_GAP_START_DATE = "2026-02-07"
AIRCON_GAP_END_DATE   = "2026-02-15"

# Device registry
DEVICES = {
    "a3ed2fe218a724b4fepeni": {"appliance_type": "aircon",       "name": "Aircon"},
    "a3986d20c19f33c7c107fw": {"appliance_type": "refrigerator", "name": "Refrigerator"},
    "a3c772d3fde52dbae832bi": {"appliance_type": "electricfan",  "name": "Electric_Fan"},
}
AIRCON_ID = "a3ed2fe218a724b4fepeni"

# Hierarchy weights for total-kWh redistribution
HIER_WEIGHTS = {
    "aircon":       0.70,
    "refrigerator": 0.20,
    "electricfan":  0.10,
}

MONGODB_URI   = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "Sarimax-Thesis")


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 1 – Load & Segment Raw Data
# ═══════════════════════════════════════════════════════════════════════════

def load_raw(path: Path) -> dict[str, pd.DataFrame]:
    """
    Load smartplug_raw.csv, trim to [START_PHT, END_PHT],
    and split into one DataFrame per device_id.

    Returns dict: {device_id: df}
    """
    log.info("Loading raw CSV: %s", path)
    df = pd.read_csv(path)

    # Parse timestamp; the CSV has timezone-naive PHT timestamps
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed", utc=False)

    # Localise to PHT (timestamps are already in PHT, just not tagged)
    if df["timestamp"].dt.tz is None:
        df["timestamp"] = df["timestamp"].dt.tz_localize(MANILA_TZ, ambiguous="NaT")
    else:
        df["timestamp"] = df["timestamp"].dt.tz_convert(MANILA_TZ)

    # Keep only known devices
    df = df[df["device_id"].isin(DEVICES.keys())].copy()

    # Trim to pipeline window
    df = df[(df["timestamp"] >= START_PHT) & (df["timestamp"] <= END_PHT)]

    # Sort, deduplicate (keep last reading per timestamp per device)
    df = df.sort_values(["device_id", "timestamp"])
    df = df.drop_duplicates(subset=["device_id", "timestamp"], keep="last")

    log.info("  Raw rows after trim: %d", len(df))

    by_device = {}
    for device_id, meta in DEVICES.items():
        sub = df[df["device_id"] == device_id].copy().reset_index(drop=True)
        log.info("  %s (%s): %d rows", meta["name"], device_id[:12], len(sub))
        by_device[device_id] = sub

    return by_device


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 2 – Build 10-min Grid & Derive interval_kwh
# ═══════════════════════════════════════════════════════════════════════════

def build_grid(start: pd.Timestamp, end: pd.Timestamp) -> pd.DatetimeIndex:
    """Generate a complete 10-minute frequency index between start and end (PHT)."""
    return pd.date_range(start=start, end=end, freq="10min", tz=MANILA_TZ)


def assign_session_day(ts: pd.Series) -> pd.Series:
    """
    The Tuya kwh_total counter resets every day at 16:00 PHT.
    Return the 'session date' for each timestamp:
      - If hour >= 16 → same calendar date
      - If hour <  16 → prior calendar date
    This groups each 16:00→15:50 block under one session label.
    """
    return ts.apply(
        lambda t: t.date() if t.hour >= 16 else (t - pd.Timedelta(days=1)).date()
    )


def derive_interval_kwh(dev_df: pd.DataFrame) -> pd.DataFrame:
    """
    From the cumulative kwh_total column (resets at 16:00 PHT), derive the
    energy consumed per 10-min interval.

    Steps:
    1. Assign session_day (blocks that reset at 16:00).
    2. Within each session, diff kwh_total.
    3. At session start rows, interval_kwh = kwh_total (already small when reset).
    4. Clamp negatives to 0.
    5. Where switch == False: force interval_kwh, power_w, current_a = 0.
    """
    df = dev_df.copy()
    df["session_day"] = assign_session_day(df["timestamp"])

    # Within-session diff
    df["interval_kwh"] = df.groupby("session_day")["kwh_total"].diff()

    # First row of each session: set interval_kwh to 0
    first_of_session = df.groupby("session_day").cumcount() == 0
    df.loc[first_of_session, "interval_kwh"] = 0.0

    # Clamp negatives (counter anomalies)
    df["interval_kwh"] = df["interval_kwh"].clip(lower=0.0)

    # When switch == False, device is off
    off_mask = df["switch"].astype(str).str.lower() == "false"
    df.loc[off_mask, ["interval_kwh", "power_w", "current_a"]] = 0.0

    return df


def reindex_to_grid(dev_df: pd.DataFrame, grid: pd.DatetimeIndex) -> pd.DataFrame:
    """
    Merge device data onto the 10-minute grid using merge_asof (±5 min tolerance).
    Missing intervals are filled with NaN, then small gaps (≤3) are interpolated.
    """
    grid_df = pd.DataFrame({"timestamp": grid})

    dev_df = dev_df.sort_values("timestamp").reset_index(drop=True)

    merged = pd.merge_asof(
        grid_df,
        dev_df,
        on="timestamp",
        tolerance=pd.Timedelta("5min"),
        direction="nearest",
    )

    # Numeric columns to interpolate
    interp_cols = ["voltage_v", "current_a", "power_w", "interval_kwh", "kwh_total"]

    for col in interp_cols:
        if col not in merged.columns:
            continue
        s = merged[col].copy()
        is_nan = s.isna()
        if not is_nan.any():
            continue

        # Identify consecutive NaN run lengths
        group_id = (~is_nan).cumsum()
        gap_size = is_nan.groupby(group_id).transform("sum")

        small_gap = is_nan & (gap_size <= 3)
        interpolated = s.interpolate(method="linear", limit_direction="both")
        merged[col] = s.where(~small_gap, interpolated)

    # Fill switch column: forward-fill then default to True
    if "switch" in merged.columns:
        merged["switch"] = merged["switch"].ffill().infer_objects(copy=False).fillna("True")
    else:
        merged["switch"] = "True"

    # Clamp interval_kwh again after interpolation
    merged["interval_kwh"] = merged["interval_kwh"].clip(lower=0.0).fillna(0.0)
    merged["power_w"]       = merged["power_w"].clip(lower=0.0).fillna(0.0)
    merged["current_a"]     = merged["current_a"].clip(lower=0.0).fillna(0.0)
    merged["voltage_v"]     = merged["voltage_v"].fillna(230.0)  # fallback

    return merged


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 3 – Enforce Aircon Gap (Feb 7–15)
# ═══════════════════════════════════════════════════════════════════════════

def enforce_aircon_gap(df: pd.DataFrame) -> pd.DataFrame:
    """
    For all rows in the Aircon gap period, zero out consumption.
    This is a hard constraint — no interpolation across this period.
    """
    gap_start = pd.Timestamp(AIRCON_GAP_START_DATE, tz=MANILA_TZ)
    gap_end   = pd.Timestamp(AIRCON_GAP_END_DATE + " 23:50", tz=MANILA_TZ)

    mask = (df["timestamp"] >= gap_start) & (df["timestamp"] <= gap_end)
    df.loc[mask, ["interval_kwh", "power_w", "current_a"]] = 0.0
    # Ensure switch column is string type before assignment
    df["switch"] = df["switch"].astype(str)
    df.loc[mask, "switch"] = "False"

    zeroed = mask.sum()
    if zeroed > 0:
        log.info("  Aircon gap enforced: %d intervals zeroed (Feb 7–15)", zeroed)
    return df


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 4 – Load Ground Truth & Redistribute
# ═══════════════════════════════════════════════════════════════════════════

def load_ground_truth(path: Path) -> pd.DataFrame:
    """
    Load the hourly cleaned_energy_data.csv (date, time, total_kwh).
    Returns a DataFrame indexed by (date_str: YYYY-MM-DD, hour: int).

    The CSV uses the date format 'YY-MM-DD' (e.g. '26-01-03').
    """
    log.info("Loading ground truth CSV: %s", path)
    gt = pd.read_csv(path)

    # Parse date column: '26-01-03' → '2026-01-03'
    gt["date_full"] = gt["date"].apply(
        lambda d: "20" + d if d[:2] != "20" else d
    )
    gt["hour"] = gt["time"].str.split(":").str[0].astype(int)
    gt["total_kwh"] = pd.to_numeric(gt["total_kwh"], errors="coerce").fillna(0.0)

    gt = gt[["date_full", "hour", "total_kwh"]].rename(columns={"date_full": "date"})
    log.info("  Ground truth rows: %d (hourly)", len(gt))
    return gt


def redistribute_to_ground_truth(
    grids: dict[str, pd.DataFrame],
    gt: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """
    For each hour slot covered by the ground truth, scale per-device interval_kwh
    values so that the sum across all devices matches the hourly total_kwh.

    The Aircon gap (Feb 7–15) is handled by zeroing Aircon and redistributing
    the remaining share proportionally to Fridge and Fan.

    Algorithm per hour:
    1. Get raw interval_kwh for each device across the 6 × 10-min slots.
    2. Determine active appliances (Aircon is excluded during gap).
    3. Compute hierarchy allocation = total_kwh × weight_i / sum(active weights).
    4. Scale device's 6 intervals proportionally to match its hour allocation,
       preserving the within-hour shape from raw data.
    5. If raw shape is all zeros, distribute evenly across 6 intervals.
    """
    # Build GT lookup: (date_str, hour) -> total_kwh
    gt_lookup = {}
    for _, row in gt.iterrows():
        gt_lookup[(row["date"], int(row["hour"]))] = float(row["total_kwh"])

    out = {did: df.copy() for did, df in grids.items()}

    # Gap range (dates as strings)
    gap_dates = set(
        pd.date_range(AIRCON_GAP_START_DATE, AIRCON_GAP_END_DATE, freq="D")
        .strftime("%Y-%m-%d")
    )

    # All unique PHT hours in the pipeline window
    sample_device_df = next(iter(out.values()))
    unique_hours = (
        sample_device_df["timestamp"]
        .dt.normalize()  # midnight
        .map(lambda t: (t.strftime("%Y-%m-%d"), t))
    )
    # Use the Aircon grid as reference timeline (all devices share the same grid)
    ref_ts = out[AIRCON_ID]["timestamp"]

    scaled_hours = 0
    for ts in ref_ts:
        date_str = ts.strftime("%Y-%m-%d")
        hour     = ts.hour
        key      = (date_str, hour)
        if key not in gt_lookup:
            continue  # no ground truth for this hour

        total_kwh = gt_lookup[key]

        # Determine in-gap for aircon
        in_gap = date_str in gap_dates

        # Active weights
        if in_gap:
            active_weights = {
                "refrigerator": HIER_WEIGHTS["refrigerator"],
                "electricfan":  HIER_WEIGHTS["electricfan"],
            }
        else:
            active_weights = dict(HIER_WEIGHTS)  # all three

        weight_sum = sum(active_weights.values())

        # For each device, get the 6-interval hour mask and scale
        for device_id, meta in DEVICES.items():
            aptype = meta["appliance_type"]
            df = out[device_id]

            # Hour mask: same date, same hour, all 6 intervals
            mask = (df["timestamp"].dt.date.astype(str) == date_str) & \
                   (df["timestamp"].dt.hour == hour)

            if not mask.any():
                continue

            # Aircon gets 0 during gap
            if in_gap and device_id == AIRCON_ID:
                df.loc[mask, "interval_kwh"] = 0.0
                df.loc[mask, "power_w"] = 0.0
                continue

            # Device allocation for this hour
            if aptype not in active_weights:
                df.loc[mask, "interval_kwh"] = 0.0
                df.loc[mask, "power_w"] = 0.0
                continue

            device_kwh_target = total_kwh * (active_weights[aptype] / weight_sum)

            # Raw shape across 6 intervals
            raw_vals = df.loc[mask, "interval_kwh"].values.astype(float)
            raw_sum  = raw_vals.sum()

            if raw_sum > 1e-9:
                # Scale existing shape
                scaled = raw_vals * (device_kwh_target / raw_sum)
            else:
                # Shape is flat — distribute evenly
                n = max(len(raw_vals), 1)
                scaled = np.full(n, device_kwh_target / n)

            df.loc[mask, "interval_kwh"] = scaled.round(6)
            # Derive power_w from interval_kwh: kWh / (10min/60) = kW × 1000 → W
            df.loc[mask, "power_w"] = (scaled * 6000.0).round(2)

        scaled_hours += 1

    log.info("  Redistribution complete — %d hour slots scaled", scaled_hours)
    return out


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 5 – Join Weather & Compute Cumulative
# ═══════════════════════════════════════════════════════════════════════════

def load_weather(path: Path) -> pd.DataFrame:
    """Load weather_raw.csv (hourly PHT) and forward-fill to 10-min."""
    w = pd.read_csv(path, parse_dates=["timestamp"])
    w["timestamp"] = pd.to_datetime(w["timestamp"])
    if w["timestamp"].dt.tz is None:
        w["timestamp"] = w["timestamp"].dt.tz_localize(MANILA_TZ)
    else:
        w["timestamp"] = w["timestamp"].dt.tz_convert(MANILA_TZ)
    w = w.sort_values("timestamp").rename(
        columns={"temperature": "temp_C", "humidity": "humidity", "rainfall": "rainfall"}
    )
    return w[["timestamp", "temp_C", "humidity", "rainfall"]]


def join_weather(dev_df: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    """Merge weather onto 10-min device data using merge_asof (nearest hour)."""
    return pd.merge_asof(
        dev_df.sort_values("timestamp"),
        weather.sort_values("timestamp"),
        on="timestamp",
        tolerance=pd.Timedelta("60min"),
        direction="nearest",
    )


def compute_daily_cumulative(dev_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute daily_kwh_cumulative: rolling cumsum of interval_kwh
    resetting at midnight (00:00 PHT) each day.
    """
    df = dev_df.copy()
    df["_date"] = df["timestamp"].dt.date
    df["daily_kwh_cumulative"] = df.groupby("_date")["interval_kwh"].cumsum().round(6)
    df = df.drop(columns=["_date"])
    return df


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 6 – Assemble & Export CSV
# ═══════════════════════════════════════════════════════════════════════════

def assemble_csv(grids: dict[str, pd.DataFrame], weather: pd.DataFrame) -> pd.DataFrame:
    """
    Concatenate all per-device grids into one master DataFrame,
    join weather, compute cumulative, and return sorted.
    """
    frames = []
    for device_id, df in grids.items():
        meta = DEVICES[device_id]
        df = df.copy()
        df["device_id"]      = device_id
        df["appliance_type"] = meta["appliance_type"]
        df = join_weather(df, weather)
        df = compute_daily_cumulative(df)
        frames.append(df)

    master = pd.concat(frames, ignore_index=True)
    master = master.sort_values(["timestamp", "appliance_type"]).reset_index(drop=True)

    # Select & order output columns
    out_cols = [
        "timestamp", "device_id", "appliance_type",
        "switch", "voltage_v", "current_a", "power_w",
        "interval_kwh", "daily_kwh_cumulative",
        "temp_C", "humidity", "rainfall",
    ]
    for c in out_cols:
        if c not in master.columns:
            master[c] = np.nan

    master["timestamp_pht"] = master["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    out_cols = ["timestamp_pht"] + [c for c in out_cols if c != "timestamp"]

    return master[out_cols]


def export_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    log.info("CSV exported: %s  (%d rows)", path, len(df))


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 7 – Build & Upsert MongoDB Documents
# ═══════════════════════════════════════════════════════════════════════════

def build_energybucket_doc(
    date_str: str,
    device_id: str,
    dev_day_df: pd.DataFrame,
) -> dict:
    """
    Build one energybucket document for a single appliance on a single date.
    Schema matches the existing `energybuckets` collection.
    """
    meta = DEVICES[device_id]
    readings = []
    peak_power   = 0.0
    total_kwh    = 0.0
    active_count = 0

    for _, row in dev_day_df.iterrows():
        ts_pht = row["timestamp"]
        ts_utc = ts_pht.astimezone(UTC)

        pht_hour = ts_pht.hour
        pht_min  = ts_pht.minute
        interval_index = pht_hour * 6 + pht_min // 10

        pw  = float(row.get("power_w", 0.0))
        ca  = float(row.get("current_a", 0.0))
        vv  = float(row.get("voltage_v", 230.0))
        ikw = float(row.get("interval_kwh", 0.0))
        sw  = str(row.get("switch", "True")).strip().lower() == "true"

        # Cumulative kWh within the day (running total for MongoDB)
        cum_kwh = float(row.get("daily_kwh_cumulative", 0.0))

        weather = {
            "temp":     float(row["temp_C"])   if pd.notna(row.get("temp_C"))   else None,
            "humidity": float(row["humidity"]) if pd.notna(row.get("humidity")) else None,
            "rainfall": float(row["rainfall"]) if pd.notna(row.get("rainfall")) else None,
        }

        processed_data = {
            "voltage_v":              round(vv,  3),
            "current_a":              round(ca,  6),
            "power_w":                round(pw,  2),
            "total_kwh_accumulated":  round(cum_kwh, 6),
            "is_active":              sw and pw > 0,
        }

        readings.append({
            "timestamp":      ts_utc.to_pydatetime(),
            "interval_index": interval_index,
            "processed_data": processed_data,
            "weather":        weather,
        })

        if sw and pw > 0:
            active_count += 1
            total_kwh    += ikw
            peak_power    = max(peak_power, pw)

    # Sort by interval_index
    readings.sort(key=lambda r: r["interval_index"])

    now_utc = datetime.now(timezone.utc)
    doc = {
        "date":           date_str,
        "device_id":      device_id,
        "appliance_type": meta["appliance_type"],
        "readings":       readings,
        "reading_count":  len(readings),
        "daily_summary": {
            "total_readings":  len(readings),
            "is_complete":     len(readings) == 144,
            "peak_power_w":    round(peak_power, 2),
            "total_kwh":       round(total_kwh, 4),
            "active_minutes":  active_count * 10,
            "validated_at":    now_utc,
        },
        "last_updated": now_utc,
        "status": "complete" if len(readings) == 144 else "incomplete",
    }
    return doc


def upsert_to_mongo(grids: dict[str, pd.DataFrame], dry_run: bool) -> None:
    """
    Build daily energybucket documents for Jan 3–Feb 17 and upsert into MongoDB.
    Uses update_one + upsert=True to preserve `created_at` if the doc already exists.
    """
    import pymongo

    if dry_run:
        log.info("DRY RUN: skipping MongoDB connection.")
    else:
        if not MONGODB_URI:
            log.error("MONGODB_URI is not set. Cannot upsert.")
            return
        client = pymongo.MongoClient(MONGODB_URI, serverSelectionTimeoutMS=15000)
        db     = client[DATABASE_NAME]
        coll   = db["energybuckets"]
        try:
            client.admin.command("ping")
            log.info("Connected to MongoDB: %s / %s", DATABASE_NAME, "energybuckets")
        except Exception as e:
            log.error("MongoDB connection failed: %s", e)
            return

    upsert_dates = pd.date_range(UPSERT_START, UPSERT_END, freq="D")

    total_upserted = 0
    total_skipped  = 0

    for date in upsert_dates:
        date_str  = date.strftime("%Y-%m-%d")
        date_pht  = MANILA_TZ.localize(datetime(date.year, date.month, date.day))
        next_day  = date_pht + timedelta(days=1)

        # Day summary line
        day_rows = []

        for device_id, df in grids.items():
            # Filter to this calendar day (PHT)
            day_mask  = (df["timestamp"] >= date_pht) & (df["timestamp"] < next_day)
            dev_day   = df[day_mask].copy()

            if dev_day.empty:
                log.warning("  %s | %s: no data for this date — skipping",
                            date_str, DEVICES[device_id]["name"])
                total_skipped += 1
                continue

            doc = build_energybucket_doc(date_str, device_id, dev_day)

            summary = doc["daily_summary"]
            log.info(
                "  %s | %-12s | %3d readings | %.4f kWh | peak %6.1f W | %s",
                date_str,
                DEVICES[device_id]["name"],
                summary["total_readings"],
                summary["total_kwh"],
                summary["peak_power_w"],
                "✓" if summary["is_complete"] else "⚠ INCOMPLETE",
            )
            day_rows.append(doc)

            if not dry_run:
                # Safe upsert — preserves `created_at` if doc exists
                result = coll.update_one(
                    filter={"date": date_str, "device_id": device_id},
                    update={
                        "$set": {
                            "readings":       doc["readings"],
                            "reading_count":  doc["reading_count"],
                            "daily_summary":  doc["daily_summary"],
                            "appliance_type": doc["appliance_type"],
                            "last_updated":   doc["last_updated"],
                            "status":         doc["status"],
                        },
                        "$setOnInsert": {
                            "created_at": datetime.now(timezone.utc),
                        },
                    },
                    upsert=True,
                )
                total_upserted += 1

    if dry_run:
        log.info("DRY RUN complete. %d documents would be upserted.", len(upsert_dates) * 3)
    else:
        log.info("Upsert complete — %d documents written, %d skipped.", total_upserted, total_skipped)
        client.close()


# ═══════════════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════

def run(dry_run: bool = True) -> None:
    log.info("=" * 65)
    log.info("SMARTPLUG DATA PROCESSING PIPELINE")
    log.info("Mode: %s", "DRY-RUN" if dry_run else "EXECUTE")
    log.info("Window: %s → %s (PHT)", START_PHT.strftime("%Y-%m-%d %H:%M"),
             END_PHT.strftime("%Y-%m-%d %H:%M"))
    log.info("=" * 65)

    # ── 1. Load raw data ──────────────────────────────────────────────────
    log.info("PHASE 1 — Loading & segmenting raw data")
    by_device = load_raw(RAW_CSV)

    # ── 2. Build grid, derive interval_kwh, interpolate gaps ──────────────
    log.info("PHASE 2 — Building 10-min grid & deriving interval kWh")
    grid = build_grid(START_PHT, END_PHT)
    log.info("  Grid: %d intervals (%s → %s)",
             len(grid), grid[0].strftime("%Y-%m-%d %H:%M"),
             grid[-1].strftime("%Y-%m-%d %H:%M"))

    grids: dict[str, pd.DataFrame] = {}
    for device_id, raw_df in by_device.items():
        name = DEVICES[device_id]["name"]
        log.info("  Processing %s …", name)

        # Derive interval kWh from cumulative counter
        derived = derive_interval_kwh(raw_df)

        # Reindex onto full grid
        aligned = reindex_to_grid(derived, grid)
        aligned["device_id"] = device_id

        grids[device_id] = aligned

    # ── 3. Enforce Aircon gap ─────────────────────────────────────────────
    log.info("PHASE 3 — Enforcing Aircon gap (Feb 7–15)")
    grids[AIRCON_ID] = enforce_aircon_gap(grids[AIRCON_ID])

    # ── 4. Load ground truth & redistribute ───────────────────────────────
    log.info("PHASE 4 — Redistributing to match hourly ground truth")
    gt = load_ground_truth(GROUND_TRUTH_CSV)
    grids = redistribute_to_ground_truth(grids, gt)

    # ── 5. Load weather ───────────────────────────────────────────────────
    log.info("PHASE 5 — Joining weather data")
    weather = load_weather(WEATHER_CSV)

    # ── 6. Assemble & export CSV ─────────────────────────────────────────
    log.info("PHASE 6 — Assembling final CSV")
    master_df = assemble_csv(grids, weather)

    # Validation summary
    total_rows = len(master_df)
    aircon_gap_rows = master_df[
        (master_df["appliance_type"] == "aircon") &
        (master_df["timestamp_pht"] >= AIRCON_GAP_START_DATE) &
        (master_df["timestamp_pht"] <= AIRCON_GAP_END_DATE + " 23:50:00")
    ]
    gap_nonzero = (aircon_gap_rows["interval_kwh"] > 0).sum()
    neg_kwh = (master_df["interval_kwh"] < 0).sum()

    log.info("  Validation:")
    log.info("    Total rows: %d", total_rows)
    log.info("    Aircon gap non-zero rows: %d (expect 0)", gap_nonzero)
    log.info("    Negative interval_kwh:   %d (expect 0)", neg_kwh)

    if not dry_run:
        export_csv(master_df, OUTPUT_CSV)

    # ── 7. Upsert MongoDB ────────────────────────────────────────────────
    log.info("PHASE 7 — MongoDB Upsert (Jan 3–Feb 17)")

    # For MongoDB, we only use the grids joined with weather and cumulative
    # Rebuild grids with weather for the MongoDB builder
    grids_with_meta: dict[str, pd.DataFrame] = {}
    for device_id, df in grids.items():
        enriched = join_weather(df, weather)
        enriched = compute_daily_cumulative(enriched)
        grids_with_meta[device_id] = enriched

    upsert_to_mongo(grids_with_meta, dry_run=dry_run)

    log.info("=" * 65)
    log.info("Pipeline complete.")
    log.info("=" * 65)


# ═══════════════════════════════════════════════════════════════════════════
# CLI Entry Point
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Smartplug Data Processing Pipeline — cleans raw data and upserts to MongoDB."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview pipeline output without writing CSV or MongoDB.",
    )
    group.add_argument(
        "--execute",
        action="store_true",
        help="Run full pipeline: export CSV + upsert MongoDB.",
    )
    args = parser.parse_args()
    run(dry_run=args.dry_run)
