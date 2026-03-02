import requests
import logging

logger = logging.getLogger(__name__)

class WeatherClient:
    def __init__(self, api_key, city):
        self.api_key = api_key
        self.city = city
        self.url = f"https://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}&units=metric"

    def get_weather(self):
        try:
            r = requests.get(self.url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                main = data.get("main", {})
                rain = data.get("rain", {})
                # Extract rainfall (1h is standard for current weather, default to 0)
                rainfall = rain.get("1h", rain.get("3h", 0))
                
                return {
                    "temp": main.get("temp"),
                    "humidity": main.get("humidity"),
                    "rainfall": rainfall,
                }
            logger.warning(f"Weather API error: {r.status_code}")
            return {"temp": None, "humidity": None, "rainfall": None}
        except Exception as e:
            logger.exception("Weather request failed")
            return {"temp": None, "humidity": None, "rainfall": None}
