from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SubOrgSchema(BaseModel):
    """Schema for sub-organization data"""
    id: int
    kh_name: str
    en_name: str
    
    class Config:
        from_attributes = True

class MinisterSchema(BaseModel):
    """Schema for minister data"""
    id: int
    kh_name: str
    en_name: Optional[str] = None
    current: bool
    legislation: int
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ContentSchema(BaseModel):
    """Schema for content data"""
    id: int
    page: str
    name: str
    kh_title: str
    en_title: str
    kh_content: Optional[str] = None
    en_content: Optional[str] = None
    image: Optional[str] = None
    editor_name: Optional[str] = None
    
    class Config:
        from_attributes = True 