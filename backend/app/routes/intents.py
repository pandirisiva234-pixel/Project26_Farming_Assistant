from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.models import Intent
from schemas import IntentCreate

router = APIRouter(
    prefix="/intents",
    tags=["Intents"]
)


@router.get("/")
def get_intents(db: Session = Depends(get_db)):
    intents = db.query(Intent).all()
    return intents


@router.post("/")
def create_intent(
    intent: IntentCreate,
    db: Session = Depends(get_db)
):
    new_intent = Intent(
        name=intent.name,
        description=intent.description
    )

    db.add(new_intent)
    db.commit()
    db.refresh(new_intent)

    return new_intent