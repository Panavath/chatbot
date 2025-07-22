from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OrderSchemaIn(BaseModel):
    cashier_id          : Optional[int] = None
    receipt_number      : int
    total_price         : Optional[float] = None
    ordered_at          : Optional[datetime] = None
    platform            : Optional[str] = 'Web'

    class Config:
        from_attributes = True


class OrderSchemaOut(BaseModel):
    id                  : int
    cashier_id          : Optional[int] = None
    receipt_number      : int
    total_price         : Optional[float] = None
    ordered_at          : datetime
    platform            : str
    created_at          : datetime
    updated_at          : datetime

    class Config:
        from_attributes = True