import time
from typing import Dict, Any, Literal
from pydantic import BaseModel, Field
from app.graph.state import TicketState
from app.llm.factory import get_llm_client
from app.services.event_emitter import event_emitter

class ClassificationOutput(BaseModel):
    category: Literal["billing", "tech", "general"] = Field(description="Category of the ticket")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    sentiment: Literal["neutral", "negative", "angry"] = Field(description="Customer sentiment")
    reasoning: str = Field(description="Short rationale for the classification")

CLASSIFIER_PROMPT = """You are a customer support intake classifier.
Classify the user's message into exactly one of: 'billing', 'tech', 'general'.
Also assess sentiment: 'neutral', 'negative', 'angry'.
Return confidence between 0.0 and 1.0. If unsure, choose 'general' with confidence below 0.6.
Respond ONLY as JSON matching the requested schema.
"""

async def classify_node(state: TicketState) -> Dict[str, Any]:
    start_time = time.time()
    seq = state.get("seq", 0) + 1
    ticket_id = state.get("ticket_id", "")
    run_id = state.get("run_id", "")

    # If injection was detected in guard node, skip classification and escalate
    if state.get("injection_detected"):
        duration = int((time.time() - start_time) * 1000)
        await event_emitter.emit(
            ticket_id=ticket_id,
            run_id=run_id,
            seq=seq,
            node="classify",
            event_type="node_completed",
            payload={"category": "general", "confidence": 0.0, "sentiment": "negative", "reason": "Bypassed due to injection flag"},
            duration_ms=duration
        )
        return {
            "seq": seq,
            "category": "general",
            "confidence": 0.0,
            "sentiment": "negative",
            "reasoning": "Prompt injection detected.",
            "route": "escalate"
        }

    llm = get_llm_client()
    masked_text = state.get("masked_text", "")
    history = state.get("messages", [])

    history_str = "\n".join([f"{m.get('role')}: {m.get('content')}" for m in history[-4:]])
    prompt_messages = [
        {"role": "system", "content": CLASSIFIER_PROMPT},
        {"role": "user", "content": f"Conversation history:\n{history_str}\n\nLatest Customer Message:\n{masked_text}"}
    ]

    result: ClassificationOutput = await llm.chat_json(
        prompt_messages,
        ClassificationOutput,
        temperature=0.1,
        ticket_id=ticket_id,
        run_id=run_id,
        node="classify"
    )

    duration = int((time.time() - start_time) * 1000)
    await event_emitter.emit(
        ticket_id=ticket_id,
        run_id=run_id,
        seq=seq,
        node="classify",
        event_type="classified",
        payload={
            "category": result.category,
            "confidence": result.confidence,
            "sentiment": result.sentiment,
            "reasoning": result.reasoning
        },
        duration_ms=duration
    )

    return {
        "seq": seq,
        "category": result.category,
        "confidence": result.confidence,
        "sentiment": result.sentiment,
        "reasoning": result.reasoning
    }
