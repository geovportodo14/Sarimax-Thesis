from backend.api.services.predict_service import PredictService

def test():
    print("Testing aircon...")
    res = PredictService.get_forecast(appliance="aircon", history=[100.0, 150.0, 120.0], horizon=4)
    print("Aircon Res:", res)

    print("\nTesting electric_fan...")
    res2 = PredictService.get_forecast(appliance="electric_fan", history=[50.0, 60.0], horizon=4)
    print("Fan Res:", res2)
    
    print("\nTesting refrigerator...")
    res3 = PredictService.get_forecast(appliance="refrigerator", history=[20.0, 30.0], horizon=4)
    print("Fridge Res:", res3)

if __name__ == "__main__":
    test()
