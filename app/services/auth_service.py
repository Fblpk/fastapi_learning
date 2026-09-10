from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.schemas.user import UserCreate
from app.models.user import User
from app.core.security import hash_password, create_access_token, verify_password



def register(
        user: UserCreate,
        db: Session
):

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


def login(
        user: UserCreate,
        db: Session
):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"access_token": create_access_token(db_user.id), "token_type": "bearer"}