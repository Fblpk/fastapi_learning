from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderResponse
from app.core.security import get_current_user
from app.models.user import User



router = APIRouter(prefix='/orders', tags=['Orders'])


@router.post('/', response_model=OrderResponse)
def create_order(
        order: OrderCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    total = 0
    order_items = []
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()

        if not product:
            raise HTTPException(
                status_code=404,
                detail='Product not found'
            )

        if item.quantity > product.quantity:
            raise HTTPException(
                status_code=400,
                detail=f'Not enough stock for product {item.product_id}. Available: {product.quantity}'
            )

        total += (item.quantity * product.price)
        order_items.append(OrderItem(
            product_id = item.product_id,
            quantity = item.quantity,
            price_at_order = product.price
        ))

    new_order = Order(
        user_id=current_user.id,
        total_price = total
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item in order_items:
        item.order_id = new_order.id
        db.add(item)
    db.commit()

    return new_order


@router.get('/', response_model=list[OrderResponse])
def get_user_orders(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    user_orders = db.query(Order).filter(Order.user_id == current_user.id).all()

    return user_orders


@router.get('/{id}', response_model=OrderResponse)
def get_order_by_id(
        id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == id).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail='Order not found'
        )

    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail='Forbidden'
        )

    return order