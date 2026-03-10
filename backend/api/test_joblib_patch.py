import sys
import pandas as pd
import pandas.core.arrays.string_
import joblib

class DummyStringArray:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
    def __init__(self, *args, **kwargs):
        self.data = None
    def __setstate__(self, state):
        if isinstance(state, tuple) and len(state) >= 2:
            self.data = state[1]
        else:
            self.data = state

pandas.core.arrays.string_.StringArray = DummyStringArray
sys.modules['pandas.core.arrays.string_'].StringArray = DummyStringArray

import pandas.core.dtypes.dtypes
class DummyStringDtype:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
    def __init__(self, *args, **kwargs):
        pass
    def __setstate__(self, state):
        pass

pandas.core.dtypes.dtypes.StringDtype = DummyStringDtype
sys.modules['pandas.core.dtypes.dtypes'].StringDtype = DummyStringDtype

path = "/Users/geovannyportodo/Sarimax-Thesis/backend/modeling/aircon/best_model.pkl"

try:
    print("Loading...")
    m = joblib.load(path)
    print("Success!")
except Exception as e:
    import traceback
    traceback.print_exc()
    print("Failed!", e)
