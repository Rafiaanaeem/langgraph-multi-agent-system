import requests
from langchain_core.tools import tool
from config import Config
@tool
def get_current_weather(city: str) -> str:
    """Fetches the current weather for a given city using OpenWeatherMap."""
    api_key = Config.WEATHER_API_KEY

    if not api_key:
        return "Error: OpenWeatherMap API key is missing. Please configure it in the .env file."
        
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url).json()
        
        if response.get("cod") != 200:
            return f"Error fetching weather: {response.get('message', 'City not found')}."
            
        temp = response["main"]["temp"]
        feels_like = response["main"]["feels_like"]
        condition = response["weather"][0]["description"]
        wind_speed = response["wind"]["speed"]
        
        return (
            f"Temperature: {temp}°C (Feels like {feels_like}°C), "
            f"Condition: {condition}, "
            f"Wind Speed: {wind_speed} m/s."
        )
    except Exception as e:
        return f"An error occurred while fetching the weather: {str(e)}"
