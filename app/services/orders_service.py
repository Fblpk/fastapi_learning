from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate
from app.models.user import User
from app.core.enums import OrderStatus



def changed_order_status(
        order: Order,
        data_status: OrderStatus
):
    allowed ={
        OrderStatus.PENDING: {'PAID', 'CANCELED'},
        OrderStatus.PAID: {'SHIPPED', 'CANCELED'},
        OrderStatus.SHIPPED: {'CANCELED', 'COMPLETED'}
    }

    if data_status not in allowed.get(order.status, set()):
        raise ValueError('Order status not allowed')

    order.status = data_status



def create_order(
        order: OrderCreate,
        db: Session,
        current_user: User,
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

        product.quantity -= item.quantity
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
    new_order.items = order_items

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order



def get_user_orders(
        db: Session,
        current_user: User
):
    user_orders = db.query(Order).filter(Order.user_id == current_user.id).all()

    return user_orders



def get_order_by_id(
        id: int,
        db: Session,
        current_user: User
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



def cancel_order(
        id: int,
        db: Session,
        current_user: User
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

    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()

        if product:
            product.quantity += item.quantity

    changed_order_status(order, OrderStatus.CANCELED)
    db.commit()

    return {'canceled': True, 'id': id}

