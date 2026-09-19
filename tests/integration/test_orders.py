import pytest
from fastapi import HTTPException
from sqlalchemy import text

from app.schemas.order import OrderCreate, OrderItemCreate
from app.services import orders_service as service
from app.core.enums import OrderStatus


async def test_create_order(db, user, product):
    """Заказ создан, цена и количество сходятся, сток списан"""
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
    """Продукт не найден: 404, заказ не создан, сток откатывается"""
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


async def test_create_order_not_enough_quantity(db, user, product_factory):
    """Нехватка стока: 400, заказ не создан, сток обоих товаров откатывается."""
    product_1 = await product_factory()
    product_2 = await product_factory()
    initial_quantity = product_1.quantity
    product_2_id = product_2.id

    order_data = OrderCreate(
        items=[
            OrderItemCreate(
                product_id=product_1.id,
                quantity=3
            ),
            OrderItemCreate(
                product_id=product_2.id,
                quantity=10
            )
        ]
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_order(order_data, db, user)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == f"Not enough stock for product {product_2_id}. Available: {initial_quantity}"

    orders_count = (await db.execute(text("SELECT COUNT(*) FROM orders"))).scalar()
    items_count = (await db.execute(text("SELECT COUNT(*) FROM order_items"))).scalar()
    assert orders_count == 0
    assert items_count == 0

    await db.refresh(product_1)
    await db.refresh(product_2)
    assert product_1.quantity == initial_quantity
    assert product_2.quantity == initial_quantity



async def test_get_user_order(db, user, order):
    """Получаем список заказов юзера"""
    user_orders = await service.get_user_orders(db, user)

    assert len(user_orders) == 1
    assert order in user_orders


async def test_get_user_order_no_orders(db, user):
    """Нет заказов у юзера. Возвращаем пустой список"""
    user_orders = await service.get_user_orders(db, user)

    assert user_orders == []


async def test_get_order_by_id(db, user, order):
    """Получаем заказ по ID"""
    order_by_id = await service.get_order_by_id(order.id, db, user)

    assert order_by_id == order


async def test_get_order_by_id_not_found(db, user):
    """Заказ не найден: 404"""
    with pytest.raises(HTTPException) as exc_info:
        await service.get_order_by_id(999, db, user)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Order not found"


async def test_get_order_by_id_another_user(db, user_factory, order):
    """Заказ существует и принадлежит другому пользователю: 404"""
    another_user = await user_factory()
    with pytest.raises(HTTPException) as exc_info:
        await service.get_order_by_id(order.id, db, another_user)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Order not found"


async def test_cancel_order(db, user, order, product):
    """Заказ отменён: сток возвращается, статус: CANCELED"""
    initial_quantity = product.quantity
    cancelled_order = await service.cancel_order(order.id, db, user)

    assert order.status == OrderStatus.CANCELED
    assert product.quantity == initial_quantity + order.items[0].quantity


async def test_cancel_order_not_found(db, user):
    """Заказ для отмены не найден: 404"""
    with pytest.raises(HTTPException) as exc_info:
        await service.cancel_order(999, db, user)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Order not found"