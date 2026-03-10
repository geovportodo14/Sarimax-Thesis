#!/usr/bin/env python3
"""
reconstruct_energybuckets.py
============================
Reconstructs and backfills the `energybuckets` collection in MongoDB
for the period Jan 3, 2026 → Feb 17, 2026.

Data Sources (priority order):
  1. Archive CSVs in data/archive/energy_data/
  2. MongoDB source collections (aircon, electric_fan, refrigerator)

Usage:
  python reconstruct_energybuckets.py --dry-run        # Preview only
  python reconstruct_energybuckets.py --execute         # Write to DB
  python reconstruct_energybuckets.py --validate-only   # Docling PDF validation only
"""

import os
import sys
import glob
import argparse
import logging
from datetime import datetime, timedelta, time as dt_time, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pymongo
import pytz
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("reconstruct")

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "Sarimax-Thesis")
CSV_DIR = Path("data/archive/energy_data")
PDF_PATH = Path("2 months chart.pdf")

MANILA_TZ = pytz.timezone("Asia/Manila")
UTC = pytz.utc

# Recovery window
START_DATE = datetime(2026, 1, 3).date()
END_DATE = datetime(2026, 2, 17).date()

# First day starts at 18:00 PHT (10:00 UTC); subsequent days start 00:00 PHT
FIRST_DAY_START_HOUR_PHT = 18

# Device mapping  (name → device_id, appliance_type)
DEVICES = {
    "Aircon":       {"device_id": "a3ed2fe218a724b4fepeni",  "appliance_type": "aircon"},
    "Refrigerator": {"device_id": "a3986d20c19f33c7c107fw",  "appliance_type": "refrigerator"},
    "Electric_Fan": {"device_id": "a3c772d3fde52dbae832bi",  "appliance_type": "electricfan"},
}

# Tuya raw-value scaling (same as preprocessor.py)
TUYA_SCALE = {
    "cur_voltage": 10.0,     # centivolts → V
    "cur_current": 1000.0,   # milliamps → A
    "cur_power":   10.0,     # deciwatts → W
    "add_ele":     100.0,    # → kWh
}

ENERGY_PROPERTIES = list(TUYA_SCALE.keys())


# ===================================================================
# 1. DATA LOADING
# ===================================================================

def load_csv_for_date(date_obj: datetime.date) -> pd.DataFrame | None:
    """Load an archive CSV and pivot to wide-format per-device readings."""
    fname = CSV_DIR / f"energy_log_{date_obj.strftime('%Y%m%d')}.csv"
    if not fname.exists():
        return None

    log.info("  Loading CSV: %s", fname.name)
    df = pd.read_csv(fname, parse_dates=["timestamp"])

    # Keep only the energy-related Tuya properties + switch_1
    df = df[df["property"].isin(ENERGY_PROPERTIES + ["switch_1"])].copy()

    # Pivot: rows = (timestamp, device, weather), cols = property
    weather_cols = ["temp_C", "humidity", "rainfall"]
    id_cols = ["timestamp", "device"] + weather_cols
    pivot = df.pivot_table(
        index=id_cols,
        columns="property",
        values="value",
        aggfunc="first",
    ).reset_index()

    # Flatten column names
    pivot.columns.name = None

    # Convert numeric columns
    for prop in ENERGY_PROPERTIES:
        if prop in pivot.columns:
            pivot[prop] = pd.to_numeric(pivot[prop], errors="coerce")

    # Handle switch_1
    if "switch_1" in pivot.columns:
        pivot["switch_1"] = pivot["switch_1"].astype(str).str.strip().str.lower() == "true"
    else:
        pivot["switch_1"] = True

    return pivot


def load_mongo_for_date(db, date_obj: datetime.date) -> pd.DataFrame | None:
    """Fallback: read from individual device source collections in MongoDB."""
    coll_map = {
        "Aircon": "aircon",
        "Refrigerator": "refrigerator",
        "Electric_Fan": "electric_fan",
    }
    frames = []
    date_str = date_obj.strftime("%Y-%m-%d")

    for dev_name, coll_name in coll_map.items():
        coll = db[coll_name]
        # DEBUG: print query details
        print(f"Querying {coll_name} for date: {date_str}")
        doc = coll.find_one({"date": date_str})
        if not doc:
            print(f"  No document found in {coll_name}")
            continue
        if "readings" not in doc:
            print(f"  'readings' key missing in {coll_name} doc")
            continue
        for r in doc["readings"]:
            ts = r.get("timestamp")
            pd_data = r.get("processed_data") or {}
            weather = r.get("weather") or {}
            raw = r.get("raw_data") or {}
            
            # Use data from processed_data or raw_data
            row = {
                "timestamp": ts,
                "device": dev_name,
                "cur_voltage": raw.get("cur_voltage") or (pd_data.get("voltage_v") * TUYA_SCALE["cur_voltage"] if pd_data.get("voltage_v") else None),
                "cur_current": raw.get("cur_current") or (pd_data.get("current_a") * TUYA_SCALE["cur_current"] if pd_data.get("current_a") else None),
                "cur_power": raw.get("cur_power") or (pd_data.get("power_w") * TUYA_SCALE["cur_power"] if pd_data.get("power_w") else None),
                "add_ele": raw.get("add_ele") or (pd_data.get("total_kwh_accumulated") * TUYA_SCALE["add_ele"] if pd_data.get("total_kwh_accumulated") else None),
                "switch_1": (str(raw.get("switch_1", "True")).strip().lower() == "true") if raw.get("switch_1") is not None else True,
                "temp_C": weather.get("temp") or weather.get("temp_C"),
                "humidity": weather.get("humidity"),
                "rainfall": weather.get("rainfall"),
            }
            frames.append(row)
    if not frames:
        return None
    df = pd.DataFrame(frames)
    
    # Ensure numeric types for energy fields
    numeric_cols = ["cur_voltage", "cur_current", "cur_power", "add_ele", "temp_C", "humidity", "rainfall"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            
    return df


# ===================================================================
# 2. TIME-SERIES ALIGNMENT
# ===================================================================

def generate_10min_grid(date_obj: datetime.date, is_first_day: bool = False):
    """Generate 144 target timestamps for a PHT day (00:00–23:50 PHT, 10-min)."""
    if is_first_day:
        # Jan 3 starts at 18:00 PHT
        base = MANILA_TZ.localize(datetime.combine(date_obj, dt_time(FIRST_DAY_START_HOUR_PHT, 0)))
        # Only 6 hours of data: 18:00–23:50 → 36 intervals
        n_intervals = 36
    else:
        base = MANILA_TZ.localize(datetime.combine(date_obj, dt_time.min))
        n_intervals = 144
    return [base + timedelta(minutes=i * 10) for i in range(n_intervals)]


def align_to_grid(df: pd.DataFrame, grid: list) -> pd.DataFrame:
    """Align raw readings to the 10-minute grid using merge_asof."""
    if df is None or df.empty:
        return pd.DataFrame()

    # Ensure tz-aware timestamps in PHT
    if df["timestamp"].dt.tz is None:
        df["timestamp"] = df["timestamp"].dt.tz_localize(MANILA_TZ)
    else:
        df["timestamp"] = df["timestamp"].dt.tz_convert(MANILA_TZ)

    grid_df = pd.DataFrame({"grid_ts": grid})
    results = []

    for device_name in df["device"].unique():
        dev_df = df[df["device"] == device_name].sort_values("timestamp").copy()
        dev_df = dev_df.drop_duplicates(subset=["timestamp"], keep="last")

        merged = pd.merge_asof(
            grid_df.rename(columns={"grid_ts": "timestamp"}),
            dev_df,
            on="timestamp",
            tolerance=pd.Timedelta("5min"),
            direction="nearest",
        )
        merged["device"] = device_name
        results.append(merged)

    if not results:
        return pd.DataFrame()
    return pd.concat(results, ignore_index=True)


# ===================================================================
# 3. DATA QUALITY
# ===================================================================

def enforce_quality(df: pd.DataFrame) -> pd.DataFrame:
    """Apply quality rules: values > 0, linear interpolation for small gaps."""
    if df.empty:
        return df

    numeric_cols = ["cur_voltage", "cur_current", "cur_power", "add_ele"]

    for device_name in df["device"].unique():
        mask = df["device"] == device_name
        for col in numeric_cols:
            if col not in df.columns:
                continue
            # Replace 0 or negative with NaN for interpolation
            zeros = mask & (df[col] <= 0)
            df.loc[zeros, col] = np.nan

            # Count consecutive NaNs per device
            device_series = df.loc[mask, col].copy()
            if device_series.isna().sum() == 0:
                continue

            # Identify gap groups
            is_nan = device_series.isna()
            gap_groups = (~is_nan).cumsum()
            gap_sizes = is_nan.groupby(gap_groups).transform("sum")

            # Only interpolate gaps ≤ 3 intervals
            small_gap_mask = is_nan & (gap_sizes <= 3)
            if small_gap_mask.any():
                interpolated = device_series.interpolate(method="linear")
                df.loc[mask, col] = device_series.where(~small_gap_mask, interpolated)

    return df


# ===================================================================
# 4. NORMALIZE & BUILD DOCUMENTS
# ===================================================================

def normalize_row(row) -> dict:
    """Apply Tuya scaling to a single row and return processed_data dict."""
    voltage = row.get("cur_voltage")
    current = row.get("cur_current")
    power = row.get("cur_power")
    add_ele = row.get("add_ele")

    processed = {
        "voltage_v": float(voltage / TUYA_SCALE["cur_voltage"]) if pd.notna(voltage) else None,
        "current_a": float(current / TUYA_SCALE["cur_current"]) if pd.notna(current) else None,
        "power_w": float(power / TUYA_SCALE["cur_power"]) if pd.notna(power) else None,
        "total_kwh_accumulated": float(add_ele / TUYA_SCALE["add_ele"]) if pd.notna(add_ele) else None,
        "is_active": bool(row.get("switch_1", False)),
    }
    return processed


def build_daily_document(date_obj, device_name, aligned_df, is_first_day=False):
    """Build one energybucket document for a single appliance on a single day."""
    device_info = DEVICES[device_name]
    date_str = date_obj.strftime("%Y-%m-%d")

    dev_df = aligned_df[aligned_df["device"] == device_name].copy()
    if dev_df.empty:
        return None

    readings = []
    peak_power = 0.0
    total_kwh = 0.0
    active_intervals = 0

    for _, row in dev_df.iterrows():
        ts_pht = row["timestamp"]
        # Convert to UTC for storage
        ts_utc = ts_pht.astimezone(UTC)

        # Calculate interval_index based on PHT hour/minute
        pht_hour = ts_pht.hour
        pht_min = ts_pht.minute
        interval_index = pht_hour * 6 + pht_min // 10

        processed = normalize_row(row)

        weather = {
            "temp": float(row["temp_C"]) if pd.notna(row.get("temp_C")) else None,
            "humidity": float(row["humidity"]) if pd.notna(row.get("humidity")) else None,
            "rainfall": float(row["rainfall"]) if pd.notna(row.get("rainfall")) else None,
        }

        reading = {
            "timestamp": ts_utc.to_pydatetime() if hasattr(ts_utc, 'to_pydatetime') else ts_utc,
            "interval_index": interval_index,
            "processed_data": processed,
            "weather": weather,
        }
        readings.append(reading)

        # Aggregate for daily summary
        pw = processed.get("power_w") or 0.0
        peak_power = max(peak_power, pw)
        if processed.get("is_active") and pw > 0:
            active_intervals += 1
            total_kwh += (pw / 6.0) / 1000.0  # 10-min interval → kWh

    # Sort readings by interval_index
    readings.sort(key=lambda r: r["interval_index"])

    doc = {
        "date": date_str,
        "device_id": device_info["device_id"],
        "appliance_type": device_info["appliance_type"],
        "readings": readings,
        "reading_count": len(readings),
        "daily_summary": {
            "total_readings": len(readings),
            "is_complete": len(readings) == 144,
            "peak_power_w": round(peak_power, 2),
            "total_kwh": round(total_kwh, 4),
            "active_minutes": active_intervals * 10,
            "validated_at": datetime.now(timezone.utc),
        },
        "created_at": datetime.now(timezone.utc),
        "last_updated": datetime.now(timezone.utc),
        "status": "complete" if len(readings) == 144 else "incomplete",
    }
    return doc


# ===================================================================
# 5. DOCLING PDF VALIDATION
# ===================================================================

def extract_pdf_trendline(pdf_path: Path) -> dict | None:
    """
    Use Docling to parse the Smart Life PDF chart and extract
    any tabular or textual energy data for trendline comparison.
    Returns a dict of {date_str: total_power_value} or None.
    """
    try:
        from docling.document_converter import DocumentConverter
    except ImportError:
        log.error("docling is not installed. Run: pip install docling")
        return None

    if not pdf_path.exists():
        log.warning("PDF not found: %s", pdf_path)
        return None

    log.info("Parsing PDF with Docling: %s", pdf_path)
    converter = DocumentConverter()
    result = converter.convert(str(pdf_path))

    # Extract the full markdown content
    md_content = result.document.export_to_markdown()
    log.info("Docling extracted %d characters of content from PDF", len(md_content))

    # Save raw extraction for debugging
    extraction_path = Path("docling_extraction.md")
    extraction_path.write_text(md_content, encoding="utf-8")
    log.info("Saved raw Docling extraction to %s", extraction_path)

    # Try to extract tabular data
    tables = result.document.tables if hasattr(result.document, "tables") else []
    log.info("Found %d tables in PDF", len(tables))

    # Attempt to parse energy values from text content
    # Look for patterns like dates and kWh values
    import re
    reference_data = {}

    # Extract sequential kWh values
    # Docling output is structured with lines like "2.97 kwh" interspersed with structural texts
    # Since dates weren't extracted, we will collect all valid kWh numbers and map them
    # sequentially to our date range (Jan 3 to Feb 17 = 46 days). 
    # Notice the PDF has more data points, so we align backwards from Feb 17.
    import re
    from datetime import datetime, timedelta

    lines = md_content.split("\n")
    kwh_values = []
    
    for line in lines:
        line = line.strip()
        # Look for a number followed immediately by kWh/kwh/KWH at the end of the line
        match = re.fullmatch(r"(\d+\.?\d*)\s*(?:kWh|kwh|KWH)", line, re.IGNORECASE)
        if match:
            kwh_values.append(float(match.group(1)))

    reference_data = {}
    if kwh_values:
        log.info("Extracted %d sequential daily kWh values from Docling", len(kwh_values))
        
        # We know the end date of the timeline is Feb 17 (or close).
        # We will map the last `N` values to the days leading up to Feb 17.
        # But wait, looking at the docling output, they are listed chronologically.
        # Let's map chronologically from Jan 3. If there are extra, we truncate.
        
        start_date = datetime(2026, 1, 3).date()
        for i, val in enumerate(kwh_values):
            target_date = start_date + timedelta(days=i)
            # Stop if we pass our end date (Feb 17)
            if target_date > datetime(2026, 2, 17).date():
                break
            reference_data[target_date.strftime("%Y-%m-%d")] = val
            
    if not reference_data:
        log.warning("Could not extract structured energy data from PDF. "
                     "The chart may be a pure image. Check docling_extraction.md for raw output.")

    # Also extract any table data
    for i, table in enumerate(tables):
        log.info("Table %d: %s", i, table)
        try:
            table_df = table.export_to_dataframe()
            log.info("Table %d DataFrame:\n%s", i, table_df.to_string())
        except Exception:
            pass

    return reference_data if reference_data else None


def generate_verification_report(daily_docs: list, pdf_data: dict | None):
    """Generate a verification report comparing reconstructed data to PDF trendline."""
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("  ENERGYBUCKETS RECONSTRUCTION — VERIFICATION REPORT")
    report_lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 70)
    report_lines.append("")

    # Aggregate reconstructed daily totals
    daily_totals = {}
    for doc in daily_docs:
        date_str = doc["date"]
        kwh = doc["daily_summary"]["total_kwh"]
        if date_str not in daily_totals:
            daily_totals[date_str] = {"total_kwh": 0, "appliances": {}}
        daily_totals[date_str]["total_kwh"] += kwh
        daily_totals[date_str]["appliances"][doc["appliance_type"]] = kwh

    report_lines.append("DAILY SUMMARY")
    report_lines.append("-" * 70)
    report_lines.append(f"{'Date':<14} {'Aircon':>10} {'Refrig':>10} {'Fan':>10} {'Total':>10} {'PDF Ref':>10} {'Var%':>8}")
    report_lines.append("-" * 70)

    total_var_pct = []

    for date_str in sorted(daily_totals.keys()):
        dt = daily_totals[date_str]
        aircon = dt["appliances"].get("aircon", 0)
        fridge = dt["appliances"].get("refrigerator", 0)
        fan = dt["appliances"].get("electricfan", 0)
        total = dt["total_kwh"]

        # Check against PDF reference
        pdf_ref = "N/A"
        var_pct_str = "N/A"
        if pdf_data:
            for key, val in pdf_data.items():
                if date_str in key or key in date_str:
                    pdf_ref = f"{val:.2f}"
                    if val > 0:
                        var_pct = ((total - val) / val) * 100
                        var_pct_str = f"{var_pct:+.1f}%"
                        total_var_pct.append(abs(var_pct))
                    break

        report_lines.append(
            f"{date_str:<14} {aircon:>10.4f} {fridge:>10.4f} {fan:>10.4f} "
            f"{total:>10.4f} {pdf_ref:>10} {var_pct_str:>8}"
        )

    report_lines.append("-" * 70)
    report_lines.append(f"Total documents created: {len(daily_docs)}")
    report_lines.append(f"Total days covered: {len(daily_totals)}")

    if total_var_pct:
        avg_var = sum(total_var_pct) / len(total_var_pct)
        max_var = max(total_var_pct)
        report_lines.append(f"Average absolute variance vs PDF: {avg_var:.1f}%")
        report_lines.append(f"Maximum absolute variance vs PDF: {max_var:.1f}%")
        if max_var > 20:
            report_lines.append("⚠️  WARNING: Some days exceed 20% variance threshold!")
    else:
        report_lines.append("(No PDF reference data available for comparison)")

    report_lines.append("")
    report_text = "\n".join(report_lines)

    # Print and save
    print(report_text)
    report_path = Path("verification_report.txt")
    report_path.write_text(report_text, encoding="utf-8")
    log.info("Verification report saved to %s", report_path)

    return report_text


# ===================================================================
# 6. MAIN PIPELINE
# ===================================================================

def run_pipeline(mode: str = "dry-run"):
    """
    Main reconstruction pipeline.
    mode: 'dry-run' | 'execute' | 'validate-only'
    """
    log.info("=" * 60)
    log.info("ENERGYBUCKETS RECONSTRUCTION PIPELINE")
    log.info("Mode: %s", mode)
    log.info("Period: %s → %s", START_DATE, END_DATE)
    log.info("=" * 60)

    # Connect to MongoDB
    client = pymongo.MongoClient(MONGODB_URI, serverSelectionTimeoutMS=20000)
    db = client[DATABASE_NAME]
    
    # Test connection
    try:
        client.admin.command('ping')
        log.info("Successfully connected to MongoDB Atlas")
    except Exception as e:
        log.error(f"Failed to connect to MongoDB: {e}")
        return

    if mode == "validate-only":
        # Just run Docling validation on existing data
        pdf_data = extract_pdf_trendline(PDF_PATH)
        existing_docs = list(db["energybuckets"].find(
            {"date": {"$gte": START_DATE.strftime("%Y-%m-%d"),
                      "$lte": END_DATE.strftime("%Y-%m-%d")}},
            {"date": 1, "appliance_type": 1, "daily_summary": 1, "_id": 0}
        ))
        generate_verification_report(existing_docs, pdf_data)
        return

    # ── Phase 1: Data Extraction & Reconstruction ──
    all_docs = []
    current_date = START_DATE
    day_num = 0

    while current_date <= END_DATE:
        day_num += 1
        is_first_day = current_date == START_DATE
        date_str = current_date.strftime("%Y-%m-%d")
        log.info("")
        log.info("━━━ Day %d: %s ━━━", day_num, date_str)

        # Source exclusively from MongoDB as requested
        # Skip CSV loading
        raw_df = load_mongo_for_date(db, current_date)
        source = "MongoDB"
        if raw_df is None:
            log.warning("  ⚠ No data found for %s in MongoDB. Skipping.", date_str)
            current_date += timedelta(days=1)
            continue

        log.info("  Source: %s | Raw rows: %d", source, len(raw_df))

        # Generate 10-minute grid
        grid = generate_10min_grid(current_date, is_first_day)
        log.info("  Grid: %d intervals (%s → %s)",
                 len(grid), grid[0].strftime("%H:%M"), grid[-1].strftime("%H:%M"))

        # Align to grid
        aligned = align_to_grid(raw_df, grid)
        if aligned.empty:
            log.warning("  ⚠ Alignment produced no data for %s. Skipping.", date_str)
            current_date += timedelta(days=1)
            continue

        # Data quality enforcement
        aligned = enforce_quality(aligned)

        # Build per-appliance documents
        for dev_name in DEVICES:
            doc = build_daily_document(current_date, dev_name, aligned, is_first_day)
            if doc:
                all_docs.append(doc)
                summary = doc["daily_summary"]
                log.info("  ✓ %s: %d readings, %.4f kWh, peak %.1f W",
                         dev_name, summary["total_readings"],
                         summary["total_kwh"], summary["peak_power_w"])
            else:
                log.warning("  ✗ %s: No data for this day", dev_name)

        current_date += timedelta(days=1)

    # ── Phase 2: Docling PDF Validation ──
    log.info("")
    log.info("━━━ PDF VALIDATION ━━━")
    pdf_data = extract_pdf_trendline(PDF_PATH)

    # ── Phase 3: Verification Report ──
    generate_verification_report(all_docs, pdf_data)

    # ── Phase 4: Database Write ──
    if mode == "execute":
        log.info("")
        log.info("━━━ DATABASE WRITE ━━━")
        collection = db["energybuckets"]

        # Delete existing documents in the recovery period first
        del_result = collection.delete_many({
            "date": {
                "$gte": START_DATE.strftime("%Y-%m-%d"),
                "$lte": END_DATE.strftime("%Y-%m-%d"),
            }
        })
        log.info("Deleted %d existing documents in recovery period", del_result.deleted_count)

        # Batch insert
        if all_docs:
            batch_size = 50
            for i in range(0, len(all_docs), batch_size):
                batch = all_docs[i:i + batch_size]
                collection.insert_many(batch)
                log.info("  Inserted batch %d–%d of %d",
                         i + 1, min(i + batch_size, len(all_docs)), len(all_docs))

            log.info("✅ Successfully inserted %d documents into energybuckets", len(all_docs))
        else:
            log.warning("No documents to insert!")

    elif mode == "dry-run":
        log.info("")
        log.info("━━━ DRY RUN COMPLETE ━━━")
        log.info("Would insert %d documents into energybuckets", len(all_docs))
        if all_docs:
            # Show a sample document (first one)
            sample = all_docs[0]
            log.info("Sample document:")
            log.info("  date: %s", sample["date"])
            log.info("  device_id: %s", sample["device_id"])
            log.info("  appliance_type: %s", sample["appliance_type"])
            log.info("  readings count: %d", len(sample["readings"]))
            if sample["readings"]:
                r = sample["readings"][0]
                log.info("  First reading:")
                log.info("    timestamp: %s", r["timestamp"])
                log.info("    interval_index: %d", r["interval_index"])
                log.info("    processed_data: %s", r["processed_data"])
                log.info("    weather: %s", r["weather"])
            log.info("  daily_summary: %s", sample["daily_summary"])

    client.close()
    log.info("Done.")


# ===================================================================
# CLI
# ===================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reconstruct energybuckets collection for Jan 3 – Feb 17, 2026"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Preview without writing to DB")
    group.add_argument("--execute", action="store_true", help="Write reconstructed data to DB")
    group.add_argument("--validate-only", action="store_true", help="Only run Docling PDF validation")

    args = parser.parse_args()

    if args.dry_run:
        run_pipeline("dry-run")
    elif args.execute:
        run_pipeline("execute")
    elif args.validate_only:
        run_pipeline("validate-only")
