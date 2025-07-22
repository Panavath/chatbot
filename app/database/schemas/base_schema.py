from uuid import uuid4
from uuid import UUID
from typing import Generic, Optional, TypeVar, Set
from pydantic import BaseModel, Field


DataType = TypeVar("DataType")

def getUUID():
    return str(uuid4())

class Base(BaseModel):

    class Config:
        from_attributes = True
        use_enum_values = True


class IResponseBase(BaseModel, Generic[DataType]):
    log_id  : str = Field(default_factory=getUUID)
    success : int = 1
    code    : str = ''
    message : str = ''
    data    : Optional[DataType] = None

class RequirementCheck(BaseModel):
    """Structure for tracking user requirements"""
    original_query          : str
    identified_requirements : Set[str]
    fulfilled_requirements  : Set[str]
    missing_requirements    : Set[str]
    validation_score        : float = Field(default=0.0, ge=0.0, le=1.0)