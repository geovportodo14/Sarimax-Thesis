# `add_ele` Scaling Factor Analysis Report

## Summary

**There is a critical inconsistency in the `add_ele` (cumulative energy) scaling across the codebase.**

| Source | Scaling Factor | `add_ele=41` → kWh |
|--------|---------------|---------------------|
| **Tuya Cloud Spec** | ÷ 1000 (multiple: 3) | 0.041 kWh |
| **preprocessor.py** (current live code) | ÷ 1000 | 0.041 kWh |
| **refined_csv_migrator.py** (historical data generator) | ÷ 100 (writes: `kwh × 100`) | 0.41 kWh |
| **verify_mongo_revert.py** (verification script) | ÷ 100 | 0.41 kWh |
| **TH2_Mongo_Extractor.py** (pipeline export) | ÷ 1000 (writes: `kwh × 1000`) | 0.041 kWh |
| **All stored MongoDB data** | ÷ 100 (observed) | 0.41 kWh |
| **All reconstructed CSVs** | ÷ 100 (observed) | 0.41 kWh |

---

## 1. Tuya Cloud Specification

From the Tuya IoT Platform documentation for the smart plug's `add_ele` data point:

```
DP Code: add_ele (Increase power)
Type:    value
Range:   0 to 50000
Interval: 100
Multiple: 3
Unit:    kWh
```

**"Multiple: 3" means the raw integer value must be divided by 10³ = 1000 to obtain kWh.**

This is consistent with other Tuya data points:
| DP Code | Multiple | Divisor | Example |
|---------|----------|---------|---------|
| `cur_voltage` | 1 | 10¹ = 10 | 2349 → 234.9 V |
| `cur_current` | 3 | 10³ = 1000 | 1727 → 1.727 A |
| `cur_power` | 1 | 10¹ = 10 | 3988 → 398.8 W |
| **`add_ele`** | **3** | **10³ = 1000** | **41 → 0.041 kWh** |

---

## 2. What the Code Currently Does

### 2.1 `backend/collector/utils/preprocessor.py` (Live Data Collector)
```python
kwh_raw = raw_status.get("add_ele", 0)
kwh = float(kwh_raw) / 1000.0   # ← Divides by 1000 (matches Tuya spec)
```
**Uses ÷ 1000** ✅ Matches Tuya spec

### 2.2 `backend/collector/refined_csv_migrator.py` (Historical Data Generator)
```python
"add_ele": int(accumulated_kwh * 100)   # ← Multiplies by 100 (inverse = ÷ 100)
```
**Uses ÷ 100** ❌ Does NOT match Tuya spec

### 2.3 `backend/verify_mongo_revert.py` (Verification Script)
```python
expected = float(add_ele) / 100.0   # ← Divides by 100
# Prints: "SUCCESS: total_kwh_accumulated matches raw/100"
```
**Uses ÷ 100** ❌ Does NOT match Tuya spec

### 2.4 `backend/preprocessing/TH2_Mongo_Extractor.py` (Pipeline Export)
```python
kwh_raw = round(kwh_total * 1000)   # ← Multiplies by 1000 (inverse = ÷ 1000)
```
**Uses ÷ 1000** ✅ Matches Tuya spec

---

## 3. What the Stored Data Shows

### 3.1 MongoDB (energybuckets collection)
From the electric fan data:
```
raw_data: { add_ele: 16 }
processed_data: { total_kwh_accumulated: 0.16 }
```
**16 / 100 = 0.16** → Data was stored using ÷ 100

### 3.2 Reconstructed CSVs
```csv
add_ele,kwh
41,0.41      # aircon: 41/100 = 0.41
65,0.65      # refrigerator: 65/100 = 0.65
21,0.21      # electric_fan: 21/100 = 0.21
```
**All reconstructed data uses ÷ 100**

### 3.3 Archive Energy Logs
```csv
2026-03-10 09:20:00,Aircon,add_ele,1
2026-03-10 09:20:00,Refrigerator,add_ele,81
2026-03-10 09:20:00,Electric_Fan,add_ele,6
```
These raw values are very small integers, suggesting they may have already been divided by 100 before storage.

---

## 4. What the Thesis Paper Says

### Table 3.6 (Both V1 and V2 — identical)
```
| timestamp            | voltage_raw | current_raw | power_raw | kwh_raw | voltage_v | current_a | power_w | kwh_total | pf   |
|----------------------|-------------|-------------|-----------|---------|-----------|-----------|---------|-----------|------|
| 2025-10-17 08:00:00  | 228.5       | 0.31        | 70.8      | 0.024   | 228.5     | 0.31      | 70.8    | 0.024     | 0.92 |
| 2025-10-17 08:10:00  | 227.9       | 0.29        | 66        | 0.036   | 227.9     | 0.29      | 66      | 0.036     | 0.91 |
| 2025-10-17 08:20:00  | 229.3       | 0.32        | 72.5      | 0.048   | 229.3     | 0.32      | 72.5    | 0.048     | 0.92 |
```

**Key observation:** In Table 3.6, `voltage_raw = voltage_v`, `kwh_raw = kwh_total`. The thesis states: *"For the sample dataset in Table 3.6, the readings are already in scaled engineering units."*

This means the thesis presents the data AFTER the logger has already converted raw Tuya integers to engineering units. The table does NOT show the actual raw integer values from the Tuya API (which would be like `cur_voltage: 2285`, `add_ele: 24`, etc.).

The thesis does NOT explicitly state whether `add_ele` is divided by 100 or 1000. It only says: *"The general scaling relation is applied depending on the scale factor assigned to each parameter based on TUYA's specifications."*

---

## 5. Cross-Validation with Tuya Smart App

From the Tuya Smart app screenshots (docling_extraction.md), daily electricity usage values for the aircon include:
- 2.97 kWh, 7.16 kWh, 6.53 kWh, 5.79 kWh, 4.63 kWh, etc.

For an aircon running at ~400W for ~18 hours/day: `0.4 kW × 18h = 7.2 kWh/day` — this matches the app values.

**If using ÷ 100:** A daily `add_ele` change of ~716 units → 7.16 kWh ✓
**If using ÷ 1000:** A daily `add_ele` change of ~7160 units → 7.16 kWh ✓

Both are plausible given the Tuya spec range of 0–50000. However, the "interval: 100" in the spec means the value increments in steps of 100, which would make values like 7160 impossible (not a multiple of 100). A daily change of 716 is also not a multiple of 100.

**Re-interpretation:** "Interval: 100" likely means the minimum reportable increment is 100 units. With ÷ 1000, that's 0.1 kWh minimum increment. With ÷ 100, that's 1.0 kWh minimum increment. Since the app shows values like 2.97 kWh (not a whole number), **÷ 1000 with interval 100 (= 0.1 kWh steps) is more consistent** with the app display.

---

## 6. Conclusion & Recommendation

### The Correct Scaling Factor is ÷ 1000 (per Tuya specification)

Based on the Tuya Cloud documentation (`multiple: 3` = divide by 10³ = 1000), **the correct conversion is:**

```
kWh = add_ele / 1000
```

### The Problem

**All historical data in the system was stored using ÷ 100, making all `total_kwh_accumulated` values 10× too high.**

| Component | Current Factor | Correct Factor | Status |
|-----------|---------------|----------------|--------|
| `preprocessor.py` | ÷ 1000 | ÷ 1000 | ✅ Correct |
| `TH2_Mongo_Extractor.py` | ÷ 1000 | ÷ 1000 | ✅ Correct |
| `refined_csv_migrator.py` | ÷ 100 | ÷ 1000 | ❌ **Needs fix** |
| `verify_mongo_revert.py` | ÷ 100 | ÷ 1000 | ❌ **Needs fix** |
| All stored MongoDB data | ÷ 100 | ÷ 1000 | ❌ **All kWh values are 10× too high** |
| All reconstructed CSVs | ÷ 100 | ÷ 1000 | ❌ **All kWh values are 10× too high** |

### Recommended Actions

1. **Fix `refined_csv_migrator.py`:** Change `int(accumulated_kwh * 100)` → `int(accumulated_kwh * 1000)`
2. **Fix `verify_mongo_revert.py`:** Change `float(add_ele)/100.0` → `float(add_ele)/1000.0`
3. **Re-evaluate all stored data:** All `total_kwh_accumulated` values in MongoDB need to be divided by 10 to correct the 10× overestimation
4. **Re-evaluate reconstructed CSVs:** All `kwh` columns need to be divided by 10
5. **Update thesis Table 3.6:** Clarify that `kwh_raw` contains the post-conversion value, or show the actual raw Tuya integer values with the scaling formula

### Impact on SARIMAX Model

If the kWh values used for training the SARIMAX model are 10× too high, the model's forecasts will also be 10× too high. However, since the error is systematic (all values are scaled by the same factor), the **relative patterns and trends remain valid** — only the absolute magnitude is wrong. The model can be corrected by applying a ÷ 10 factor to all forecasted values, or by retraining with corrected data.
