from fastapi import APIRouter, Depends

from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, Token
from app.services import auth_service as service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=Token)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await service.register(user, db)


@router.post("/login", response_model=Token)
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await service.login(user, db)