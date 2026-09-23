from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.order import OrderItem


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    price: Mapped[Decimal] = mapped_column(Numeric)
    quantity: Mapped[int]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")