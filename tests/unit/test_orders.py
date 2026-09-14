import pytest
from fastapi import HTTPException

from app.core.enums import OrderStatus
from app.services import orders_service as service
from app.models.order import Order

@pytest.mark.parametrize(
    'current, new, should_fail',
    [
        (OrderStatus.PENDING, OrderStatus.PENDING, True),
        (OrderStatus.PENDING, OrderStatus.PAID, False),
        (OrderStatus.PENDING, OrderStatus.CANCELED, False),
        (OrderStatus.PENDING, OrderStatus.COMPLETED, True),
        (OrderStatus.PENDING, OrderStatus.SHIPPED, True),
        (OrderStatus.PAID, OrderStatus.PAID, True),
        (OrderStatus.PAID, OrderStatus.PENDING, True),
        (OrderStatus.PAID, OrderStatus.CANCELED, False),
        (OrderStatus.PAID, OrderStatus.COMPLETED, True),
        (OrderStatus.PAID, OrderStatus.SHIPPED, False),
        (OrderStatus.SHIPPED, OrderStatus.SHIPPED, True),
        (OrderStatus.SHIPPED, OrderStatus.PAID, True),
        (OrderStatus.SHIPPED, OrderStatus.CANCELED, True),
        (OrderStatus.SHIPPED, OrderStatus.COMPLETED, False),
        (OrderStatus.SHIPPED, OrderStatus.PENDING, True)
    ]
)

def test_changed_order_status(current, new, should_fail):
    order = Order(status=current)

    if should_fail:
        with pytest.raises(HTTPException):
            service.changed_order_status(order, new)

    else:
        service.changed_order_status(order, new)

        assert order.status == new



@pytest.mark.parametrize(
    'terminal_status',
    [OrderStatus.COMPLETED, OrderStatus.CANCELED]
)

@pytest.mark.parametrize(
    'any_status', OrderStatus
)

def test_cannot_change_status_from_terminal(terminal_status, any_status):
    order = Order(status=terminal_status)

    with pytest.raises(HTTPException) as exc_info:
        service.changed_order_status(order, any_status)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == f"Order status: {order.status} not allowed"





