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


load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


router = APIRouter(
    prefix="/assistant",
    tags=["Farming Assistant"]
)


class AssistantRequest(BaseModel):
    text: str
    city: str


@router.post("/query")
def assistant_query(request: AssistantRequest):

    # ========================================================
    # STEP 1: CLASSIFY FARMER QUESTION
    # ========================================================

    intent = classify_intent(request.text)


    # ========================================================
    # STEP 2: HANDLE WEATHER QUESTIONS
    # ========================================================

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
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )

        data = response.json()

        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        weather = data["weather"][0]["description"]

        return {
            "query": request.text,
            "intent": intent,
            "location": request.city,
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "weather": weather
        }


    # ========================================================
    # STEP 3: SEARCH AGRICULTURAL KNOWLEDGE USING RAG
    # ========================================================

    documents = search_knowledge(
        request.text,
        top_k=3
    )


    # ========================================================
    # STEP 4: CHECK WHETHER RESULTS WERE FOUND
    # ========================================================

    if not documents:

        return {
            "query": request.text,
            "intent": intent,
            "answer": (
                "I could not find relevant agricultural information."
            ),
            "retrieved_documents": 0
        }


    # ========================================================
    # STEP 5: EXTRACT ONLY THE ANSWER
    # ========================================================

    answer = extract_answer(
        documents[0]
    )


    # ========================================================
    # STEP 6: RETURN CLEAN RESPONSE
    # ========================================================

    return {
        "query": request.text,
        "intent": intent,
        "answer": answer,
        "retrieved_documents": len(documents)
    }