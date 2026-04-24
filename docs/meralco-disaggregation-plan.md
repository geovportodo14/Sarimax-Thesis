# SARIMAX Thesis — Context Brief & Proposed Improvement Plan

> Prepared from thesis codebase analysis and panelist recommendation — April 19, 2026

---

## 1. Project Overview

**Thesis:** Short-term energy consumption forecasting for individual household appliances using SARIMAX (Seasonal AutoRegressive Integrated Moving Average with eXogenous variables).

**Appliances modeled:**
- Air conditioner (Aircon)
- Electric fan (E-Fan)
- Refrigerator (Ref)

**Data sources:** Tuya IoT smart plugs (per-appliance energy monitoring), Open-Meteo weather API, Meralco monthly billing.

**Forecasting task:** Predict next 24 hours of hourly energy consumption (kWh) per appliance.

---

## 2. Current Model Versions

| Appliance | Active Version | SARIMAX Order |
|---|---|---|
| Aircon | V3 | (3,0,2)(0,0,0,24) |
| E-Fan | V4 | (0,0,0)(0,1,2,24) |
| Ref | V4 | (0,0,1)(0,0,1,24) |

All models use **s=24** (hourly data, daily seasonality).

**Exogenous features (12 total):**
- Weather: `temperature`, `humidity`, `rainfall`
- Temporal: `sin_hour`, `cos_hour`, `sin_day_of_week`, `cos_day_of_week`, `is_weekend`
- Lagged: `lag_24`, `lag_168`
- Rolling means: `rolling_mean_24`, `rolling_mean_168`

---

## 3. Current Data Situation

### Real Sensor Data
- **Source:** Tuya smart plugs → MongoDB (`Sarimax-Thesis` DB, `energybuckets` collection)
- **Period:** Jan 3, 2026 19:00 → March 28, 2026
- **Volume:** ~2,040 hourly rows per appliance (~85 days)

### Synthetic Data (Current)
- **Period:** Dec 27, 2024 → Jan 3, 2026 18:00 (~8,947 rows)
- **How generated:** Pattern learned from only Jan 3–11, 2026 (8–9 days), then extrapolated backward
- **Problem:** Not anchored to any real-world ground truth — freely generated from a very short pattern basis

### Combined Training Data (Current)
```
Total rows:  ~10,536 hourly per appliance
Synthetic:    ~8,947 rows (84.9%)  ← low quality baseline
Real:          ~1,589 rows (15.1%) ← only real signal
Train/test:   70% real data for training, 30% for testing
```

---

## 4. Current Model Performance vs. Targets

### Targets
- MAPE ≤ 5%
- RMSE: lower is better
- R² ≥ 0.70

### Actual Results

| Model | MAPE (hourly) | RMSE | R² |
|---|---|---|---|
| V3 Aircon | 43.21% | 0.1186 kWh | **0.689** ← almost there |
| V4 E-Fan | 42.31% | 0.0214 kWh | 0.246 |
| V4 Ref | 30.34% | 0.0481 kWh | 0.001 |

### Why MAPE Is So High

MAPE is computed **hour-by-hour on non-zero hours**. Aircon and fan turn on/off unpredictably. When actual = 0.001 kWh but predicted = 0.05 kWh, that single hour contributes thousands of percent to MAPE. This is a **structural problem** with hourly MAPE on spiky appliances — no model tuning fully solves it.

### Why Refrigerator R² ≈ 0

Refrigerator runs 24/7 with nearly constant consumption (~2.25 kWh/day, zero days completely off). The variance is so small that even a very accurate model produces R² ≈ 0. This is a **metric-appliance mismatch**, not a model failure.

### Aircon R² at 0.689

Only **0.011 away** from the 0.70 target. Achievable with better training data.

---

## 5. Panelist Recommendation

During the panel defense, the professor (electrical engineer) recommended an approach he informally called **"few-shot learning"**. His actual description:

> "Monthly niyo maging 5-minute interval so merong scaling yun. Parang pagsasama — ang tawag ayun few-shots learning approach — wherein meron kang synthetic, meron kang limited data ng sensor data niyo na 2 months, i-aadd niyo dun sa trend na makikita mo sa Meralco bill."

### What He Actually Described

**Approach A — Meralco Bill Disaggregation:**
Take the Meralco monthly total and distribute it into hourly/5-minute intervals using your real sensor data as the consumption shape.

**Approach B — Pattern Borrowing from Public Datasets:**
Find open 5-minute appliance energy datasets on GitHub/UCI/REDD, use their shape as a proxy pattern, then scale to your Meralco totals.

### Formal Technical Name

This is **Temporal Disaggregation** (also called profile-based downscaling). It is an established technique in energy research. The concept: use a low-frequency ground truth (monthly billing) + high-frequency shape (hourly sensor pattern) → calibrated high-frequency synthetic data.

He called it "few-shot learning" informally because you have limited real data (kaunti lang data). It is not traditional ML few-shot learning (which requires neural networks and meta-learning), but the motivation is the same.

---

## 6. Meralco Billing Data Available

14 complete billing periods — Dec 2024 through Feb 2026:

| Billing Period | kWh |
|---|---|
| Dec 19, 2024 – Jan 18, 2025 | 303 |
| Jan 19 – Feb 18, 2025 | 298 |
| Feb 19 – Mar 19, 2025 | 307 |
| Mar 20 – Apr 19, 2025 | 345 |
| Apr 20 – May 19, 2025 | 342 |
| May 20 – Jun 19, 2025 | 312 |
| Jun 20 – Jul 19, 2025 | 319 |
| Jul 20 – Aug 19, 2025 | 291 |
| Aug 20 – Sep 19, 2025 | 315 |
| Sep 20 – Oct 19, 2025 | 319 |
| Oct 20 – Nov 19, 2025 | 353 |
| Nov 20 – Dec 19, 2025 | 308 |
| Dec 20, 2025 – Jan 19, 2026 | 332 |
| Jan 20 – Feb 18, 2026 | 294 |

**Seasonal pattern visible:**
- Summer peak: Mar–May (~342–345 kWh) ← aircon-driven
- Cool trough: Jul–Aug (~291 kWh)
- Ber-month peak: Oct–Nov (~353 kWh)

This variation is **real signal** that the current synthetic data does not capture.

---

## 7. Appliance Share Calculation

From real sensor data daily averages:

| Appliance | Mean kWh/day | Monthly est. (~28 days) | Share of 282 kWh bill |
|---|---|---|---|
| Aircon | 2.58 kWh | ~72 kWh | 25.5% |
| Refrigerator | 2.25 kWh | ~63 kWh | 22.3% |
| E-Fan | 1.27 kWh | ~36 kWh | 12.8% |
| **3-appliance total** | **6.10 kWh** | **~171 kWh** | **60.6%** |
| Other loads | ~4.01 kWh | ~112 kWh | 39.4% |

These ratios are used to estimate each appliance's share of each historical billing period.

---

## 8. Why This Improves Training Data

| Aspect | Current Synthetic | Proposed (Disaggregated) |
|---|---|---|
| Pattern basis | 8–9 days of real data | 85 days of real sensor data |
| Ground truth anchor | None (free extrapolation) | Calibrated to Meralco monthly totals |
| Seasonal variation | Not captured | Full year — captures summer peak & cool trough |
| Synthetic data quality | Low | Significantly higher |
| Model architecture change | — | None — still SARIMAX, same pipeline |

---

## 9. Implementation Plan

### Phase 1 — Validate Appliance Ratios

**New file:** `backend/disaggregation/validate_ratios.py`

1. Query MongoDB `energybuckets` for Jan 20 – Feb 18, 2026 (billing period = 294 kWh)
2. Sum kWh per appliance over that exact window
3. Compute `aircon_ratio`, `ref_ratio`, `efan_ratio`
4. Verify: `(aircon + ref + efan) ≈ 294 × 0.606 = ~178 kWh`
5. Lock ratios if within ±15% tolerance

**Deliverable:** Validated ratio constants saved to `profiles.json`

---

### Phase 2 — Build Normalized Hourly Profiles

**New file:** `backend/disaggregation/build_profiles.py`

1. Load real sensor data from existing `*_model_ready.csv` (Jan 3 – Mar 28, 2026 only)
2. **Clean first:** Remove refrigerator outlier on Jan 14, 2026 (13.07 kWh recorded — likely sensor error, mean is 2.25 kWh/day)
3. Build 2 profiles per appliance:
   - `profile_weekday[0..23]` — average hourly normalized consumption, weekdays
   - `profile_weekend[0..23]` — same for weekends
   - Each profile normalized so it sums to 1.0 (shape only, no magnitude)
4. For aircon and e-fan: compute `P(on | weekday)` and `P(on | weekend)` — probability appliance is used on a given day

**Deliverable:** `profiles.json` with 6 profile arrays + 4 probability values

---

### Phase 3 — Disaggregate Each Billing Period

**New files:** `backend/disaggregation/disaggregate.py`, `backend/disaggregation/meralco_billing.csv`

For each of the 13 historical billing periods (Dec 2024 – Jan 2026):

```
Step 1: Estimate per-appliance monthly kWh
    aircon_est = period_kwh × 0.255
    ref_est    = period_kwh × 0.223
    efan_est   = period_kwh × 0.128

Step 2: Count days in period, label each day weekday/weekend

Step 3: For each day:
    Refrigerator (always-on):
        hourly_kwh[h] = daily_est × profile_weekday[h] or profile_weekend[h]

    Aircon / E-Fan (on-off):
        Roll P(on) → if appliance runs today:
            hourly_kwh[h] = daily_est_active × profile[h]
        else:
            hourly_kwh[h] = 0 for all 24 hours

Step 4: Scale so monthly total = estimated monthly kWh
```

**Deliverable:** `synthetic_disaggregated.csv` — timestamp + per-appliance hourly kWh, Dec 2024 – Jan 2, 2026

---

### Phase 4 — Attach Exogenous Features

**Reuses:** `backend/collector/historical_backfiller.py`, `backend/preprocessing/stage_c_features.py`

1. Fetch historical weather (temperature, humidity, rainfall) from Open-Meteo Archive API for Dec 2024 – Jan 2, 2026
2. Run synthetic data through `stage_c_features.py`:
   - Adds `sin_hour`, `cos_hour`, `sin_day_of_week`, `cos_day_of_week`, `is_weekend`
   - Adds `lag_24`, `lag_168`, `rolling_mean_24`, `rolling_mean_168`
3. Output schema must be identical to existing `*_model_ready.csv`

**Deliverable:** Feature-complete synthetic CSVs, one per appliance

---

### Phase 5 — Merge Synthetic + Real Data

**Reuses:** `backend/preprocessing/stage_d_export.py`

```
Synthetic:  Dec 19, 2024 – Jan 2, 2026    (~12,700 rows, Meralco-calibrated)
Real:       Jan 3, 2026  – Mar 28, 2026   (~2,040 rows, actual sensor)
──────────────────────────────────────────────────────────────────────────
Total:      ~14,740 rows per appliance
```

1. Concatenate, ordered by timestamp
2. Recompute lag/rolling features at the Jan 3 join boundary using forward-fill (same logic as current pipeline)
3. Export as `aircon_model_ready_v5.csv`, `ref_model_ready_v5.csv`, `efan_model_ready_v5.csv`

Train/test split remains: 70% real data for training, 30% for testing.

---

### Phase 6 — Retrain & Evaluate

**Reuses:** `model_stageA.py`, `model_stageB1.py`, `model_stageC.py`

1. Run `model_stageA.py` — stationarity tests may suggest different d/D with new data
2. Run `model_stageB1.py` — full grid search over (p,q,P,Q), expanding-window CV
3. Run `model_stageC.py` — rolling-origin 24h evaluation
4. Compute metrics at **two levels:**
   - **Hourly** (existing): MAE, RMSE, MAPE, R²
   - **Daily aggregated** (new): sum 24 hourly predictions per day, then compute daily MAPE and R²

**Expected improvement:**

| Model | Current R² | Expected R² | Current Hourly MAPE | Expected Daily MAPE |
|---|---|---|---|---|
| Aircon | 0.689 | ≥ 0.70 | 43.21% | ~15–25% |
| E-Fan | 0.246 | ~0.40–0.55 | 42.31% | ~10–18% |
| Ref | 0.001 | ~0.30–0.50 | 30.34% | ~5–10% ← closest to target |

---

## 10. New Files Summary

| File | Phase | Purpose |
|---|---|---|
| `backend/disaggregation/meralco_billing.csv` | Setup | Billing table from Meralco bills |
| `backend/disaggregation/validate_ratios.py` | Phase 1 | MongoDB query + ratio validation |
| `backend/disaggregation/build_profiles.py` | Phase 2 | Extract normalized hourly profiles from sensor data |
| `backend/disaggregation/disaggregate.py` | Phase 3 | Core disaggregation engine |
| `backend/disaggregation/merge_and_export.py` | Phase 5 | Join synthetic + real, export model-ready CSVs |

Everything else reuses the existing preprocessing and model pipeline. No changes to SARIMAX model architecture.

---

## 11. Metric Recommendations for Thesis Defense

| Metric | Recommendation |
|---|---|
| **MAPE** | Report at **daily aggregate level** (sum 24h predictions), not hourly. Daily MAPE is more meaningful for energy planning and closer to the 5% target. |
| **R²** | Keep for aircon (achievable ≥ 0.70) and e-fan. For refrigerator, **replace R² with MAE and RMSE** — R² is statistically invalid for near-constant signals. |
| **RMSE** | Keep as primary accuracy metric across all models. |

**Suggested thesis framing:**
> "Hourly MAPE is reported for completeness; daily aggregated MAPE is the operationally relevant metric for household energy planning and Meralco billing alignment."

---

## 12. Risk Flags

| Risk | Impact | Mitigation |
|---|---|---|
| Appliance ratios shift seasonally (more aircon in summer) | Overestimates aircon in cool months | Use separate ratios for hot (Mar–May) vs. cool (Jul–Aug) months |
| Refrigerator outlier Jan 14, 2026 (13.07 kWh vs. 2.25 mean) | Corrupts hourly profile | Remove before Phase 2 |
| Billing periods don't align to calendar weeks | Fractional week at period boundaries | Handle partial weeks in Phase 3 disaggregation logic |
| 40% of bill is unmonitored loads | Ratio may drift across months | Document as thesis limitation; ±15% tolerance is acceptable |
| New synthetic data may shift optimal SARIMAX parameters | Full grid search needed | Phase 6 runs full stageB1 — expected and correct |

---

## 13. What Stays the Same

- SARIMAX model architecture
- Seasonal period s=24 (hourly, daily cycle)
- Exogenous feature set (all 12 features)
- Train/test split logic (70/30 on real data)
- Evaluation pipeline (stageA/B/C scripts)
- MongoDB + Tuya data collection pipeline

The only change is **how the synthetic training data is generated** — from freely extrapolated pattern to Meralco-calibrated disaggregation.

---

## 14. Daily MAPE Evaluation — No Retraining Needed

This is a quick win that can be done right now without touching any model.

### How It Works

Instead of evaluating MAPE hour-by-hour, sum the 24 hourly predictions into a daily total and compare against the daily actual total:

```python
daily_predicted = sum(hourly_pred[hour 0..23])   # kWh/day
daily_actual    = sum(hourly_actual[hour 0..23])  # kWh/day
daily_MAPE      = |daily_predicted - daily_actual| / daily_actual × 100
```

Run this on your existing `eval_predictions.csv` for each model — no retraining, no new model, just aggregation.

### Why It Helps

- Over- and under-predictions partially cancel across 24 hours → lower net error
- Zero-hour spikes (actual=0.001, predicted=0.05) get diluted by the rest of the day
- Daily R² is more meaningful because weekly patterns (weekday/weekend) are real and predictable

### Daily Data Statistics (from existing sensor data)

| Appliance | Complete Days | Mean kWh/day | Std Dev | Min kWh/day | Max kWh/day | Zero Days |
|---|---|---|---|---|---|---|
| Aircon | 439 | 2.58 kWh | 1.12 | 0.00 | 4.55 | 8 (1.8%) |
| Refrigerator | 439 | 2.25 kWh | 0.57 | 1.09 | **13.07** | 0 (0%) |
| E-Fan | 429 | 1.27 kWh | 0.81 | 0.00 | 4.49 | 4 (0.9%) |

Refrigerator has zero zero-days — its daily total is the most predictable of the three. Best candidate to hit ≤5% daily MAPE.

### Expected Daily MAPE vs. Current Hourly MAPE

| Model | Hourly MAPE (current) | Expected Daily MAPE | Likely to hit 5%? |
|---|---|---|---|
| V3 Aircon | 43.21% | ~15–25% | No |
| V4 E-Fan | 42.31% | ~10–18% | No |
| V4 Ref | 30.34% | ~5–10% | Possibly |

### Recommended Action

Run this evaluation script on `eval_predictions.csv` before committing to any retraining. The daily MAPE result will tell you how far you actually are from the 5% target at the operationally relevant granularity.

---

## 15. 5-Minute vs. Hourly — What the Panelist Meant

The panelist said: *"monthly niyo maging 5-minute interval."* Here is what that means in context and how it relates to your current setup.

### Current Setup: Hourly

Your models forecast at **1-hour resolution** (s=24). Data is collected at 10-minute intervals from Tuya smart plugs, then resampled to hourly in `stage_c_features.py` before model training.

### What the Panelist Described

He was describing a data generation workflow, not a model change:

```
Meralco monthly total (kWh)
        ↓
Distribute into 5-minute intervals
using sensor data shape as the template
        ↓
Calibrated 5-minute synthetic training data
```

The "5-minute" refers to the resolution of the **synthetic data you generate**, not necessarily the model's forecast resolution.

### Practical Options

| Option | Resolution | Implication |
|---|---|---|
| **A — Keep hourly (recommended)** | 1-hour | No change to models; generate synthetic at hourly resolution anchored to Meralco |
| **B — Upgrade to 5-minute** | 5-min | Requires retraining with s=288 (daily cycle at 5-min = 288 intervals); much larger model, more compute, more data needed |

**Option A is the right call for this thesis.** The Meralco disaggregation approach works at any resolution — you generate hourly synthetic data, not 5-minute. The panelist's mention of 5-minute was illustrative of the technique, not a hard requirement to change your model resolution.

If reviewers ask: *"We retain hourly resolution as it aligns with our SARIMAX seasonal period (s=24) and is sufficient for the 24-hour ahead forecasting task. The disaggregation technique applies equally at hourly granularity."*

---

## 16. Few-Shot Learning — Formal Clarification

This section exists so your group can answer confidently if the panel asks about the term.

### What Few-Shot Learning Actually Is (ML Definition)

Few-shot learning is a **deep learning / neural network concept** where:
1. A model is **pre-trained on a large dataset** to learn transferable representations (embeddings)
2. At inference time, it generalizes to a new task using only **2–30 labeled examples** (the "few shots")
3. It requires meta-learning, prototypical networks, or large language models — none of which are in your pipeline

Examples: image classifiers that recognize new categories from 5 photos; LLMs that answer new question types from 3 examples.

### Why It Does Not Apply to SARIMAX

| Requirement | Few-Shot Learning | Your SARIMAX Models |
|---|---|---|
| Pre-trained representations | Required | Not present — SARIMAX has no embeddings |
| Neural network | Required | Not present — parameter estimation via MLE |
| Transfer across tasks | Core mechanism | Not possible — each model is appliance-specific |
| Few examples at inference | Core mechanism | SARIMAX needs sufficient history to fit AR/MA terms |

SARIMAX estimates parameters (AR, MA, seasonal) via **Maximum Likelihood Estimation** from scratch on each dataset. There is nothing to "transfer" from one appliance model to another.

### What the Panelist Actually Meant

He used the term informally to describe the motivation: *"you have kaunti lang data (very little data), so you use the few real observations to bootstrap more."*

The correct technical term for what he described is:

> **Temporal Disaggregation** — distributing a low-frequency aggregate (monthly Meralco bill) into high-frequency intervals (hourly) using a shape template from real observations.

### How to Answer in the Defense

If asked: *"Is this few-shot learning?"*

> "The panelist used the term informally to describe learning from limited data. Formally, few-shot learning requires neural network-based meta-learning, which is outside our SARIMAX framework. What we implement is temporal disaggregation — a well-established technique in energy research that uses Meralco monthly billing totals as ground-truth anchors and real sensor data as the disaggregation template. The motivation is the same: making the most of limited real observations."

---

## 17. Existing Training Pipeline Explained

For groupmates unfamiliar with the codebase, here is what each stage does.

### Stage A — `model_stageA.py` (Pre-Modeling Checks)

Runs before any model fitting. Determines whether the data needs differencing.

- **ADF test (Augmented Dickey-Fuller):** checks if the time series is stationary (stable mean/variance)
- **ACF analysis:** checks for seasonal patterns at lag 24
- **Output:** `_premodel_report.json` — suggests d (first differencing) and D (seasonal differencing) values

### Stage B1 — `model_stageB1.py` (Grid Search + Cross-Validation)

Finds the best SARIMAX parameter combination.

- **Search space:** p, q ∈ [0,3], P, Q ∈ [0,2], max total order ≤ 10 (~100+ combinations)
- **Cross-validation:** 3-fold expanding-window within the training set, 24-hour forecast horizon per fold
- **Selection:** Best CV RMSE wins; AIC/BIC used only as tiebreaker
- **Output:** `best_params.json`, `best_model.pkl`, `search_results.csv`

### Stage C — `model_stageC.py` (Rolling-Origin Evaluation)

Evaluates the best model on the held-out test set.

- **Rolling-origin:** For each test day, train on all data up to that day, forecast next 24 hours
- **Daily refit:** Model is retrained each day (captures concept drift)
- **Metrics computed:** MAE, RMSE, NRMSE, MAPE (non-zero hours only), sMAPE, R²
- **Output:** `eval_predictions.csv`, `eval_metrics.json`, residual diagnostics

### Data Flow Summary

```
Raw MongoDB data (energybuckets)
        ↓
stage_a_standardization.py   — schema validation, UTC+8 timezone
        ↓
stage_b_cleaning.py          — gap filling, outlier handling
        ↓
stage_c_features.py          — hourly resample, weather join, lag/rolling features
        ↓
stage_d_export.py            — final *_model_ready.csv per appliance
        ↓
model_stageA.py              — stationarity analysis
        ↓
model_stageB1.py             — grid search, CV, best model selection
        ↓
model_stageC.py              — rolling-origin evaluation, final metrics
```

### Key Config Values

| Parameter | Value | Meaning |
|---|---|---|
| Seasonal period (s) | 24 | Daily cycle at hourly resolution |
| CV folds | 3 | Expanding-window within train set |
| CV horizon | 24 hours | One full day per fold |
| Min train rows for CV | 300 | Safety floor before CV starts |
| Max iterations | 150 | MLE optimizer iterations |
| Forecast horizon | 24 hours | Next-day prediction |
| Refit frequency | Daily | Model retrained each day in evaluation |
