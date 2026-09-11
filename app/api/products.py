from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.product import ProductCreate, ProductResponse
from app.core.security import get_current_user
from app.models.user import User
from app.services import products_service as service

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_product(product, db, current_user)


@router.put("/{id}", response_model=ProductResponse)
def update_product(
    id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.update_product(id, product, db, current_user)


@router.delete("/{id}")
def delete_product(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.delete_product(id, db, current_user)


@router.get("/{id}", response_model=ProductResponse)
def get_product(id: int, db: Session = Depends(get_db)):
    return service.get_product(id, db)


@router.get("/", response_model=List[ProductResponse])
def get_all_products(
    limit: int = 10,
    offset: int = 0,
    search: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    db: Session = Depends(get_db),
):
    return service.get_all_products(db, limit, offset, search, min_price, max_price)
