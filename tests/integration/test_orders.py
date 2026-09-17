import pytest
from fastapi import HTTPException

from app.schemas.order import OrderCreate, OrderItemCreate
from app.services import orders_service as service
from sqlalchemy import text


async def test_create_order(db, user, product):
    order_data = OrderCreate(
        items=[
            OrderItemCreate(
                product_id=product.id,
                quantity=3
            )
        ]
    )

    order = await service.create_order(order_data, db, user)

    assert order.total_price == product.price * 3
    assert product.quantity == 2
    assert len(order.items) == 1
    assert order.items[0].product_id == product.id
    assert order.items[0].quantity == 3
    assert order.items[0].price_at_order == product.price


async def test_create_order_not_found_product_error(db, user):
    order_data = OrderCreate(
        items=[
            OrderItemCreate(
                product_id=999999,
                quantity=1,
            )
        ]
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_order(order_data, db, user)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Product not found"

    orders_count = (await db.execute(text("SELECT COUNT(*) FROM orders"))).scalar()
    items_count = (await db.execute(text("SELECT COUNT(*) FROM order_items"))).scalar()
    assert orders_count == 0
    assert items_count == 0


async def test_create_order_not_enough_quantity(db, user, product):
    order_data = OrderCreate(
        items=[
            OrderItemCreate(
                product_id=product.id,
                quantity=6
            )
        ]
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_order(order_data, db, user)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == f"Not enough stock for product {order_data.items[0].product_id}. Available: {product.quantity}"

    orders_count = (await db.execute(text("SELECT COUNT(*) FROM orders"))).scalar()
    items_count = (await db.execute(text("SELECT COUNT(*) FROM order_items"))).scalar()
    assert orders_count == 0
    assert items_count == 0