from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel

class TicketCreateRequest(BaseModel):
    message: str
    subject: Optional[str] = None
    customer_id: Optional[str] = None

class TicketMessageCreate(BaseModel):
    message: str

class TicketCreateResponse(BaseModel):
    ticket_id: str
    run_id: str
    status: str
    stream_url: str

class TicketMessageOut(BaseModel):
    id: str
    ticket_id: str
    role: str
    content: str
    citations: Optional[List[Dict[str, Any]]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TicketListItem(BaseModel):
    id: str
    customer_id: str
    subject: Optional[str] = None
    category: Optional[str] = None
    status: str
    last_critic_score: Optional[float] = None
    loops: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TicketListResponse(BaseModel):
    items: List[TicketListItem]
    page: int
    page_size: int
    total: int

class TicketDetailResponse(BaseModel):
    id: str
    customer_id: str
    subject: Optional[str] = None
    category: Optional[str] = None
    status: str
    last_critic_score: Optional[float] = None
    loops: int
    created_at: datetime
    updated_at: datetime
    messages: List[TicketMessageOut]

    class Config:
        from_attributes = True

class TicketEventOut(BaseModel):
    seq: int
    node: str
    event_type: str
    payload: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class RunTraceOut(BaseModel):
    run_id: str
    events: List[TicketEventOut]

class TicketTraceResponse(BaseModel):
    ticket_id: str
    runs: List[RunTraceOut]

class FeedbackRequest(BaseModel):
    message_id: Optional[str] = None
    rating: int  # 1 or -1
    comment: Optional[str] = None
