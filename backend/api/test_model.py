import joblib

path = "/Users/geovannyportodo/Sarimax-Thesis/backend/modeling/aircon/best_model.pkl"
model = joblib.load(path)

print("Endogenous:", model.model.endog_names)
print("Exogenous:", model.model.exog_names if hasattr(model.model, "exog_names") else "None")
