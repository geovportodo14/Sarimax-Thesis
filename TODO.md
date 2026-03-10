# Dashboard Data Refinement & Smart Budgeting — Implementation TODO

## Steps

- [x] 1. `backend/controllers/liveForecastController.js` — Add `current_bucket_index` to API response
- [x] 2. `backend/controllers/historicalController.js` — Remove all forecasting/prediction logic; return actuals only
- [x] 3. `src/App.js` — Fix double-counting: sum forecasts only from `current_bucket_index + 1` onwards

## No Changes Needed
- `backend/api/services/model_loader.py` — already correct (stable refrigerator model + correct metrics)
- `src/components/SmartBudgetCard.js` — already fully implemented
