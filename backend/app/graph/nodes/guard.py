import time
from typing import Dict, Any
from app.graph.state import TicketState
from app.guardrails.pii import pii_masker
from app.guardrails.injection import injection_detector
from app.services.event_emitter import event_emitter

async def guard_node(state: TicketState) -> Dict[str, Any]:
    start_time = time.time()
    seq = state.get("seq", 0) + 1
    ticket_id = state.get("ticket_id", "")
    run_id = state.get("run_id", "")

    # Extract latest customer message content
    messages = state.get("messages", [])
    raw_message = ""
    for m in reversed(messages):
        if m.get("role") == "customer":
            raw_message = m.get("content", "")
            break

    # PII Masking
    masked_text, pii_types = pii_masker.mask(raw_message)

    # Prompt Injection Scan
    is_injection, flagged = injection_detector.detect(raw_message)

    duration = int((time.time() - start_time) * 1000)
    await event_emitter.emit(
        ticket_id=ticket_id,
        run_id=run_id,
        seq=seq,
        node="guard",
        event_type="node_completed",
        payload={"pii_masked": pii_types, "injection_detected": is_injection},
        duration_ms=duration
    )

    return {
        "seq": seq,
        "masked_text": masked_text,
        "injection_detected": is_injection,
        "escalation_reason": "prompt_injection_detected" if is_injection else None
    }
