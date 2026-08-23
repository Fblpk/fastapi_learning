from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    owner_id: int | None = None

    class Config:
        from_attributes = True