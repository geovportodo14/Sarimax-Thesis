
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")

# --- Copied Functions from TimeGan.py ---

def parse_value_to_float(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, str):
        s = x.strip()
        if s.lower() == "true":
            return 1.0
        if s.lower() == "false":
            return 0.0
        try:
            return float(s)
        except Exception:
            return np.nan
    try:
        return float(x)
    except Exception:
        return np.nan

def long_to_wide(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp")

    if not {"device", "property", "value"}.issubset(df.columns):
        raise ValueError("CSV must contain: timestamp, device, property, value")

    df["key"] = df["device"].astype(str) + "__" + df["property"].astype(str)
    df["value_num"] = df["value"].apply(parse_value_to_float)

    wide = (
        df.pivot_table(index="timestamp", columns="key", values="value_num", aggfunc="last")
        .sort_index()
    )
    return wide

def resample_fixed(wide: pd.DataFrame, freq: str) -> pd.DataFrame:
    out = wide.resample(freq).mean()
    out = out.ffill().bfill()
    out = out.fillna(0.0)
    return out

def build_daily_sequences(X: np.ndarray, seq_len: int) -> np.ndarray:
    if X.shape[0] < seq_len:
        raise ValueError("Not enough points to form even one daily sequence.")

    n_days = X.shape[0] // seq_len
    X = X[: n_days * seq_len]
    return X.reshape(n_days, seq_len, X.shape[1]).astype(np.float32)

# --- Tests ---

def test_parse_value():
    assert parse_value_to_float("True") == 1.0
    assert parse_value_to_float("False") == 0.0
    assert parse_value_to_float("123.45") == 123.45
    assert np.isnan(parse_value_to_float("abc"))
    print("test_parse_value: PASSED")

def test_long_to_wide():
    data = {
        "timestamp": ["2026-01-01 10:00:00", "2026-01-01 10:00:00", "2026-01-01 10:10:00"],
        "device": ["DevA", "DevA", "DevA"],
        "property": ["prop1", "prop2", "prop1"],
        "value": ["10", "20", "15"]
    }
    df = pd.DataFrame(data)
    wide = long_to_wide(df)
    
    assert "DevA__prop1" in wide.columns
    assert "DevA__prop2" in wide.columns
    assert wide.shape == (2, 2)
    assert wide.loc["2026-01-01 10:00:00", "DevA__prop1"] == 10.0
    print("test_long_to_wide: PASSED")

def test_resample_fixed():
    dates = pd.date_range("2026-01-01 10:00:00", periods=3, freq="20min") # Gap of 20 mins
    df = pd.DataFrame({"val": [1, 2, 3]}, index=dates)
    
    # Resample to 10min, should fill gaps
    resampled = resample_fixed(df, "10min")
    
    # Expected: 10:00->1, 10:10->(filled), 10:20->2 ...
    # 0    10:00   1
    # 1    10:10   NaN -> ffill -> 1
    # 2    10:20   2
    assert len(resampled) == 5 # 00, 10, 20, 30, 40
    assert resampled.iloc[1]["val"] == 1.0 
    print("test_resample_fixed: PASSED")

def test_build_sequences():
    # 2 days of data at 10min freq = 144 * 2 points
    # 3 features
    N_POINTS = 144 * 2 + 50 # +50 extra should be dropped
    X = np.random.rand(N_POINTS, 3)
    
    seqs = build_daily_sequences(X, seq_len=144)
    
    assert seqs.shape == (2, 144, 3)
    print("test_build_sequences: PASSED")

if __name__ == "__main__":
    test_parse_value()
    test_long_to_wide()
    test_resample_fixed()
    test_build_sequences()
    print("\nSTAGE 1: All Data Loading Tests Passed!")
