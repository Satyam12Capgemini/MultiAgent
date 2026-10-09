import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.models import Escalation, Ticket, TicketMessage, Refund, User
from app.core.errors import NotFoundError, AppError
from app.services.event_emitter import event_emitter

class EscalationService:
    async def list_escalations(
        self,
        session: AsyncSession,
        status: Optional[str] = None
    ) -> List[Escalation]:
        stmt = select(Escalation)
        if status:
            stmt = stmt.where(Escalation.status == status)
        stmt = stmt.order_by(desc(Escalation.created_at))
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_escalation(self, session: AsyncSession, escalation_id: str) -> Dict[str, Any]:
        result = await session.execute(select(Escalation).where(Escalation.id == escalation_id))
        esc = result.scalar_one_or_none()
        if not esc:
            raise NotFoundError(f"Escalation {escalation_id} not found")

        context = json.loads(esc.context_json) if esc.context_json else {}
        return {
            "id": esc.id,
            "ticket_id": esc.ticket_id,
            "reason": esc.reason,
            "summary": esc.summary,
            "context": context,
            "status": esc.status,
            "claimed_by": esc.claimed_by,
            "created_at": esc.created_at,
            "resolved_at": esc.resolved_at
        }

    async def claim_escalation(self, session: AsyncSession, escalation_id: str, agent_id: str) -> Escalation:
        result = await session.execute(select(Escalation).where(Escalation.id == escalation_id))
        esc = result.scalar_one_or_none()
        if not esc:
            raise NotFoundError(f"Escalation {escalation_id} not found")

        esc.claimed_by = agent_id
        esc.status = "claimed"
        await session.commit()
        return esc

    async def reply_to_escalation(
        self,
        session: AsyncSession,
        escalation_id: str,
        agent_id: str,
        message: str,
        resolve: bool = False
    ) -> Escalation:
        result = await session.execute(select(Escalation).where(Escalation.id == escalation_id))
        esc = result.scalar_one_or_none()
        if not esc:
            raise NotFoundError(f"Escalation {escalation_id} not found")

        # 1. Post message to ticket
        human_msg = TicketMessage(
            ticket_id=esc.ticket_id,
            role="human_agent",
            content=message
        )
        session.add(human_msg)

        # 2. Update status
        if resolve:
            esc.status = "resolved"
            esc.resolved_at = datetime.now(timezone.utc)
            # Update ticket status
            t_res = await session.execute(select(Ticket).where(Ticket.id == esc.ticket_id))
            ticket = t_res.scalar_one_or_none()
            if ticket:
                ticket.status = "resolved"

        await session.commit()
        return esc

    async def approve_or_reject_refund(
        self,
        session: AsyncSession,
        escalation_id: str,
        refund_id: str,
        decision: str,
        agent_id: str,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        result = await session.execute(select(Refund).where(Refund.id == refund_id))
        refund = result.scalar_one_or_none()
        if not refund:
            raise NotFoundError(f"Refund {refund_id} not found")

        refund.status = "issued" if decision == "approve" else "rejected"
        refund.approved_by = agent_id

        # Also resolve escalation
        esc_res = await session.execute(select(Escalation).where(Escalation.id == escalation_id))
        esc = esc_res.scalar_one_or_none()
        if esc:
            esc.status = "resolved"
            esc.resolved_at = datetime.now(timezone.utc)

            # Post ticket notification
            decision_text = "approved and processed" if decision == "approve" else "declined"
            sys_msg = TicketMessage(
                ticket_id=esc.ticket_id,
                role="human_agent",
                content=f"Supervisor Update: The refund request for order {refund.order_id} of ₹{refund.amount} has been {decision_text}. {note or ''}"
            )
            session.add(sys_msg)

        await session.commit()
        return {
            "refund_id": refund.id,
            "status": refund.status,
            "decision": decision
        }

escalation_service = EscalationService()
