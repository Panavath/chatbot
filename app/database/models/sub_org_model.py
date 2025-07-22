from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database.models.base_model import Base

class SubOrgModel(Base):
    __tablename__ = "sub_org"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slug = Column(String(250), nullable=False)
    logo = Column(String(250), nullable=False, default='upload/file/bdca7426-ad51-4d35-97fd-92808e3c641b')
    kh_name = Column(String(250), nullable=False, unique=True)
    en_name = Column(String(250), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # sub_org_leaders = relationship("SubOrgLeaderModel", back_populates="sub_org")

    def __repr__(self):
        return f"<SubOrg {self.kh_name}>" 