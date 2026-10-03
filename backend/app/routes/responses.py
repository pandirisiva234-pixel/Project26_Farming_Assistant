from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.models import Response
from schemas import ResponseCreate


router = APIRouter(
    prefix="/responses",
    tags=["Responses"]
)


@router.get("/")
def get_responses(db: Session = Depends(get_db)):
    responses = db.query(Response).all()
    return responses


@router.post("/")
def create_response(
    response: ResponseCreate,
    db: Session = Depends(get_db)
):
    new_response = Response(
        query_id=response.query_id,
        response_text=response.response_text,
        response_language=response.response_language
    )

    db.add(new_response)
    db.commit()
    db.refresh(new_response)

    return new_response