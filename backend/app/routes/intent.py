from fastapi import APIRouter
from pydantic import BaseModel

from services.intent_classifier import classify_intent


router = APIRouter(
    prefix="/intent",
    tags=["Intent Classification"]
)


class IntentRequest(BaseModel):
    text: str


@router.post("/classify")
def classify_user_intent(request: IntentRequest):

    intent = classify_intent(request.text)

    return {
        "query": request.text,
        "intent": intent
    }