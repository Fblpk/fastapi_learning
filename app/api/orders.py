from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.order import OrderCreate, OrderResponse
from app.core.security import get_current_user
from app.models.user import User
from app.services import orders_service as service

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_order(order, db, current_user)


@router.get("/", response_model=list[OrderResponse])
def get_user_orders(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return service.get_user_orders(db, current_user)


@router.get("/{id}", response_model=OrderResponse)
def get_order_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.get_order_by_id(id, db, current_user)


@router.post("/{id}")
def cancel_order(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.cancel_order(id, db, current_user)
