from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import User
from app.schemas.escalation import (
    EscalationListItem, EscalationDetailResponse, EscalationReplyRequest, RefundApprovalRequest
)
from app.services.escalation_service import escalation_service
from app.api.deps import require_roles, get_current_user

router = APIRouter()

@router.get("", response_model=List[EscalationListItem])
async def list_escalations(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["agent", "admin"]))
):
    items = await escalation_service.list_escalations(db, status=status)
    return [EscalationListItem.model_validate(item) for item in items]

@router.get("/{escalation_id}", response_model=EscalationDetailResponse)
async def get_escalation(
    escalation_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["agent", "admin"]))
):
    data = await escalation_service.get_escalation(db, escalation_id)
    return EscalationDetailResponse.model_validate(data)

@router.post("/{escalation_id}/claim", response_model=EscalationListItem)
async def claim_escalation(
    escalation_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["agent", "admin"]))
):
    item = await escalation_service.claim_escalation(db, escalation_id, user.id)
    return EscalationListItem.model_validate(item)

@router.post("/{escalation_id}/reply", response_model=EscalationListItem)
async def reply_escalation(
    escalation_id: str,
    req: EscalationReplyRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["agent", "admin"]))
):
    item = await escalation_service.reply_to_escalation(
        session=db,
        escalation_id=escalation_id,
        agent_id=user.id,
        message=req.message,
        resolve=req.resolve
    )
    return EscalationListItem.model_validate(item)

@router.post("/{escalation_id}/approve-refund")
async def approve_refund(
    escalation_id: str,
    req: RefundApprovalRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["agent", "admin"]))
):
    res = await escalation_service.approve_or_reject_refund(
        session=db,
        escalation_id=escalation_id,
        refund_id=req.refund_id,
        decision=req.decision,
        agent_id=user.id,
        note=req.note
    )
    return res
