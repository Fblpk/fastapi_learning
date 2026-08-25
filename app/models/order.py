
from sqlalchemy import Column, Integer, Numeric, ForeignKey
from app.core.database import Base
from sqlalchemy.orm import relationship


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_price = Column(Numeric(precision=10, scale=2))

    user = relationship('User', back_populates='order')
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    price_at_order = Column(Numeric(precision=10, scale=2))

    order = relationship("Order", back_populates="items")
    product = relationship("Product")