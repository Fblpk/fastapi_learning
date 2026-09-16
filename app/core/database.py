from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from app.core.config import settings

ASYNC_DATABASE_URL = settings.ASYNC_DATABASE_URL

async_engine = create_async_engine(ASYNC_DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as db:
        yield db