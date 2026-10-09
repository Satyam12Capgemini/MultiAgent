import time
from typing import Dict, Any, List, Literal
from pydantic import BaseModel, Field
from app.graph.state import TicketState
from app.llm.factory import get_llm_client
from app.rag.retriever import retriever
from app.services.event_emitter import event_emitter

class ClaimVerdict(BaseModel):
    text: str = Field(description="The atomic claim extracted from the answer")
    verdict: Literal["SUPPORTED", "PARTIAL", "UNSUPPORTED"] = Field(description="Verdict based on context")
    source: str = Field(default="", description="Citation source marker e.g. [1]")

class CriticOutput(BaseModel):
    claims: List[ClaimVerdict] = Field(default_factory=list, description="List of atomic claims and verdicts")
    feedback: List[str] = Field(default_factory=list, description="Actionable points to fix unsupported claims")

CRITIC_PROMPT = """You are a strict grounding critic and fact-checker.
Compare the generated draft answer against the provided context.
Break the answer into atomic factual claims.
For each claim, determine if it is:
- 'SUPPORTED': Fully stated or logically entailed by the context chunks.
- 'PARTIAL': Partially true but lacks full detail or citation.
- 'UNSUPPORTED': Extrapolated, assumed, or contradicted by the context.

Return ONLY JSON matching the schema:
{
  "claims": [{"text": "...", "verdict": "SUPPORTED|PARTIAL|UNSUPPORTED", "source": "[1]"}],
  "feedback": ["actionable correction 1", "actionable correction 2"]
}
"""

async def critic_node(state: TicketState) -> Dict[str, Any]:
    start_time = time.time()
    seq = state.get("seq", 0) + 1
    ticket_id = state.get("ticket_id", "")
    run_id = state.get("run_id", "")
    loops = state.get("loops", 0) + 1
    answer = state.get("answer", "")
    retrieved = state.get("retrieved", [])
    category = state.get("category", "general")

    # If billing node handled an action or refund, score is 1.0
    if category == "billing":
        duration = int((time.time() - start_time) * 1000)
        await event_emitter.emit(
            ticket_id=ticket_id,
            run_id=run_id,
            seq=seq,
            node="critic",
            event_type="critic_scored",
            payload={"loop": loops, "score": 1.0, "unsupported_claims": [], "feedback": []},
            duration_ms=duration
        )
        return {
            "seq": seq,
            "loops": loops,
            "critic_score": 1.0,
            "critic_feedback": []
        }

    # If agent responded that it does not have enough information
    if "not have enough information" in answer.lower():
        duration = int((time.time() - start_time) * 1000)
        await event_emitter.emit(
            ticket_id=ticket_id,
            run_id=run_id,
            seq=seq,
            node="critic",
            event_type="critic_scored",
            payload={"loop": loops, "score": 1.0, "unsupported_claims": [], "feedback": []},
            duration_ms=duration
        )
        return {
            "seq": seq,
            "loops": loops,
            "critic_score": 1.0,
            "critic_feedback": []
        }

    context_str = retriever.build_context_block(retrieved)
    messages = [
        {"role": "system", "content": CRITIC_PROMPT},
        {"role": "user", "content": f"Context:\n{context_str}\n\nDraft Answer:\n{answer}"}
    ]

    llm = get_llm_client()
    result: CriticOutput = await llm.chat_json(
        messages,
        CriticOutput,
        temperature=0.1,
        ticket_id=ticket_id,
        run_id=run_id,
        node="critic"
    )

    # Compute grounded score deterministically in code from per-claim verdicts
    if not result.claims:
        score = 0.5
        unsupported = ["No verifiable claims found in draft."]
    else:
        total_points = 0.0
        unsupported = []
        for claim in result.claims:
            if claim.verdict == "SUPPORTED":
                total_points += 1.0
            elif claim.verdict == "PARTIAL":
                total_points += 0.5
                unsupported.append(claim.text)
            else:
                unsupported.append(claim.text)
        score = total_points / len(result.claims)

    duration = int((time.time() - start_time) * 1000)
    await event_emitter.emit(
        ticket_id=ticket_id,
        run_id=run_id,
        seq=seq,
        node="critic",
        event_type="critic_scored",
        payload={
            "loop": loops,
            "score": round(score, 2),
            "unsupported_claims": unsupported,
            "feedback": result.feedback
        },
        duration_ms=duration
    )

    return {
        "seq": seq,
        "loops": loops,
        "critic_score": score,
        "critic_feedback": result.feedback
    }
