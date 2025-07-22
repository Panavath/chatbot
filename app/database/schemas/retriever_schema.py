from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field

from app.database.schemas.document_schema import DocumentChunk

class RetrieverRequest(BaseModel):
    query           : str
    metadata        : Optional[Dict[str, Any]]  = Field(default_factory=dict)
    filters         : Optional[Dict[str, Any]]  = Field(default_factory=dict)
    search_type     : str                       = "similarity"
    top_k           : int                       = 4


class RetrieverResponse(BaseModel):
    query           : str
    documents       : List[DocumentChunk]
    metadata        : Optional[Dict[str, Any]]  = Field(default_factory=dict)


class RetrievalResult(BaseModel):
    request         : RetrieverRequest
    response        : RetrieverResponse
    processing_time : float


class RetrieverConfig(BaseModel):
    embedding_model : str
    chunk_size      : int = 1000
    chunk_overlap   : int = 200
    distance_metric : str = "cosine"
    index_type      : str = "hnsw"
    search_params   : Optional[Dict[str, Any]] = Field(default_factory=dict)



class RetrieverError(BaseModel):
    error_code      : str
    message         : str
    details         : Optional[Dict[str, Any]] = None