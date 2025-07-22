from pydantic import BaseModel, Field
from typing import List, TypedDict, Optional, Annotated, Dict, Any, Union, Set
from uuid import UUID
from enum import Enum
from datetime import datetime
from decimal import Decimal
from langgraph.graph.message import add_messages, AnyMessage

# app/database/schemas/stock_schema.py

from typing import List, Dict, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str
    code: str
    unit_price: float
    stock: int
    type_id: int  
    creator_id: int  
    discount: float = 0.0
    image: Optional[str] = None  
    created_a: Optional[datetime] = datetime.now()  
    updated_a: Optional[datetime] = datetime.now()  
    
    class Config:
        from_attributes = True
    
class StockData(BaseModel):
    """Stock information for a product"""
    product_id       : int
    code            : str
    name            : str
    current_stock   : int              = Field(default=0, description="Calculated from orders")
    unit_price      : float
    discount        : Decimal
    type_id         : Optional[int]    = None
    type_name       : Optional[str]    = None
    last_order_date : Optional[datetime] = None
    
    class Config:
        from_attributes = True

class StockMovement(BaseModel):
    """Stock movement record"""
    product_id      : int
    order_id        : int
    quantity        : int
    movement_date   : datetime
    unit_price      : float
    
    class Config:
        from_attributes = True

class DailySales(BaseModel):
    """Daily sales record"""
    date            : datetime
    quantity        : int
    revenue         : float

class StockAnalysis(BaseModel):
    """Stock analysis results"""
    product_id      : int
    total_sold      : int
    total_revenue   : float
    average_price   : float
    period_start    : datetime
    period_end      : datetime
    daily_sales     : List[DailySales]
    
    class Config:
        from_attributes = True

class StockSummary(BaseModel):
    """Summary of stock status"""
    total_products  : int
    low_stock_count : int
    out_of_stock    : int
    total_value     : float
    last_update     : datetime
    
    class Config:
        from_attributes = True

class StockUpdateRequest(BaseModel):
    """Request for stock update"""
    product_id      : int
    quantity_change : int
    reason          : Optional[str] = None
    reference_id    : Optional[str] = None

class StockResponse(BaseModel):
    """Generic stock operation response"""
    status          : str
    message         : str
    data            : Optional[Dict[str, StockData]] = None
    analysis        : Optional[StockAnalysis] = None
    summary         : Optional[StockSummary] = None
    
    class Config:
        from_attributes = True