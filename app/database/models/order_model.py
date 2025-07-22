from datetime import datetime

from typing import Optional

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from app.database.models.base_model import Base
from app.database.models.user_model import UserModel


# class OrderModel(Base):
#     __tablename__ = "orders"  # Changed from "order" to "orders" for clarity

#     id            = Column(Integer, primary_key=True, index=True)
#     cashier_id    = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"))  # Fixed FK
#     receipt_number = Column(BigInteger, unique=True, nullable=False)
#     total_price   = Column(Float)
#     platform      = Column(String(20), default='Web')

#     created_at    = Column(DateTime, default=datetime.utcnow)
#     updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     # Relationships
#     cashier       = relationship("UserModel", back_populates="orders")
#     order_details = relationship("OrderDetailModel", back_populates="order")

#     def __repr__(self):
#         return f"<Order {self.receipt_number}>"
    

class OrderModel(Base):
    __tablename__       = "order"

    id                  = Column(Integer, primary_key=True, index=True)
    cashier_id          = Column(Integer, ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"))
    receipt_number      = Column(BigInteger, unique=True, nullable=False)
    total_price         = Column(Float)
    ordered_at          = Column(DateTime(timezone=True), default=datetime.utcnow)
    platform            = Column(String(20), default='Web')
    created_at          = Column(DateTime(timezone=True), nullable=False)
    updated_at          = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    cashier             = relationship("UserModel", foreign_keys=[cashier_id], back_populates="orders")
    order_details       = relationship("OrderDetailModel", back_populates="order")

    def __repr__(self):
        return f"<Order {self.receipt_number}>"