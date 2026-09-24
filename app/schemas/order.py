from pydantic import BaseModel, ConfigDict, Field
from app.core.enums import OrderStatus


class OrderItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(min_length=1)


class ProductSummary(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class OrderItemResponse(BaseModel):
    product_id: int
    product: ProductSummary
    quantity: int
    price_at_order: float

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: float
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
