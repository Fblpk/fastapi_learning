

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=3, max_length=75)
    price: float = Field(gt=0)
    quantity: int = Field(gt=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    owner_id: int | None = None

    class Config:
        from_attributes = True