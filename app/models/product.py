from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.core.database import Base
from sqlalchemy.orm import relationship


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    quantity = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))

    order_items = relationship("OrderItem")