import pandas as pd
from pathlib import Path

# folders
INPUT_DIR = Path("model_ready")
OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==============================
# CONFIG (choose your mode here)
# ==============================

START_DATE = None  # or None
END_DATE = pd.Timestamp("2026-03-08 23:00:00")    # or None

# Examples:
# START_DATE = None
# END_DATE = pd.Timestamp("2026-03-08 23:00:00")

# START_DATE = pd.Timestamp("2026-01-10 19:00:00")
# END_DATE = None

# ==============================
# PROCESS
# ==============================

for csv_file in INPUT_DIR.glob("*.csv"):
    
    # read file
    df = pd.read_csv(csv_file, parse_dates=["timestamp"])

    # apply filtering based on config
    if START_DATE is not None and END_DATE is not None:
        df_filtered = df[
            (df["timestamp"] >= START_DATE) &
            (df["timestamp"] <= END_DATE)
        ]

    elif START_DATE is not None:
        df_filtered = df[df["timestamp"] >= START_DATE]

    elif END_DATE is not None:
        df_filtered = df[df["timestamp"] <= END_DATE]

    else:
        df_filtered = df.copy()  # no filtering

    # output path
    out_path = OUTPUT_DIR / csv_file.name
    
    # save filtered dataset
    df_filtered.to_csv(out_path, index=False)

    print(f"Processed: {csv_file.name} → {out_path} ({len(df_filtered)} rows)")