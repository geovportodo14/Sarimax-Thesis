import pickle
import joblib
import io
import sys

path = "/Users/geovannyportodo/Sarimax-Thesis/backend/modeling/aircon/best_model.pkl"

class DummyStringDtype:
    def __init__(self, *args, **kwargs):
        print(f"DummyStringDtype initialized with args={args}, kwargs={kwargs}")
    def __setstate__(self, state):
        print(f"DummyStringDtype setstate with {state}")

class CustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if name == 'StringDtype' and 'pandas' in module:
            return DummyStringDtype
        return super().find_class(module, name)

with open(path, 'rb') as f:
    unpickler = CustomUnpickler(f)
    print("Unpickling with custom unpickler...")
    try:
        model = unpickler.load()
        print("Model loaded successfully!")
    except Exception as e:
        print("Failed:", repr(e))
