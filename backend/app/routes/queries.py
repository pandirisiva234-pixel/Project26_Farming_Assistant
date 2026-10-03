from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.models import Query
from schemas import QueryCreate


router = APIRouter(
    prefix="/queries",
    tags=["Queries"]
)


@router.get("/")
def get_queries(db: Session = Depends(get_db)):
    queries = db.query(Query).all()
    return queries


@router.post("/")
def create_query(
    query: QueryCreate,
    db: Session = Depends(get_db)
):
    new_query = Query(
        user_id=query.user_id,
        intent_id=query.intent_id,
        language_id=query.language_id,
        query_text=query.query_text
    )

    db.add(new_query)
    db.commit()
    db.refresh(new_query)

    return new_query