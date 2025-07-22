from pydantic import BaseModel, Field
from typing import List, TypedDict, Optional, Annotated, Dict, Any
from uuid import UUID
from datetime import datetime

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages, AnyMessage

from typing_extensions import TypedDict, Annotated

from app.database.schemas.base_schema import RequirementCheck
from app.database.schemas.data_schema import ValidationResult
from app.database.schemas.task_schema import TaskType, TaskResult
from app.database.schemas.search_schema import SearchResult
from app.database.schemas.stock_schema import StockData
from app.database.schemas.market_schema import MarketAnalysis


class AssistantState(TypedDict, total=False):
    """Base Assistant State"""
    messages                    : Annotated[List[BaseMessage], add_messages]
    context                     : str
    current_tasks               : List[TaskType]
    task_results                : Dict[TaskType, TaskResult]
    requirements                : RequirementCheck
    search_results              : List[SearchResult]
    stock_data                  : Optional[Dict[str, StockData]]
    market_analysis             : Optional[MarketAnalysis]
    validation_result           : Optional[ValidationResult]
    conversation_context        : Dict[str, Any]
    thread_id                   : Optional[UUID]
    last_validation_time        : Optional[datetime]
    processing_metadata         : Dict[str, Any]

    vision_data                 : Optional[Dict[str, Any]]
    vision_analysis             : Optional[Dict[str, Any]]
    extracted_text              : Optional[Dict[str, Any]]
class AssistantRequest(BaseModel):
    """Schema for chat request"""
    messages        : str               = Field(..., description="The message from the user")
    thread_id       : Optional[str]     = Field(None, description="Thread ID for conversation tracking")
    image_data      : Optional[bytes]    = Field(None, description="Binary image data if an image is uploaded")
    image_type      : Optional[str]      = Field(None, description="MIME type of the uploaded image")

    class Config:
        arbitrary_types_allowed = True

class AssistantResponseData(BaseModel):
    """Schema for assistant response data"""
    response        : str               = Field(..., description="The assistant's response")
    thread_id       : Optional[str]     = Field(None, description="Thread ID for conversation tracking")
    processing_time : float             = Field(..., description="Time taken to process request")
    confidence_score: float             = Field(default=1.0, description="Confidence score of the response")
    visual_context  : Optional[Dict]    = Field(None, description="Context from image analysis if any")


class AssistantResponse(BaseModel):
    """Schema for assistant response"""
    status                  : bool = Field(True, description="Operation status")
    data                    : Optional[AssistantResponseData] = Field(None, description="Response data")
    validation_results      : Optional[Dict[str, Any]] = Field(None, description="Validation details")
    fallback_suggestions    : Optional[List[str]] = Field(None, description="Fallback suggestions")

    class Config:
        arbitrary_types_allowed = True

class AssistantErrorResponse(BaseModel):
    """Schema for error responses"""
    error                   : List[str] = Field(..., description="Error messages")
    details                 : Optional[str] = Field(None, description="Error details")
    recovery_suggestions    : Optional[List[str]] = Field(None, description="Recovery suggestions")