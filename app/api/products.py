from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.product import ProductCreate, ProductResponse
from app.core.security import get_current_user
from app.models.user import User
from app.services import products_service as service

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.create_product(product, db, current_user)


@router.put("/{id}", response_model=ProductResponse)
async def update_product(
    id: int,
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.update_product(id, product, db, current_user)


@router.delete("/{id}")
async def delete_product(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.delete_product(id, db, current_user)


@router.get("/{id}", response_model=ProductResponse)
async def get_product(id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_product(id, db)


@router.get("/", response_model=List[ProductResponse])
async def get_all_products(
    limit: int = 10,
    offset: int = 0,
    search: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_all_products(db, limit, offset, search, min_price, max_price)