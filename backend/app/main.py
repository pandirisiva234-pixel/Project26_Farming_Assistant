from fastapi import FastAPI

from database import engine, Base
from models import models

from routes.users import router as users_router
from routes.languages import router as languages_router

from routes.intents import router as intents_router

from routes.queries import router as queries_router
from routes.responses import router as responses_router
from routes.weather import router as weather_router
from routes.intent import router as intent_router
from routes.assistant import router as assistant_router


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Project 26 - Multilingual Farming Assistant",
    description="Multilingual Voice-Based Farming Assistant with Camera-Based Plant Disease Detection",
    version="1.0.0"
)


# Register API routes
app.include_router(users_router)
app.include_router(languages_router)
app.include_router(intents_router)
app.include_router(queries_router)
app.include_router(responses_router)
app.include_router(weather_router)
app.include_router(intent_router)
app.include_router(assistant_router)


@app.get("/")
def home():
    return {
        "message": "Project 26 Farming Assistant API is running",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }