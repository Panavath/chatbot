from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models to ensure Alembic detects them
from .user_model import UserModel
from .order_model import OrderModel
from .order_details_model import OrderDetailModel
from .product_model import ProductModel
from .product_type_model import ProductTypeModel
from .minister_model import MinisterModel
from .sub_org_model import SubOrgModel
from .content_model import ContentModel
from .title_model import TitleModel

# Expose models so Alembic detects them
__all__ = [
    "Base",
    "UserModel",
    "OrderModel",
    "OrderDetailModel",
    "ProductModel",
    "ProductTypeModel",
    "MinisterModel",
    "SubOrgModel",
    "ContentModel",
    "TitleModel",
]
