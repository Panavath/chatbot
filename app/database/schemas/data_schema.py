from pydantic import BaseModel, Field
from typing import List, TypedDict, Optional, Annotated, Dict, Any, Union, Set
from uuid import UUID
from enum import Enum
from datetime import datetime
from langgraph.graph.message import add_messages, AnyMessage


class ValidationResult(BaseModel):
    is_complete         : bool
    missing_information : List[str]
    confidence_score    : float
    suggested_actions   : List[str]
