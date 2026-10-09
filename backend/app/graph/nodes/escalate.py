import json
import time
from typing import Dict, Any
from sqlalchemy import select
from app.graph.state import TicketState
from app.db.session import AsyncSessionLocal
from app.db.models import Ticket, Escalation, TicketMessage
from app.services.event_emitter import event_emitter

async def escalate_node(state: TicketState) -> Dict[str, Any]:
    start_time = time.time()
    seq = state.get("seq", 0) + 1
    ticket_id = state.get("ticket_id", "")
    run_id = state.get("run_id", "")
    reason = state.get("escalation_reason") or "human_intervention_required"
    
    # Check fallback reasons
    if state.get("loops", 0) >= 3:
        reason = "critic_cap_reached"
    elif state.get("confidence", 1.0) < 0.6:
        reason = "low_classifier_confidence"
    elif state.get("sentiment") == "angry":
        reason = "angry_customer_sentiment"

    summary = f"Ticket escalated to human specialist. Reason: {reason}."
    context_data = {
        "category": state.get("category"),
        "confidence": state.get("confidence"),
        "sentiment": state.get("sentiment"),
        "reasoning": state.get("reasoning"),
        "last_draft": state.get("answer"),
        "critic_score": state.get("critic_score"),
        "retrieved_chunks": state.get("retrieved", []),
        "pending_refund": state.get("pending_refund")
    }

    escalation_id = None
    async with AsyncSessionLocal() as session:
        # 1. Create Escalation record
        escalation = Escalation(
            ticket_id=ticket_id,
            reason=reason,
            summary=summary,
            context_json=json.dumps(context_data),
            status="open"
        )
        session.add(escalation)

        # 2. Update Ticket status
        result = await session.execute(select(Ticket).where(Ticket.id == ticket_id))
        ticket = result.scalar_one_or_none()
        if ticket:
            ticket.status = "escalated"
            ticket.category = state.get("category", ticket.category)
            ticket.last_critic_score = state.get("critic_score")
            ticket.loops = state.get("loops", 0)

        # 3. Add system message informing customer
        customer_msg = "Your request has been escalated to a human support specialist with your full context. An agent will connect shortly."
        sys_msg = TicketMessage(
            ticket_id=ticket_id,
            role="assistant",
            content=customer_msg
        )
        session.add(sys_msg)
        await session.commit()
        escalation_id = escalation.id

    duration = int((time.time() - start_time) * 1000)
    await event_emitter.emit(
        ticket_id=ticket_id,
        run_id=run_id,
        seq=seq,
        node="escalate",
        event_type="escalated",
        payload={"reason": reason, "escalation_id": escalation_id, "summary": summary},
        duration_ms=duration
    )
    await event_emitter.emit(
        ticket_id=ticket_id,
        run_id=run_id,
        seq=seq + 1,
        node="escalate",
        event_type="done",
        payload={}
    )

    return {
        "seq": seq + 1,
        "final_answer": "Your request has been escalated to a human support specialist.",
        "escalation_reason": reason
    }
