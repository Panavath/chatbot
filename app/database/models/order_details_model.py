from datetime import datetime

from typing import Optional

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.models.base_model import Base

# class OrderDetailModel(Base):
#     __tablename__ = "order_details"

#     id           = Column(Integer, primary_key=True, index=True)
#     order_id     = Column(Integer, ForeignKey("orders.id", onupdate="CASCADE", ondelete="CASCADE"))  # Fixed FK
#     product_id   = Column(Integer, ForeignKey("products.id", onupdate="CASCADE", ondelete="CASCADE"))  # Fixed FK

#     unit_price   = Column(Float)
#     qty          = Column(Integer, nullable=False, default=0)

#     created_at   = Column(DateTime, default=datetime.utcnow)
#     updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     # Relationships
#     order        = relationship("OrderModel", back_populates="order_details")
#     product      = relationship("ProductModel", back_populates="order_details")

#     def __repr__(self):
#         return f"<OrderDetail {self.id}>"

class OrderDetailModel(Base):
    __tablename__       = "order_details"

    id                  = Column(Integer, primary_key=True, index=True)
    order_id            = Column(Integer, ForeignKey("order.id", onupdate="CASCADE", ondelete="CASCADE"))
    product_id          = Column(Integer, ForeignKey("product.id", onupdate="CASCADE", ondelete="CASCADE"))
    unit_price          = Column(Float)
    qty                 = Column(Integer, nullable=False, default=0)
    created_at          = Column(DateTime(timezone=True), nullable=False)
    updated_at          = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    order               = relationship("OrderModel", back_populates="order_details")
    product             = relationship("ProductModel", back_populates="order_details")

    def __repr__(self):
        return f"<OrderDetail {self.id}>"