import json
import time
from typing import Dict, Any
from sqlalchemy import select
from app.graph.state import TicketState
from app.db.session import AsyncSessionLocal
from app.db.models import Ticket, TicketMessage
from app.guardrails.policy import policy_enforcer
from app.services.event_emitter import event_emitter
from app.llm.factory import get_llm_client

async def finalize_node(state: TicketState) -> Dict[str, Any]:
    start_time = time.time()
    seq = state.get("seq", 0) + 1
    ticket_id = state.get("ticket_id", "")
    run_id = state.get("run_id", "")
    raw_answer = state.get("answer", "")
    citations = state.get("citations", [])
    has_refund = state.get("pending_refund") is not None or "refund" in raw_answer.lower()

    # Apply output policy sanitize guardrail
    clean_answer = policy_enforcer.sanitize_output(raw_answer, has_refund_tool_result=has_refund)

    # Stream final tokens
    llm = get_llm_client()
    words = clean_answer.split(" ")
    for i, word in enumerate(words):
        token_str = word + (" " if i < len(words) - 1 else "")
        await event_emitter.emit(
            ticket_id=ticket_id,
            run_id=run_id,
            seq=seq,
            node="finalize",
            event_type="token",
            payload={"text": token_str}
        )

    # Persist assistant message and update ticket
    message_id = None
    async with AsyncSessionLocal() as session:
        msg = TicketMessage(
            ticket_id=ticket_id,
            role="assistant",
            content=clean_answer,
            citations=json.dumps(citations) if citations else None
        )
        session.add(msg)

        result = await session.execute(select(Ticket).where(Ticket.id == ticket_id))
        ticket = result.scalar_one_or_none()
        if ticket:
            ticket.status = "answered"
            ticket.category = state.get("category", ticket.category)
            ticket.last_critic_score = state.get("critic_score")
            ticket.loops = state.get("loops", 0)

        await session.commit()
        message_id = msg.id

    duration = int((time.time() - start_time) * 1000)
    await event_emitter.emit(
        ticket_id=ticket_id,
        run_id=run_id,
        seq=seq,
        node="finalize",
        event_type="final",
        payload={"message_id": message_id, "answer": clean_answer, "citations": citations},
        duration_ms=duration
    )
    await event_emitter.emit(
        ticket_id=ticket_id,
        run_id=run_id,
        seq=seq + 1,
        node="finalize",
        event_type="done",
        payload={}
    )

    return {
        "seq": seq + 1,
        "final_answer": clean_answer
    }
