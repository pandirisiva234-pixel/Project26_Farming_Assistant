from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.models import Language
from schemas import LanguageCreate

router = APIRouter(
    prefix="/languages",
    tags=["Languages"]
)


@router.get("/")
def get_languages(db: Session = Depends(get_db)):
    languages = db.query(Language).all()
    return languages


@router.post("/")
def create_language(
    language: LanguageCreate,
    db: Session = Depends(get_db)
):
    new_language = Language(
        name=language.name,
        code=language.code
    )

    db.add(new_language)
    db.commit()
    db.refresh(new_language)

    return new_language