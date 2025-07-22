from typing import List, Optional, Dict, Any

from pydantic import BaseModel

class DocumentChunk(BaseModel):
    content             : str
    metadata            : Dict[str, Any]
    score               : Optional[float] = None