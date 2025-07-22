from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.database.models.base_model import Base

class ContentModel(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    page = Column(String(50), nullable=False)
    slug = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    kh_title = Column(String(250), nullable=False)
    en_title = Column(String(250), nullable=False)
    image = Column(String(250), nullable=True)
    kh_content = Column(Text, nullable=True)
    en_content = Column(Text, nullable=True)
    editor_name = Column(String(250), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Content {self.kh_title}>" 