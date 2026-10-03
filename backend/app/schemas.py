from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    language_id: Optional[int] = None


class LanguageCreate(BaseModel):
    name: str
    code: str


class IntentCreate(BaseModel):
    name: str
    description: Optional[str] = None


class QueryCreate(BaseModel):
    user_id: Optional[int] = None
    intent_id: Optional[int] = None
    language_id: Optional[int] = None
    query_text: str


class ResponseCreate(BaseModel):
    query_id: Optional[int] = None
    response_text: str
    response_language: Optional[str] = None


class WeatherCreate(BaseModel):
    location: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    precipitation: Optional[float] = None
    rain: Optional[float] = None
    wind_speed: Optional[float] = None
    forecast_time: Optional[str] = None