from datetime import datetime

from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.models.base_model import Base

# class UserModel(Base):
#     __tablename__ = "users"  # Changed from "user" to "users" for consistency

#     id          = Column(Integer, primary_key=True, index=True)
#     name        = Column(String(50), nullable=False)
#     email       = Column(String(100), unique=True, nullable=False)
#     phone       = Column(String(100), nullable=False)
#     password    = Column(String(100), nullable=False)
#     is_active   = Column(Integer, default=1)

#     # Self-referencing FK for creator and updater
#     creator_id  = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"))
#     updater_id  = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"))

#     last_login  = Column(DateTime, default=datetime.utcnow)
#     created_at  = Column(DateTime, default=datetime.utcnow)
#     updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     deleted_at  = Column(DateTime, nullable=True)

#     # Relationships
#     products    = relationship("ProductModel", back_populates="creator")
#     orders      = relationship("OrderModel", back_populates="cashier")

#     created_users = relationship("UserModel", backref="creator", remote_side=[id], foreign_keys=[creator_id])
#     updated_users = relationship("UserModel", backref="updater", remote_side=[id], foreign_keys=[updater_id])

#     def __repr__(self):
#         return f"<User {self.name}>"
    

class UserModel(Base):
   __tablename__       = "user"

   id                  = Column(Integer, primary_key=True, index=True)
   avatar              = Column(String(200), default='static/avatar.png')
   name                = Column(String(50), nullable=False)
   email               = Column(String(100))
   phone               = Column(String(100), nullable=False)
   password            = Column(String(100), nullable=False)

   is_active           = Column(Integer, nullable=False, default=1)
   creator_id          = Column(Integer, ForeignKey("user.id", onupdate="CASCADE", ondelete="SET NULL"))
   updater_id          = Column(Integer, ForeignKey("user.id", onupdate="CASCADE", ondelete="SET NULL"))
   
   last_login          = Column(DateTime(timezone=True), default=datetime.utcnow)
   created_at          = Column(DateTime(timezone=True), nullable=False)
   updated_at          = Column(DateTime(timezone=True), nullable=False)
   deleted_at          = Column(DateTime(timezone=True), nullable=True)

   # Relationships
   products             = relationship("ProductModel", back_populates="creator")
   orders               = relationship("OrderModel", back_populates="cashier")
   created_users        = relationship("UserModel", 
                                   backref="creator",
                                   remote_side=[id],
                                   foreign_keys=[creator_id])
   updated_users        = relationship("UserModel",
                                   backref="updater",
                                   remote_side=[id],
                                   foreign_keys=[updater_id])

   def __repr__(self):
       return f"<User {self.name}>"