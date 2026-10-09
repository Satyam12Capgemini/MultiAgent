from typing import Literal
from app.graph.state import TicketState
from app.core.config import settings

def route_after_classify(state: TicketState) -> str:
    """
    Evaluates confidence, sentiment, and category after the classify node.
    """
    if state.get("escalation_reason"):
        return "escalate"

    if state.get("confidence", 1.0) < settings.CLASSIFY_MIN_CONF:
        return "escalate"

    if state.get("sentiment") == "angry":
        return "escalate"

    cat = state.get("category")
    if cat in ("billing", "tech", "general"):
        return cat

    return "escalate"

def route_after_critic(state: TicketState) -> str:
    """
    Evaluates critic score and loop counts.
    """
    if state.get("escalation_reason"):
        return "escalate"

    score = state.get("critic_score", 0.0)
    loops = state.get("loops", 0)

    if score >= settings.CRITIC_PASS_SCORE:
        return "finalize"

    if loops >= settings.MAX_CRITIC_LOOPS:
        return "escalate"

    cat = state.get("category", "general")
    return f"retry_{cat}"
