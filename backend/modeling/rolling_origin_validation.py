import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
import warnings

# Use the path you provided
BASE_PATH = "/Users/geovannyportodo/Sarimax-Thesis/data/final/"
warnings.filterwarnings("ignore")

def full_sarimax_pipeline(file_name, appliance_name):
    file_path = os.path.join(BASE_PATH, file_name)
    print(f"\n{'='*70}\nTHESIS PIPELINE: {appliance_name}\n{'='*70}")

    # 1. LOAD & PREPROCESS
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    # FIX: Use lowercase 'h' for frequency and .ffill() for newer Pandas versions
    df = df.asfreq('h').ffill() 

    # 2. ADF TEST (Stationarity)
    print("\n[STEP 1] Augmented Dickey-Fuller Test")
    dftest = adfuller(df['kWh'].dropna(), autolag='AIC')
    print(f"ADF Statistic: {dftest[0]:.4f} (p-value: {dftest[1]:.4f})")

    # 4. EXOGENOUS FEATURES (Section 3.3.4)
    # Including all features from your CSV data
    exog_cols = ['temperature', 'humidity', 'pressure', 'hour_of_day', 
                 'day_of_week', 'is_weekend', 'lag_24', 'lag_168']
    train_size = int(len(df) * 0.8)
    train, test = df.iloc[:train_size], df.iloc[train_size:]

    # 5. MODEL SELECTION (AIC/BIC Comparison)
    print("\n[STEP 2] Model Selection (AIC/BIC Comparison)")
    candidate_orders = [(1,1,1), (1,0,1), (2,1,1)]
    results_list = []
    
    for order in candidate_orders:
        try:
            model = SARIMAX(train['kWh'], exog=train[exog_cols], 
                            order=order, seasonal_order=(1,1,1,24)).fit(disp=False)
            results_list.append({'Order': order, 'AIC': model.aic, 'BIC': model.bic})
            print(f"Order {order}: AIC={model.aic:.2f}")
        except: continue

    best_order = sorted(results_list, key=lambda x: x['AIC'])[0]['Order']
    print(f"Best Order Selected: {best_order}")

    # 6. FINAL TRAINING & DIAGNOSTICS (Critical for Chapter 4)
    final_model = SARIMAX(train['kWh'], exog=train[exog_cols], 
                          order=best_order, seasonal_order=(1,1,1,24)).fit(disp=False)
    
    print("\n[STEP 3] Running Residual Diagnostics...")
    final_model.plot_diagnostics(figsize=(15, 10))
    plt.show()

    # 7. EVALUATION (Metrics as per Section 3.6.3)
    predictions = final_model.forecast(steps=len(test), exog=test[exog_cols])
    mae = mean_absolute_error(test['kWh'], predictions)
    rmse = np.sqrt(mean_squared_error(test['kWh'], predictions))
    mape = np.mean(np.abs((test['kWh'] - predictions) / (test['kWh'] + 1e-7))) * 100
    r2 = r2_score(test['kWh'], predictions)

    print("\n[STEP 4] Final Evaluation Metrics")
    print(f"MAE: {mae:.6f} | RMSE: {rmse:.6f} | MAPE: {mape:.2f}% | R-squared: {r2:.4f}")

    # 8. VISUALIZATION
    plt.figure(figsize=(12, 5))
    plt.plot(test.index[:168], test['kWh'][:168], label='Actual', alpha=0.6)
    plt.plot(test.index[:168], predictions[:168], label='Forecast', color='red', ls='--')
    plt.title(f"Forecast vs Actual (1 Week Preview): {appliance_name}")
    plt.legend()
    plt.show()

    # 9. SAVE MODEL
    joblib.dump(final_model, f"model_{appliance_name.lower().replace(' ', '_')}.pkl")

# EXECUTION BLOCK
appliances = [
    ('model_ready_a3ed2fe218a724b4fepeni.csv', 'Air Conditioner'),
    ('model_ready_a3986d20c19f33c7c107fw.csv', 'Refrigerator'),
    ('model_ready_a3c772d3fde52dbae832bi.csv', 'Electric Fan')
]

for file, name in appliances:
    full_sarimax_pipeline(file, name)