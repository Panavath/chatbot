from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserSchemaIn(BaseModel):
   avatar              : Optional[str] = 'static/avatar.png'
   name                : str
   email               : Optional[EmailStr] = None
   phone               : str
   password            : str
   
   is_active           : Optional[int] = 1
   creator_id          : Optional[int] = None
   updater_id          : Optional[int] = None
   last_login          : Optional[datetime] = None

   class Config:
       from_attributes = True


class UserSchemaOut(BaseModel):
   id                  : int
   avatar              : str
   name                : str
   email               : Optional[EmailStr] = None
   phone               : str

   is_active           : int
   creator_id          : Optional[int] = None
   updater_id          : Optional[int] = None
   last_login          : Optional[datetime] = None
   
   created_at          : datetime
   updated_at          : datetime
   deleted_at          : Optional[datetime] = None

   class Config:
       from_attributes = True