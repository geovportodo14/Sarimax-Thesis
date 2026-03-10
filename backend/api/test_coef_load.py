import os
import sys

# Add the project root to sys.path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.api.services.model_loader import ModelLoader

try:
    print("Testing Aircon Model Load...")
    ac_model = ModelLoader.get_model("aircon")
    print("Aircon Model Params:", ac_model.param_names)

    print("\nTesting Electricfan Model Load...")
    ef_model = ModelLoader.get_model("electricfan")
    print("Electricfan Model Params:", ef_model.param_names)

    print("\nTesting Refrigerator Model Load...")
    ref_model = ModelLoader.get_model("refrigerator")
    print("Refrigerator Model Params:", ref_model.param_names)

    print("\nSUCCESS: All models loaded via JSON and CSV metadata.")
except Exception as e:
    import traceback
    traceback.print_exc()
