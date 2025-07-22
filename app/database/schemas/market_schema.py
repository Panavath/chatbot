from pydantic import BaseModel, Field
from typing import List, TypedDict, Optional, Annotated, Dict, Any, Union, Set
from uuid import UUID
from enum import Enum
from datetime import datetime
from langgraph.graph.message import add_messages, AnyMessage


class MarketAnalysis(BaseModel):
    market_segment      : str
    timeframe           : str
    metrics             : Dict[str, float]
    insights            : List[str]
