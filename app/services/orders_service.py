from sqlalchemy import select
from fastapi import HTTPException
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate
from app.models.user import User
from app.core.enums import OrderStatus



def changed_order_status(order: Order, data_status: OrderStatus):
    allowed = {
        OrderStatus.PENDING: {
            OrderStatus.PAID,
            OrderStatus.CANCELED
        },
        OrderStatus.PAID: {
            OrderStatus.SHIPPED,
            OrderStatus.CANCELED
        },
        OrderStatus.SHIPPED: {
            OrderStatus.COMPLETED
        },
    }

    if data_status not in allowed.get(order.status, set()):
        raise HTTPException(
            status_code=400,
            detail=f"Order status: {order.status} not allowed"
        )

    order.status = data_status


async def create_order(
    order: OrderCreate,
    db: AsyncSession,
    current_user: User,
):
    try:
        total = 0
        order_items = []

        for item in order.items:
            stmt = select(Product).filter(Product.id == item.product_id).with_for_update(nowait=True)

            product = (await db.execute(stmt)).scalars().first()

            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

            if item.quantity > product.quantity: #type: ignore
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for product {item.product_id}. Available: {product.quantity}", #type: ignore
                )

            product.quantity -= item.quantity #type: ignore
            total += item.quantity * product.price #type: ignore
            order_items.append(
                OrderItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price_at_order=product.price, #type: ignore
                )
            )

        new_order = Order(user_id=current_user.id, total_price=total)
        new_order.items = order_items

        db.add(new_order)
        await db.commit()

        return new_order

    except OperationalError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="The item is currently being processed by another user. Please try again."
        )

    except HTTPException:
        await db.rollback()
        raise


async def get_user_orders(db: AsyncSession, current_user: User):
    stmt = select(Order).filter(Order.user_id == current_user.id).options(selectinload(Order.items))
    user_orders = (await db.execute(stmt)).scalars().all()

    return user_orders


async def get_order_by_id(id: int, db: AsyncSession, current_user: User):
    stmt = select(Order).filter(
        Order.id == id, Order.user_id == current_user.id
    ).options(selectinload(Order.items))
    order = (await db.execute(stmt)).scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


async def cancel_order(id: int, db: AsyncSession, current_user: User):
    stmt = select(Order).filter(Order.id == id, Order.user_id == current_user.id).options(selectinload(Order.items))
    order = (await db.execute(stmt)).scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    for item in order.items: #type: ignore
        product_stmt = select(Product).filter(Product.id == item.product_id)
        product = (await db.execute(product_stmt)).scalars().first()


        if product:
            product.quantity += item.quantity #type: ignore

    changed_order_status(order, OrderStatus.CANCELED)
    await db.commit()
    return {"canceled": True, "id": id}

