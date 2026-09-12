from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_async
from app.schemas.order import OrderCreate, OrderResponse
from app.core.security import get_current_user
from app.models.user import User
from app.services import orders_service as service

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    db: AsyncSession = Depends(get_db_async),
    current_user: User = Depends(get_current_user),
):
    return await service.create_order(order, db, current_user)


@router.get("/", response_model=list[OrderResponse])
async def get_user_orders(
    db: AsyncSession = Depends(get_db_async),
    current_user: User = Depends(get_current_user),
):
    return await service.get_user_orders(db, current_user)


@router.get("/{id}", response_model=OrderResponse)
async def get_order_by_id(
    id: int,
    db: AsyncSession = Depends(get_db_async),
    current_user: User = Depends(get_current_user),
):
    return await service.get_order_by_id(id, db, current_user)


@router.post("/{id}")
async def cancel_order(
    id: int,
    db: AsyncSession = Depends(get_db_async),
    current_user: User = Depends(get_current_user),
):
    return await service.cancel_order(id, db, current_user)
