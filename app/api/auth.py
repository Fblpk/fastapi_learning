from fastapi import APIRouter, Depends

from app.core.database import get_db
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, Token
from app.services import auth_service as service


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post('/register', response_model= Token)
def register(
        user: UserCreate,
        db: Session = Depends(get_db)
):
    return service.register(user, db)


@router.post('/login', response_model= Token)
def login(
        user: UserCreate,
        db: Session = Depends(get_db)
):
    return service.login(user, db)