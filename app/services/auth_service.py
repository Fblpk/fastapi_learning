from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.schemas.user import UserCreate
from app.models.user import User
from app.core.security import hash_password, create_access_token, verify_password


async def register(user: UserCreate, db: AsyncSession):

    stmt = select(User).filter(User.username == user.username)
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    new_user = User(
        username=user.username, hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    await db.commit()

    return {"access_token": create_access_token(new_user.id), "token_type": "bearer"}


async def login(user: UserCreate, db: AsyncSession):
    stmt = select(User).filter(User.username == user.username)
    db_user = (await db.execute(stmt)).scalars().first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"access_token": create_access_token(db_user.id), "token_type": "bearer"}