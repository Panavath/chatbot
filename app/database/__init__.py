from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.database.models.base_model import Base

from app.core.config import settings

from app.database.models.order_model import OrderModel
from app.database.models.order_details_model import OrderDetailModel
from app.database.models.product_model import ProductModel
from app.database.models.product_type_model import ProductTypeModel

#DATABASE_URL = f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
#DATABASE_URL = f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
DATABASE_URL = f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
#DATABASE_URL = f"mysql+postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
#DATABASE_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"


engine      = create_engine(
    DATABASE_URL
    , pool_pre_ping = True
    , pool_size     = 5
    , max_overflow  = 10
    , pool_timeout  = 30
    , pool_recycle  = 1800
)

SessionLocal    = sessionmaker(
    autocommit  = False
    , autoflush = False
    , bind      = engine
)

def get_db():
    db  = SessionLocal()
    try:
        yield db
    finally:
        db.close()