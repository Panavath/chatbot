#from sqlalchemy.ext.declarative import declarative_base


#Base    = declarative_base()
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr

class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()  # Automatically sets table name

Base = declarative_base(cls=Base)
