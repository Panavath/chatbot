from datetime import datetime

from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database.models.base_model import Base


class ProductTypeModel(Base):
    __tablename__       = "products_type"

    id                  = Column(Integer, primary_key=True, index=True)
    name                = Column(String(100), nullable=False)
    image               = Column(String(100), nullable=True)
    created_at          = Column(DateTime(timezone=True), nullable=False)
    updated_at          = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    products            = relationship("ProductModel", back_populates="product_type")

    def __repr__(self):
        return f"<ProductType {self.name}>"