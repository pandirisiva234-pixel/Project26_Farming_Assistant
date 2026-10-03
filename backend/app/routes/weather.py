import os
import requests

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.models import WeatherData
from schemas import WeatherCreate


load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


router = APIRouter(
    prefix="/weather",
    tags=["Weather"]
)


@router.get("/")
def get_weather_data(db: Session = Depends(get_db)):
    weather = db.query(WeatherData).all()
    return weather


@router.post("/")
def create_weather(
    weather: WeatherCreate,
    db: Session = Depends(get_db)
):
    new_weather = WeatherData(
        location=weather.location,
        temperature=weather.temperature,
        humidity=weather.humidity,
        precipitation=weather.precipitation,
        rain=weather.rain,
        wind_speed=weather.wind_speed
    )

    db.add(new_weather)
    db.commit()
    db.refresh(new_weather)

    return new_weather


@router.get("/live/{city}")
def get_live_weather(
    city: str,
    db: Session = Depends(get_db)
):
    if not OPENWEATHER_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OpenWeather API key is not configured"
        )

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json()
        )

    data = response.json()

    temperature = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]

    rain = 0.0
    precipitation = 0.0

    if "rain" in data:
        rain = data["rain"].get("1h", 0.0)
        precipitation = rain

    new_weather = WeatherData(
        location=city,
        temperature=temperature,
        humidity=humidity,
        precipitation=precipitation,
        rain=rain,
        wind_speed=wind_speed
    )

    db.add(new_weather)
    db.commit()
    db.refresh(new_weather)

    return {
        "location": city,
        "temperature": temperature,
        "humidity": humidity,
        "rain": rain,
        "precipitation": precipitation,
        "wind_speed": wind_speed,
        "weather": data["weather"][0]["description"]
    }