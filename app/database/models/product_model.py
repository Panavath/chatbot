from datetime import datetime

from typing import Optional

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from app.database.models.base_model import Base


# class ProductModel(Base):
#     __tablename__ = "products"  # Changed to plural for consistency

#     id          = Column(Integer, primary_key=True, index=True)
#     type_id     = Column(Integer, ForeignKey("products_type.id", onupdate="CASCADE", ondelete="RESTRICT"))
#     creator_id  = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"))  # Fixed FK

#     code        = Column(String(100), unique=True, nullable=False)
#     name        = Column(String(100), nullable=False)
#     image       = Column(String(100), nullable=True)
#     unit_price  = Column(Float)
#     discount    = Column(Numeric(10, 2), nullable=False, default=0)

#     created_at  = Column(DateTime, default=datetime.utcnow)
#     updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     # Relationships
#     creator     = relationship("UserModel", back_populates="products")
#     product_type = relationship("ProductTypeModel", back_populates="products")
#     order_details = relationship("OrderDetailModel", back_populates="product")

#     def __repr__(self):
#         return f"<Product {self.name}>"

class ProductModel(Base):
    __tablename__       = "product"

    id                  = Column(Integer, primary_key=True, index=True)
    type_id             = Column(Integer, ForeignKey("products_type.id", onupdate="CASCADE", ondelete="RESTRICT"))
    creator_id          = Column(Integer, ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"))

    code                = Column(String(100), unique=True, nullable=False)
    name                = Column(String(100), nullable=False)
    image               = Column(String(100), nullable=True)
    unit_price          = Column(Float)
    discount            = Column(Numeric(10, 2), nullable=False, default=0)
    created_at          = Column(DateTime(timezone=True), nullable=False)
    updated_at          = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    creator             = relationship("UserModel", back_populates="products")
    product_type        = relationship("ProductTypeModel", back_populates="products")
    order_details       = relationship("OrderDetailModel", back_populates="product")

    def __repr__(self):
        return f"<Product {self.name}>"