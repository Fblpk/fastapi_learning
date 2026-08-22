from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import String

from app.core.database import get_db
from sqlalchemy.orm import Session
from app.core.security import create_access_token, verify_password, hash_password
from app.schemas.user import UserCreate, Token
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post('/register', response_model= Token)
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = User(
        username = user.username,
        hashed_password = hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"access_token": create_access_token(new_user.id), "token_type": "bearer"}


@router.post('/login', response_model= Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"access_token": create_access_token(db_user.id), "token_type": "bearer"}
