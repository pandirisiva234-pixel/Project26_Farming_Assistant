from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.models import User
from schemas import UserCreate

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        name=user.name,
        phone=user.phone,
        language_id=user.language_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user