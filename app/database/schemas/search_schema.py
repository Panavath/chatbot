from pydantic import BaseModel, Field
from typing import List, TypedDict, Optional, Annotated, Dict, Any, Union, Set
from uuid import UUID
from enum import Enum
from datetime import datetime
from langgraph.graph.message import add_messages, AnyMessage

class SearchResult(BaseModel):
    query           : str
    results         : List[Dict[str, Any]]
    timestamp       : datetime
    relevance_score : float
