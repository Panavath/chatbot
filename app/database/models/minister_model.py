from datetime import datetime, date
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.models.base_model import Base

class MinisterModel(Base):
    __tablename__ = "about_minister"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title_id = Column(Integer, ForeignKey("title.id"), nullable=False)
    avatar = Column(String(250), nullable=False)
    kh_name = Column(String(250), nullable=False)
    en_name = Column(String(250), nullable=True)
    legislation = Column(Integer, nullable=False)
    current = Column(Boolean, nullable=False, default=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    title = relationship("TitleModel", foreign_keys=[title_id])

    def __repr__(self):
        return f"<Minister {self.kh_name}>" 