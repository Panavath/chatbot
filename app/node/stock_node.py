from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
import re

from sqlalchemy.orm import Session

from app.database.schemas.task_schema import TaskType, TaskResult, TaskStatus
from app.database.schemas.assistant_schema import AssistantState
from app.database.schemas.stock_schema import ProductCreate

from pydantic import ValidationError
from app.tools.stock_tools import StockTools
from app import logger


class StockNode:
    """Node for handling stock operations in LangGraph workflow."""
    
    def __init__(
            self
            , llm         : Any
            , db_session  : Session
            , stock_tools : StockTools
            , verbose     : bool = True
            
    ):
        self.llm        = llm
        self.db         = db_session
        self.stock_tools = stock_tools
        self.tools      = StockTools(db_session)
        self.verbose    = verbose

    def _create_error_state(
            self
            , state: AssistantState
            , error_message: str
            , start_time: datetime
    ) -> AssistantState:
        """Helper to create error state."""
        return {
            **state,
            "task_results": {
                TaskType.STOCK_CHECK: TaskResult(
                    task_type             = TaskType.STOCK_CHECK
                    , status              = TaskStatus.FAILED
                    , message             = error_message
                    , started_at          = start_time
                    , completed_at        = datetime.now()
                    , result              = {}
                    , error               = error_message
                    , confidence_score    = 0.0
                )
            }
        }

    def extract_product_info(self, message: str) -> Dict[str, Any]:
        """Extract product information from message."""
        message = message.lower()
        
        code_match = re.search(r'\b([A-B][0-9]{3,4})\b', message)
        if code_match:
            return {"code": code_match.group(1)}

        patterns = [
            r'level of\s+([^(]+?)(?:\s*\(|$)', 
            r'stock of\s+([^(]+?)(?:\s*\(|$)', 
            r'about\s+([^(]+?)(?:\s*\(|$)',     
            r'check\s+([^(]+?)\s*stock',        
            r'have\s+([^(]+?)\s*in stock'       
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                product_name = match.group(1).strip()
                product_name = re.sub(r'\b(the|any|some|our)\b', '', product_name).strip()
                if product_name:
                    return {"name": product_name}

        # Check for special queries
        if "all products" in message:
            return {"query_type": "all"}
        elif "low stock" in message:
            return {"query_type": "low_stock"}
        elif "total sales all time" in message or "total revenue" in message or "all time sales" in message:
            return {"query_type": "total_sales_all_time"}
            
        return {"query_type": "unknown"}
    
    def extract_product_details_from_message(self, message: str) -> Optional[ProductCreate]:
        """
        Extract product details from chat message and return a ProductCreate object.
        """
        try:
            name_match = re.search(r'name[:\-]\s*([^\n,]+)', message, re.IGNORECASE)
            code_match = re.search(r'code[:\-]\s*([^\n,]+)', message, re.IGNORECASE)
            price_match = re.search(r'price[:\-]\s*([\d.]+)', message, re.IGNORECASE)
            stock_match = re.search(r'stock[:\-]\s*(\d+)', message, re.IGNORECASE)
            type_id_match = re.search(r'type_id[:\-]\s*(\d+)', message, re.IGNORECASE)
            creator_match = re.search(r'creator_id[:\-]\s*(\d+)', message, re.IGNORECASE)  # ✅ Added creator_ic
            discount_match = re.search(r'discount[:\-]\s*([\d.]+)', message, re.IGNORECASE)
            image_match = re.search(r'image[:\-]\s*(https?://[^\s]+)', message, re.IGNORECASE)  # ✅ Added image URL

            # Check required fields
            if not (name_match and code_match and price_match and stock_match and type_id_match and creator_match):
                raise ValueError("Missing required product details (name, code, price, stock, type_id, creator_id).")

            product_data = ProductCreate(
                name=name_match.group(1).strip(),
                code=code_match.group(1).strip(),
                unit_price=float(price_match.group(1)),
                stock=int(stock_match.group(1)),
                type_id=int(type_id_match.group(1)),  # ✅ Fixed type_ic
                creator_id=int(creator_match.group(1)),  # ✅ Added creator_id
                discount=Decimal(discount_match.group(1)) if discount_match else Decimal(0),
                image=image_match.group(1) if image_match else None,  # ✅ Optional image
                created_a=datetime.now(),  # ✅ Auto timestamp
                updated_a=datetime.now(),  # ✅ Auto timestamp
            )
            return product_data

        except (ValueError, ValidationError) as e:
            logger.error(f"Product extraction failed: {str(e)}")
            return None

    async def __call__(
            self
            , state    : AssistantState
            , config   : Optional[Dict[str, Any]] = None
    ) -> AssistantState:
        """Process stock-related operations in the workflow."""
        start_time = datetime.now()
        
        try:
            messages = state.get("messages", [])
            current_message = messages[-1] if messages else None
            
            if not current_message:
                return self._create_error_state(
                    state,
                    "No message found in state",
                    start_time
                )

            product_info            = self.extract_product_info(current_message.content)
            
            try:
                stock_data          = {}
                message             = "Stock check completed successfully." # Default message 
                
                if product_info.get("code"):
                    product         = await self.tools.get_product_stock(product_info["code"])
                    if product:
                        stock_data  = {product_info["code"]: product.dict()}
                        message     = f"Stock info for {product_info['code']} retrieved successfully."
                
                elif product_info.get("name"):

                    products = await self.tools.get_all_products_stock()
                    stock_data = {
                        p.code: p.dict() 
                        for p in products 
                        if product_info["name"].lower() in p.name.lower()
                    }
                    message = f"Stock info for '{product_info['name']}' retrieved successfully."
                
                elif product_info.get("query_type") == "all":

                    products        = await self.tools.get_all_products_stock()
                    stock_data      = {p.code: p.dict() for p in products}
                    message         = "Retrieved all product stocks successfully."
                
                elif product_info.get("query_type") == "low_stock":

                    products        = await self.tools.check_low_stock_products()
                    stock_data      = {p.code: p.dict() for p in products}
                    message         = f"Retrieved low stock products. Total: {len(stock_data)}."

                    
                elif product_info.get("query_type") == "total_sales_all_time":
                    total_sales = await self.tools.get_total_sales_all_time()
                    stock_data  = {"total_sales_all_time": total_sales}
                    message     = f"Total sales all time: <span style='color:green;'>${total_sales:,.2f}</span>"
                    
                elif product_info.get("query_type") == "add_product":
                    # Extract details
                    product_data = self.extract_product_details_from_message(current_message.content)

                    if product_data:
                        result = await self.tools.add_product(product_data)
                        stock_data = {"add_product_result": result}
                        message = result
                    else:
                        message = "❌ Could not extract product details. Please provide details like: \
                            `Name: Coffee, Code: C125, Price: 5000, Type: Beverage, Discount: 0.10`"


                
                else:

                    products = await self.tools.check_low_stock_products()
                    stock_data = {p.code: p.dict() for p in products}
                return {
                    **state,
                    "task_results": {
                        TaskType.STOCK_CHECK: TaskResult(
                            task_type           = TaskType.STOCK_CHECK
                            , status            = TaskStatus.COMPLETED
                            ,message            = message
                            , started_at        = start_time
                            , completed_at      = datetime.now()
                            , result            = {"stock_data": stock_data}
                            , error             = None
                            , confidence_score  = 1.0
                        )
                    },
                    "stock_data": stock_data
                }
                
            except Exception as e:
                logger.error(f"Error in stock operation: {str(e)}")
                return self._create_error_state(
                    state
                    , f"Error in stock operation: {str(e)}"
                    , start_time
                )
                
        except Exception as e:
            logger.error(f"Error in stock node: {str(e)}")
            return self._create_error_state(
                state
                , f"Error in stock node: {str(e)}"
                , start_time
            )