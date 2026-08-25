from pydantic import BaseModel, ConfigDict



class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]


class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price_at_order: float

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: float
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)
