from pydantic import BaseModel, Field
from typing import List, TypedDict, Optional, Annotated, Dict, Any, Union, Set
from uuid import UUID
from enum import Enum
from datetime import datetime
from langgraph.graph.message import add_messages, AnyMessage

class TaskType(str, Enum):
    WEB_SEARCH          = "web_search"
    STOCK_CHECK         = "stock_check"
    MARKET_ANALYSIS     = "market_analysis"
    GRAPH_GENERATION    = "graph_generation"
    DATA_VALIDATION     = "data_validation"
    VISION_ANALYSIS     = "vision_analysis"
    KNOWLEDGE_SYNTHESIS = "knowledge_synthesis"


class TaskStatus(str, Enum):
    PENDING             = "pending"
    IN_PROGRESS         = "in_progress"
    COMPLETED           = "completed"
    FAILED              = "failed"
    NEEDS_REFINEMENT    = "needs_refinement"


class TaskResult(BaseModel):
    task_type           : TaskType
    status              : TaskStatus
    message             : str = Field(default="")
    started_at          : datetime
    completed_at        : datetime
    result              : Dict[str, Any] = Field(default_factory=dict)
    error               : Optional[str] = None
    confidence_score    : float = 0.0

    class Config:
        from_attributes = True