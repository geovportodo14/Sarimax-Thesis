import pickle
import sys

path = "/Users/geovannyportodo/Sarimax-Thesis/backend/modeling/aircon/best_model.pkl"

class DummyArray:
    def __init__(self, *args, **kwargs):
        pass
    def __setstate__(self, state):
        self.data = state

class CustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if 'pandas' in module:
            if 'String' in name or 'NDArrayBacked' in name or 'ExtensionArray' in name:
                return DummyArray
        return super().find_class(module, name)

with open(path, 'rb') as f:
    u = CustomUnpickler(f)
    print("Loading with CustomUnpickler...")
    try:
        m = u.load()
        print("Success!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Failed:", e)
