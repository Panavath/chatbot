from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OrderDetailSchemaIn(BaseModel):
   order_id            : int
   product_id          : int
   unit_price          : Optional[float] = None
   qty                 : int = 0

   class Config:
       from_attributes = True


class OrderDetailSchemaOut(BaseModel):
   id                  : int
   order_id            : int
   product_id          : int
   unit_price          : float
   qty                 : int
   created_at          : datetime
   updated_at          : datetime

   class Config:
       from_attributes = True