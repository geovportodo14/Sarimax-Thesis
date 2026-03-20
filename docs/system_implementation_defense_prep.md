# System Implementation Defense Prep (Section 3.6)

This guide is for your oral defense of **Section 3.6 System Implementation** in `TH1 SARIMAX V2.md`.
It is aligned with your actual running pipeline and saved outputs.

## 1) 60-Second Defense Version

You can say this almost verbatim:

"Our system implementation converts appliance-level SARIMAX forecasts into actionable household decisions. The pipeline runs daily after data collection, loads per-appliance history, builds exogenous features such as calendar, lag, rolling means, and weather, then generates 24-hour forecasts per appliance. Next, we translate predicted kWh to peso cost, evaluate budget utilization, and classify status as within-budget, warning, or over-budget. We then apply a post-forecast MILP scheduler that suggests ON/OFF schedules under budget and time-window constraints, especially for schedulable loads like aircon and electric fan, while keeping refrigerator continuous. Finally, outputs are persisted to CSV/JSON and MongoDB, then surfaced in the web dashboard and alert channels as forecast totals, top-consuming appliances, budget status, and recommended schedule."

## 2) 5-Minute Technical Flow (Panel-Friendly)

Use this sequence:

1. **Entry point and timing**
The orchestrator is `backend/forecasting/run_pipeline.py`.
It is designed for daily execution after fresh actual data is available.

2. **Input layer**
Per appliance, the system first tries MongoDB historical data and falls back to CSV history if needed.
Appliances: `aircon`, `electric_fan`, `refrigerator`.

3. **Feature construction**
Future exogenous variables are built using:
- calendar features (`sin_hour`, `cos_hour`, weekday signals),
- lag features (`lag_24`, `lag_168`) from historical actuals,
- rolling means (`24h`, `168h`),
- weather (temperature, humidity, rainfall) from Open-Meteo with fallback.

4. **Forecasting**
Each appliance loads its trained SARIMAX model (`best_model.pkl`) and parameters (`best_params.json`), then performs `get_forecast(steps=24)`.
Predictions are clipped at zero to enforce non-negative energy.

5. **Cost and budget logic**
Predicted kWh are converted to cost and aggregated by appliance and day.
Budget status logic:
- `within_budget` if utilization < 0.90
- `warning` if utilization >= 0.90 and <= 1.00
- `over_budget` if utilization > 1.00

6. **MILP optimization layer**
A binary ON/OFF MILP scheduler runs after forecasting.
Key constraints:
- hard budget cap,
- allowed hour windows (night-focused for aircon/fan),
- refrigerator treated as non-schedulable continuous load.
Output includes optimized cost, savings, and readable time blocks.

7. **Output artifacts and integration**
The run saves:
- per-appliance forecast CSV,
- `_run_manifest.json`,
- `_recommendation.json`,
- `_schedule.json`,
- `optimized_schedule.csv`.
Dashboard controllers then read these artifacts and DB records for visualization and API responses.

## 3) Concrete Evidence You Can Present (From Actual Runs)

### A. Forecast date 2026-03-20
Source files:
- `backend/forecasting/outputs/2026-03-20/_run_manifest.json`
- `backend/forecasting/outputs/2026-03-20/_recommendation.json`
- `backend/forecasting/outputs/2026-03-20/_schedule.json`

Highlights:
- Daily predicted cost: **PHP 65.8693**
- Budget: **PHP 200.00**
- Utilization: **0.3293** (`within_budget`)
- Top cost contributor: **Aircon PHP 36.129** (~55%)
- Scheduler baseline cost: **PHP 62.8736**
- Scheduler optimized cost: **PHP 48.4914**
- Estimated savings: **PHP 14.3822 (22.87%)**
- Recommended schedule includes:
  - Aircon: `12 AM–6 AM, 6 PM–midnight`
  - Electric fan: `12 AM–6 AM, 8 PM–midnight`
  - Refrigerator: `Continuous operation`

### B. Forecast date 2026-03-21
Source files:
- `backend/forecasting/outputs/2026-03-21/_recommendation.json`
- `backend/forecasting/outputs/2026-03-21/_schedule.json`

Highlights:
- Daily predicted cost: **PHP 53.1221**
- Status: `within_budget`
- Top cost contributor: **Refrigerator PHP 27.451**
- Optimized savings: **PHP 1.439 (2.94%)**

### C. Operational reliability snapshot (March 1-21, 2026)
From run manifests in `backend/forecasting/outputs/2026-03-*/_run_manifest.json`:
- Total daily runs checked: **21**
- Full-success runs (`ok=3, failed=0`): **19**
- Partial-failure runs: **2** (dates: `2026-03-10`, `2026-03-19`)
- Recorded root cause of partial failures: missing dependency `pyarrow` for electric fan model deserialization.

Use this as a strong point:
"The system degrades gracefully: even with one appliance failure, remaining appliances and recommendation outputs were still produced."

## 4) File-to-Function Mapping (Good for Technical Questions)

- Core orchestration: `backend/forecasting/run_pipeline.py`
- Config and policies: `backend/forecasting/config.py`
- Future exog builder: `backend/forecasting/pipeline/features.py`
- Weather fetch/fallback: `backend/forecasting/pipeline/weather.py`
- SARIMAX forecasting: `backend/forecasting/pipeline/forecaster.py`
- Budget recommendation: `backend/forecasting/pipeline/recommender.py`
- MILP scheduling: `backend/forecasting/pipeline/scheduler.py`
- Artifact persistence: `backend/forecasting/pipeline/storage.py`
- API serving forecast artifacts:
  - `backend/controllers/dailyForecastsController.js`
  - `backend/controllers/liveForecastController.js`
  - `backend/routes/api.js`

## 5) Likely Panel Questions and Suggested Answers

1. **Why SARIMAX instead of deep learning?**
SARIMAX is interpretable, data-efficient for limited household data, and directly supports exogenous variables (weather and temporal features), which matches our research objective of explainable appliance-level forecasting.

2. **Why 24-hour horizon?**
It matches day-ahead planning and household decision cycles (budgeting and appliance use planning per day), while keeping forecast uncertainty manageable.

3. **How do you avoid data leakage?**
Lag and rolling features are computed only from historical observed data. Forecast exogenous features are prepared per future timestamp before inference, without using future target values.

4. **What if weather API fails?**
The system falls back to recent historical weather values (forward-fill) so forecasting still proceeds.

5. **How is budget status computed?**
Utilization = predicted cost / daily budget.
Thresholds are deterministic: `<0.90`, `0.90-1.00`, and `>1.00`.

6. **How do you validate deployment quality?**
We compare model metrics (MAE/RMSE/MAPE/R2), residual diagnostics, and baseline comparisons. The repository includes a backtest-vs-baseline evaluation script (`eval_backtest_vs_baseline.py`).

7. **Why can recommendation cost and scheduler baseline cost differ?**
Recommendation uses base tariff multiplication, while scheduler uses time-of-use hourly multipliers for optimization. They serve related but different layers (budget messaging vs. optimization objective).

8. **What are current implementation limitations?**
Observed partial failures were dependency-related (`pyarrow`). Also, residual diagnostics indicate remaining autocorrelation, so additional model refinement is an identified future improvement area.

## 6) Fast Thesis Cleanup Before Defense (Recommended)

Your current Section 3.6 is strong conceptually, but clean these for consistency:

1. **Fix equation formatting in 3.6.1 and 3.6.2**
Current equations are hard to read. Rewrite in proper notation:
- `Cost_{a,h} = \hat{E}_{a,h} * Tariff_h`
- `DailyCost_a = sum_{h=1}^{24} Cost_{a,h}`
- `ProjectedTotal = sum_a DailyCost_a`
- `Utilization = ProjectedTotal / Budget`

2. **Align tariff description with implementation**
Text currently says monthly-mapped tariff.
Implementation currently uses base tariff with hourly TOU multipliers in scheduling.
State this explicitly to avoid panel mismatch.

3. **Clarify status logic exactly as implemented**
State explicit thresholds (`<90%`, `90-100%`, `>100%`).

4. **Clarify resilience behavior**
Mention that per-appliance failures are logged in run manifest and do not always block all outputs.

## 7) Suggested Closing Line in Defense

"Section 3.6 demonstrates that our contribution is not only a predictive model but an operational decision-support system: it transforms hourly appliance forecasts into cost-aware, budget-aware, and schedule-aware actions that users can actually apply."
