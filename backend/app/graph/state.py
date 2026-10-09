from typing import TypedDict, Literal, Annotated, List, Dict, Any, Optional
from operator import add

class RetrievedChunk(TypedDict):
    chunk_id: str
    doc_id: str
    title: str
    text: str
    score: float

class TicketState(TypedDict, total=False):
    ticket_id: str
    thread_id: str
    customer_id: str
    run_id: str
    seq: int
    messages: Annotated[List[Dict[str, Any]], add]   # conversation history
    masked_text: str                                  # PII-masked latest user message
    injection_detected: bool
    category: Literal["billing", "tech", "general"]
    confidence: float
    reasoning: str
    sentiment: Literal["neutral", "negative", "angry"]
    route: Literal["billing", "tech", "general", "escalate"]
    retrieved: List[RetrievedChunk]
    answer: str
    citations: List[Dict[str, Any]]
    critic_score: float
    critic_feedback: List[str]
    loops: int
    escalation_reason: Optional[str]
    pending_refund: Optional[Dict[str, Any]]
    final_answer: Optional[str]
