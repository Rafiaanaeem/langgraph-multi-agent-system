import requests
from langchain_core.tools import tool
from config import Config
@tool
def get_current_weather(city: str = "Islamabad") -> str:
    """Fetches the current weather for a given city using OpenWeatherMap.
    If no city is provided or if city is empty, defaults to Islamabad.
    """
    # Safeguard if the LLM passes an empty string or None
    if not city or not str(city).strip():
        city = "Islamabad"

    api_key = Config.WEATHER_API_KEY
    print("Weather API Key:", api_key)

    if not api_key:
        return "Error: OpenWeatherMap API key is missing. Please configure it in the .env file."
        
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city.strip()}&appid={api_key}&units=metric"
        
        print("Before request")

        response = requests.get(url, timeout=5)

        print("Status Code:", response.status_code)

        print("After request")

        response = response.json()
        
        if response.get("cod") != 200:
            return f"Error fetching weather: {response.get('message', 'City not found')}."
            
        temp = response["main"]["temp"]
        feels_like = response["main"]["feels_like"]
        condition = response["weather"][0]["description"]
        wind_speed = response["wind"]["speed"]
        humidity = response["main"]["humidity"]
        
        return (
    f"City: {city.title()}\n"
    f"Temperature: {temp}°C\n"
    f"Feels Like: {feels_like}°C\n"
    f"Condition: {condition}\n"
    f"Humidity: {humidity}%\n"
    f"Wind Speed: {wind_speed} m/s"
)
    except requests.exceptions.Timeout:
        return "Error: The weather service took too long to respond. Please try again later."
    except Exception as e:
        return f"An error occurred while fetching the weather: {str(e)}"