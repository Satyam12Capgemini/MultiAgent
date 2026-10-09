from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel

class KBDocumentOut(BaseModel):
    id: str
    title: str
    category: str
    source: Optional[str] = None
    file_hash: str
    status: str
    error: Optional[str] = None
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class KBChunkOut(BaseModel):
    id: str
    doc_id: str
    chunk_index: int
    text: str
    token_count: int

    class Config:
        from_attributes = True

class KBDocumentDetailResponse(KBDocumentOut):
    chunks: List[KBChunkOut] = []

class KBSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    top_k: int = 4
    mode: str = "hybrid"  # hybrid, vector, bm25

class KBSearchResult(BaseModel):
    chunk_id: str
    doc_id: str
    title: str
    score: float
    vector_score: Optional[float] = None
    bm25_score: Optional[float] = None
    text: str

class KBSearchResponse(BaseModel):
    results: List[KBSearchResult]

class RAGAskRequest(BaseModel):
    question: str
    category: str = "tech"

class RAGCitation(BaseModel):
    n: int
    chunk_id: str
    title: str

class RAGAskResponse(BaseModel):
    answer: str
    citations: List[RAGCitation]
    latency_ms: int
