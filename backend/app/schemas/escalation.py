from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel

class EscalationListItem(BaseModel):
    id: str
    ticket_id: str
    reason: str
    summary: Optional[str] = None
    status: str
    claimed_by: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EscalationDetailResponse(BaseModel):
    id: str
    ticket_id: str
    reason: str
    summary: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    status: str
    claimed_by: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

class EscalationReplyRequest(BaseModel):
    message: str
    resolve: bool = False

class RefundApprovalRequest(BaseModel):
    refund_id: str
    decision: str  # "approve" or "reject"
    note: Optional[str] = None
