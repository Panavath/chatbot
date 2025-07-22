from typing import Dict, List, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, desc
from sqlalchemy.exc import SQLAlchemyError

from datetime  import datetime, timedelta
from langchain_core.tools import Tool, ToolException

from app.database.models.product_model import ProductModel
from app.database.models.order_details_model import OrderDetailModel
from app.database.models.product_type_model import ProductTypeModel
from app.database.models.order_model import OrderModel

from app.database.schemas.stock_schema import StockData, StockMovement, StockAnalysis, DailySales
from app.database.schemas.user_schema import UserSchemaIn, UserSchemaOut
from app.database.schemas.stock_schema import ProductCreate

from app import logger

import pandas as pd
import json


class StockTools:
    """Stock management tools for POS system."""
    
    def __init__(
            self
            , db_session  : Session
    ):
        self.db      = db_session
        self.tools   = self._get_tools()
        self.verbose = True

    def _get_tools(self) -> List[Tool]:
        """Initialize available tools."""
        return [
            Tool(
                name="add_product",
                func=self.add_product,
                description=(
                    "Add a new product to the database. "
                    "Args: product_data (ProductCreate)"
                )
            ),
            Tool(
                name="get_total_sales_all_time",
                func=self.get_total_sales_all_time,
                description="Get the total sales amount of all time from orders."
            ),
            Tool(
                name="get_today_sales",
                func=self.get_today_sales,
                description="Get total sales amount for today."
            ),
            Tool(
                name="get_product_stock",
                func=self.get_product_stock,
                description="Get stock information for a specific product. Args: product_id (int)"
            ),
            Tool(
                name="get_all_products_stock",
                func=self.get_all_products_stock,
                description="Get stock information for all products. Optional Args: type_id (int)"
            ),
            Tool(
                name="analyze_product_sales",
                func=self.analyze_product_sales,
                description="Analyze sales history for a product. Args: product_id (int), days (int, optional)"
            ),
            Tool(
                name="check_low_stock_products",
                func=self.check_low_stock_products,
                description="Get products with low stock. Args: threshold (int, optional)"
            ),
            Tool(
                name="get_stock_movements",
                func=self.get_stock_movements,
                description="Get stock movements for a product. Args: product_id (int), days (int)"
            ),
            Tool(
                name="get_role_POS",
                func=self.get_role_POS,
                description="Get role in database. Args: id (int), slug (str)",
            )
        ]
        
    async def add_product(self, product_data: ProductCreate) -> str:
        """Add a new product to the database."""
        try:
            # Create new product instance
            new_product = ProductModel(
                name=product_data.name,
                code=product_data.code,
                unit_price=product_data.unit_price,
                discount=product_data.discount,
                type_id=product_data.type_id,
                creator_id=1  # Set the default creator ID (change if necessary)
            )

            # Add to the session and commit
            self.db.add(new_product)
            self.db.commit()
            self.db.refresh(new_product)

            return f"✅ Product '{new_product.name}' added successfully!"
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding product: {str(e)}")
            return f"❌ Error adding product: {str(e)}"
            
    async def get_total_sales_all_time(self) -> float:
        """Get total sales of all time."""
        try:
            total_sales = (
                self.db.query(func.coalesce(func.sum(OrderModel.total_price), 0))
                .scalar()
            )

            return total_sales

        except Exception as e:
            logger.error(f"Error getting total sales of all time: {str(e)}")
            raise ToolException(str(e))
        
    async def get_today_sales(self) -> float:
        """Get total sales for today."""
        try:
            today = datetime.now().date()
            
            total_sales = (
                self.db.query(func.coalesce(func.sum(OrderDetailModel.qty * OrderDetailModel.unit_price), 0))
                .join(OrderModel, OrderDetailModel.order_id == OrderModel.id)
                .filter(OrderModel.sale_date == today)
                .scalar()
            )

            return total_sales
        
        except Exception as e:
            logger.error(f"Error getting today's sales: {str(e)}")
            raise ToolException(str(e))
        
    async def get_role_POS(
        self,
        id   : int ,
        slug : str
    ) -> UserSchemaIn:
        """Get role information"""
        try:
            role = (
                pd.read_sql_query(self.db.query())
            )
            if not role:
                raise ToolException(f"Role {id} not found")
        except Exception as e:
            logger.error(f"Error getting role user: {str(e)}")
            raise ToolException(str(e))


    async def get_product_stock(
            self
            , product_id : int
    ) -> StockData:
        """Get stock information for a specific product."""
        try:
            product = (
                self.db.query(ProductModel)
                .join(ProductTypeModel)
                .filter(ProductModel.id == product_id)
                .first()
            )
            
            if not product:
                raise ToolException(f"Product {product_id} not found")

            # Get total sold quantity
            total_sold = (
                self.db.query(func.sum(OrderDetailModel.qty))
                .filter(OrderDetailModel.product_id == product_id)
                .scalar() or 0
            )
            
            return StockData(
                product_id        = product.id
                , code            = product.code
                , name            = product.name
                , current_stock   = total_sold
                , unit_price      = product.unit_price
                , discount        = product.discount
                , type_id         = product.type_id
                , type_name       = product.product_type.name if product.product_type else None
                , last_order_date = None  
            )
            
        except Exception as e:
            logger.error(f"Error getting product stock: {str(e)}")
            raise ToolException(str(e))

    async def get_all_products_stock(
            self
            , type_id: Optional[int] = None
    ) -> List[StockData]:
        """Get stock information for all products."""
        try:
            query = (
                self.db.query(
                    ProductModel,
                    ProductTypeModel,
                    func.sum(OrderDetailModel.qty).label('total_sold')
                )
                .join(ProductTypeModel)
                .outerjoin(OrderDetailModel)
                .group_by(ProductModel.id, ProductTypeModel.id)
            )
            
            if type_id:
                query = query.filter(ProductModel.type_id == type_id)
            
            results = query.all()
            
            return [
                StockData(
                    product_id     = product.id
                    , code         = product.code
                    , name         = product.name
                    , current_stock= total_sold or 0
                    , unit_price   = product.unit_price
                    , discount     = product.discount
                    , type_id      = product.type_id
                    , type_name    = product_type.name
                )
                for product, product_type, total_sold in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting all products stock: {str(e)}")
            raise ToolException(str(e))

    async def analyze_product_sales(
            self
            , product_id : int
            , days      : int = 30
    ) -> StockAnalysis:
        """Analyze sales history for a product."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            orders      = (
                self.db.query(OrderDetailModel)
                .filter(
                    and_(
                        OrderDetailModel.product_id == product_id,
                        OrderDetailModel.created_at >= cutoff_date
                    )
                )
                .all()
            )
            
            if not orders:
                return StockAnalysis(
                    product_id      = product_id
                    , total_sold    = 0
                    , total_revenue = 0.0
                    , average_price = 0.0
                    , period_start  = cutoff_date
                    , period_end    = datetime.now()
                    , daily_sales   = []
                )
            

            daily_sales_dict    = {}
            total_revenue       = 0.0
            total_sold          = 0
            
            for order in orders:
                date            = order.created_at.date()
                revenue         = order.qty * order.unit_price
                
                if date not in daily_sales_dict:
                    daily_sales_dict[date] = DailySales(
                        date     = datetime.combine(date, datetime.min.time()),
                        quantity = 0,
                        revenue  = 0.0
                    )
                
                daily_sales_dict[date].quantity += order.qty
                daily_sales_dict[date].revenue += revenue
                total_revenue += revenue
                total_sold += order.qty
            
            daily_sales = sorted(daily_sales_dict.values(), key=lambda x: x.date)
            
            return StockAnalysis(
                product_id      = product_id
                , total_sold    = total_sold
                , total_revenue = total_revenue
                , average_price = total_revenue / total_sold if total_sold > 0 else 0.0
                , period_start  = cutoff_date
                , period_end    = datetime.now()
                ,daily_sales    = daily_sales
            )
            
        except Exception as e:
            logger.error(f"Error analyzing product sales: {str(e)}")
            raise ToolException(str(e))

    async def check_low_stock_products(
            self
            , threshold: int = 10
    ) -> List[StockData]:
        """Get list of products with low stock."""
        try:
            products = (
                self.db.query(ProductModel)
                .join(ProductTypeModel)
                .all()
            )
            
            results = []
            for product in products:
                stock_data = StockData(
                    product_id      = product.id
                    , code          = product.code
                    , name          = product.name
                    , current_stock = 0  # Default value
                    , unit_price    = product.unit_price
                    , discount      = product.discount
                    , type_id       = product.type_id
                    , type_name     = product.product_type.name if product.product_type else None
                )
                results.append(stock_data)
                
            return results
            
        except Exception as e:
            logger.error(f"Error checking low stock products: {str(e)}")
            raise ToolException(str(e))

    async def get_stock_movements(
            self
            , product_id : int
            , days      : int = 30
    ) -> List[StockMovement]:
        """Get stock movement history."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            movements = (
                self.db.query(OrderDetailModel)
                .filter(
                    and_(
                        OrderDetailModel.product_id == product_id,
                        OrderDetailModel.created_at >= cutoff_date
                    )
                )
                .order_by(OrderDetailModel.created_at.desc())
                .all()
            )
            
            return [
                StockMovement(
                    product_id       = movement.product_id
                    , order_id        = movement.order_id
                    , quantity        = movement.qty
                    , movement_date   = movement.created_at
                    , unit_price      = movement.unit_price
                )
                for movement in movements
            ]
            
        except Exception as e:
            logger.error(f"Error getting stock movements: {str(e)}")
            raise ToolException(str(e))