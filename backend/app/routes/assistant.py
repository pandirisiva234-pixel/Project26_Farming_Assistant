import os
import requests

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.intent_classifier import classify_intent
from services.rag_service import (
    search_knowledge,
    extract_answer
)

from services.translation_service import translate_text


# ========================================================
# LOAD ENVIRONMENT VARIABLES
# ========================================================

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


# ========================================================
# CREATE ROUTER
# ========================================================

router = APIRouter(
    prefix="/assistant",
    tags=["Farming Assistant"]
)


# ========================================================
# REQUEST MODEL
# ========================================================

class AssistantRequest(BaseModel):
    text: str
    city: str
    language_code: str = "en"


# ========================================================
# FARMING ASSISTANT API
# ========================================================

@router.post("/query")
def assistant_query(request: AssistantRequest):

    # ====================================================
    # STEP 1: CLASSIFY FARMER QUESTION
    # ====================================================

    intent = classify_intent(request.text)


    # ====================================================
    # STEP 2: HANDLE WEATHER QUESTIONS
    # ====================================================

    if intent == "Weather":

        if not OPENWEATHER_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenWeather API key is not configured"
            )

        url = "https://api.openweathermap.org/data/2.5/weather"

        params = {
            "q": request.city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:

            try:
                error_detail = response.json()
            except Exception:
                error_detail = "Unable to fetch weather information"

            raise HTTPException(
                status_code=response.status_code,
                detail=error_detail
            )

        data = response.json()

        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        weather = data["weather"][0]["description"]


        # ================================================
        # CREATE WEATHER ANSWER
        # ================================================

        weather_answer = (
            f"The current weather in {request.city} is "
            f"{weather}. The temperature is "
            f"{temperature}°C with humidity of "
            f"{humidity}%. Wind speed is "
            f"{wind_speed} meters per second."
        )


        # ================================================
        # TRANSLATE WEATHER ANSWER
        # ================================================

        translated_answer = translate_text(
            weather_answer,
            request.language_code
        )


        return {
            "query": request.text,
            "intent": intent,
            "language_code": request.language_code,
            "location": request.city,
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "weather": weather,
            "answer": translated_answer
        }


    # ====================================================
    # STEP 3: SEARCH AGRICULTURAL KNOWLEDGE USING RAG
    # ====================================================

    documents = search_knowledge(
        request.text,
        top_k=3
    )


    # ====================================================
    # STEP 4: CHECK WHETHER RESULTS WERE FOUND
    # ====================================================

    if not documents:

        english_answer = (
            "I could not find relevant agricultural information."
        )

        translated_answer = translate_text(
            english_answer,
            request.language_code
        )

        return {
            "query": request.text,
            "intent": intent,
            "language_code": request.language_code,
            "answer": translated_answer,
            "retrieved_documents": 0
        }


    # ====================================================
    # STEP 5: EXTRACT RAG ANSWER
    # ====================================================

    answer = extract_answer(
        documents[0]
    )


    # ====================================================
    # STEP 6: TRANSLATE RAG ANSWER
    # ====================================================

    translated_answer = translate_text(
        answer,
        request.language_code
    )


    # ====================================================
    # STEP 7: RETURN FINAL RESPONSE
    # ====================================================

    return {
        "query": request.text,
        "intent": intent,
        "language_code": request.language_code,
        "answer": translated_answer,
        "retrieved_documents": len(documents)
    }