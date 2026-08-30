from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderResponse, OrderItemCreate, OrderItemResponse
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
