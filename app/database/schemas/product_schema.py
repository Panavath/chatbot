from datetime import datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel

class ProductSchemaIn(BaseModel):
    type_id             : Optional[int] = None
    creator_id          : Optional[int] = None
    code                : str
    name                : str
    image               : Optional[str] = None
    unit_price          : Optional[float] = None
    discount            : Optional[Decimal] = 0

    class Config:
        from_attributes = True


class ProductSchemaOut(BaseModel):
    id                  : int
    type_id             : Optional[int] = None
    creator_id          : Optional[int] = None
    code                : str
    name                : str
    image               : Optional[str] = None
    unit_price          : float
    discount            : Decimal
    created_at          : datetime
    updated_at          : datetime

    class Config:
        from_attributes = True