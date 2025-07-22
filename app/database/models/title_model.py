from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database.models.base_model import Base

class TitleModel(Base):
    __tablename__ = "title"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    kh_name = Column(String(250), nullable=False)
    en_name = Column(String(250), nullable=False)  # Changed to nullable=False to match your model
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # ministers = relationship("MinisterModel", back_populates="title")

    def __repr__(self):
        return f"<Title {self.kh_name}>" 