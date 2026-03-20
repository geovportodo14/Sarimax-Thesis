# Full Defense Timed Flow (Based on Your Sequence)

Use this as your speaking guide.
Target duration: **14:00 to 14:30** depending on your Revision Recap length.

## 1) Master Timeline

- `0:00-3:00` Background, Problem, Objectives, Importance
- `3:00-3:30` Revision Recap (short version)  
or `3:00-4:00` Revision Recap (full 1-minute version)
- `3:30/4:00-4:00/4:30` Conceptual Framework
- `4:00/4:30-8:30/9:00` Methods  
  - Preprocessing `0:30`  
  - Synthetic `1:00`  
  - Modeling `1:00`  
  - Optimization `1:00`  
  - System Implementation `1:00`
- `8:30/9:00-11:00/11:30` Results (5 objectives, 30 sec each)
- `11:00/11:30-12:30/13:00` General Results, Conclusion, Recommendation
- `12:30/13:00-14:30/15:00` Prototype (2 minutes)

## 2) Script Per Section

## A. Background / Problem / Objectives / Importance (3:00 max)

Say this:

"Household electricity users usually only see total monthly cost, not appliance-level future cost. Our study addresses this by combining low-cost Tuya smart sockets, data reconstruction, SARIMAX forecasting, and budget-aware recommendations.  
The problem is how to convert raw appliance readings into actionable day-ahead decisions: what will consume most, how much it will cost, and whether budget exceedance is likely.  
Our general objective is to implement a low-cost monitoring and forecasting system with budget tracking and cost estimation.  
Our specific objectives are: monitoring and dashboarding, synthetic data reconstruction, hourly forecasting and cost estimation, and budget alerting.  
The importance is practical and academic: homeowners gain forecast-based control, while researchers get a replicable appliance-level pipeline for Philippine household conditions."

## B. Revision Recap (0:30 to 1:00)

Short version (30 sec):

"In the revised manuscript, we clarified the end-to-end implementation flow, aligned model and system outputs, strengthened validation discussion, and made the implementation section more operational by specifying artifacts, scheduling logic, and alert behavior."

Full version (1 min):

"Compared to earlier drafts, the revision now emphasizes full system operation, not only model training. We clarified preprocessing-to-forecast-to-cost-to-alert flow, tightened methodology language, and connected implementation outputs to actual artifacts such as run manifest, recommendation JSON, and schedule JSON. We also improved consistency in budget logic, execution schedule, and prototype explanation so defense discussion can trace each output back to a concrete processing step."

## C. Conceptual Framework (0:30)

Say this:

"Our conceptual framework follows an IPO structure. Inputs are smart plug data, weather data, appliance metadata, and tariff data. The process includes preprocessing, synthetic reconstruction, SARIMAX forecasting, optimization, and budget evaluation. Outputs are dashboard insights and mobile notifications showing projected kWh, projected cost, top-consuming appliance, and budget status."

## D. Methods (4:30 total)

### D1. Preprocessing (0:30)

"We cleaned and validated high-frequency appliance data, aligned timestamps, handled missing values, and engineered time-based and lag-based features. The goal is to ensure physically consistent, modeling-ready hourly series."

### D2. Synthetic (1:00)

"Because real high-frequency history was limited, we used Improved TimeGAN to reconstruct missing historical months. Synthetic outputs were validated and aligned with billing context, then merged with real data to form a longer, seasonally meaningful training window."

### D3. Modeling (1:00)

"We used SARIMAX per appliance with exogenous features such as weather and temporal variables. Forecasting is day-ahead with a 24-hour horizon. We evaluated performance using MAE, RMSE, MAPE/sMAPE, and R², plus residual diagnostics."

### D4. Optimization (1:00)

"After forecasting, we apply a post-forecast MILP scheduler. It uses budget constraints and time-window rules to produce ON/OFF recommendations for schedulable appliances while keeping refrigerator continuous. This translates prediction into cost-saving actions."

### D5. System Implementation (1:00)

"The deployed pipeline runs daily, loads latest history, builds future exogenous features, generates per-appliance forecasts, translates kWh to cost, computes budget status, then stores outputs for dashboard and alerts. Main artifacts include hourly forecast CSVs, run manifest, recommendation summary, and optimized schedule."

## E. Results (5 objectives, 30 sec each = 2:30)

Use this 5-objective framing (defense-friendly):

### Objective 1: Monitoring implementation
"We successfully implemented appliance-level monitoring and dashboard-ready outputs for aircon, electric fan, and refrigerator. The system captures and organizes data per appliance, enabling visibility beyond total household usage."

### Objective 2: Synthetic reconstruction
"We generated extended historical sequences using Improved TimeGAN to address limited real monitoring history. This enabled year-scale seasonal modeling instead of relying only on short real collection windows."

### Objective 3: Forecasting performance
"The SARIMAX models produced operationally usable day-ahead forecasts across appliances, with model-vs-baseline checks passing in our evaluation script outputs."

### Objective 4: Cost estimation and budget status
"Forecasted kWh were translated into projected cost and budget utilization. For example, on 2026-03-20, predicted cost was PHP 65.87 against PHP 200 budget, classified as within budget."

### Objective 5: Actionable optimization and recommendations
"The optimization layer generated concrete schedule recommendations. On 2026-03-20, optimized schedule estimated PHP 14.38 savings from baseline cost projection, demonstrating decision-support value beyond raw prediction."

If panel asks why 5 objectives while Chapter 1 lists 4 specific objectives:
"For reporting clarity, we split forecasting and cost-estimation outcomes into separate result slots and added optimization as an implementation objective."

## F. General Results, Conclusion, Recommendation (1:30)

Say this:

"Overall, the study achieved an end-to-end appliance-level forecasting system: from data capture to forecast, cost translation, budget classification, and actionable schedule recommendations.  
Conclusion: the framework is feasible, interpretable, and practical for household decision support under the defined scope.  
Recommendation: future work should include multi-household validation, stronger residual autocorrelation reduction, and expanded user-level usability testing and alert effectiveness metrics."

## G. Prototype Walkthrough (2:00)

Use this exact flow while showing UI:

1. "This panel shows actual vs forecast trend per appliance."
2. "This section summarizes next-24-hour projected kWh and projected cost."
3. "This card shows budget status and top-consuming appliance."
4. "This ranking panel orders appliances by expected cost contribution."
5. "This recommendation block shows optimization-based schedule suggestions."
6. "For example, on 2026-03-20, the system projected PHP 65.87 total, top load was aircon, and optimization estimated PHP 14.38 possible savings."

Close prototype:
"So the prototype does not just visualize history; it gives forecast-based, budget-aware actions users can apply before overspending happens."

## 3) Delivery Tips (Quick)

- Keep each section to timer limits; do not over-explain formulas unless asked.
- Anchor technical claims to one concrete date example (`2026-03-20`).
- If interrupted, jump to the next headline, not the previous details.
- End each major section with one takeaway sentence.
