from datetime import datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel

class ProductTypeSchemaIn(BaseModel):
    name                : str
    image               : Optional[str] = None

    class Config:
        from_attributes = True


class ProductTypeSchemaOut(BaseModel):
    id                  : int
    name                : str
    image               : Optional[str] = None
    created_at          : datetime
    updated_at          : datetime

    class Config:
        from_attributes = True
