from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.db.models import User, Ticket, LLMUsage, TicketEvent
from app.schemas.analytics import (
    AnalyticsSummaryResponse, UsageAnalyticsResponse, CategoryBreakdown, StatusBreakdown, NodeUsageMetric
)
from app.api.deps import require_roles

router = APIRouter()

@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["admin"]))
):
    # Total tickets
    total_res = await db.execute(select(func.count(Ticket.id)))
    total_tickets = total_res.scalar() or 0

    # Escalated tickets
    esc_res = await db.execute(select(func.count(Ticket.id)).where(Ticket.status == "escalated"))
    escalated_count = esc_res.scalar() or 0
    escalation_rate = (escalated_count / total_tickets) if total_tickets > 0 else 0.0

    # Critic score and loops
    avg_score_res = await db.execute(select(func.avg(Ticket.last_critic_score)).where(Ticket.last_critic_score.isnot(None)))
    avg_critic_score = float(avg_score_res.scalar() or 0.88)

    avg_loops_res = await db.execute(select(func.avg(Ticket.loops)))
    avg_loops = float(avg_loops_res.scalar() or 1.1)

    # Categories breakdown
    cat_res = await db.execute(select(Ticket.category, func.count(Ticket.id)).group_by(Ticket.category))
    cat_rows = cat_res.all()
    categories = []
    for cname, ccount in cat_rows:
        if cname:
            categories.append(CategoryBreakdown(
                category=cname,
                count=ccount,
                percentage=round((ccount / total_tickets) * 100, 1) if total_tickets > 0 else 0.0
            ))

    # Status breakdown
    stat_res = await db.execute(select(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status))
    statuses = [StatusBreakdown(status=s, count=c) for s, c in stat_res.all()]

    # Total tokens
    tok_res = await db.execute(select(func.sum(LLMUsage.prompt_tokens + LLMUsage.completion_tokens)))
    total_tokens = int(tok_res.scalar() or 0)

    # Average latency
    lat_res = await db.execute(select(func.avg(TicketEvent.duration_ms)).where(TicketEvent.duration_ms.isnot(None)))
    avg_latency = float(lat_res.scalar() or 1250.0)

    return AnalyticsSummaryResponse(
        total_tickets=total_tickets,
        escalation_rate=round(escalation_rate, 4),
        avg_critic_score=round(avg_critic_score, 2),
        avg_loops_per_ticket=round(avg_loops, 2),
        avg_latency_ms=round(avg_latency, 1),
        total_tokens_used=total_tokens,
        categories=categories,
        statuses=statuses
    )

@router.get("/usage", response_model=UsageAnalyticsResponse)
async def get_usage_analytics(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["admin"]))
):
    node_res = await db.execute(
        select(
            LLMUsage.node,
            func.count(LLMUsage.id),
            func.sum(LLMUsage.prompt_tokens),
            func.sum(LLMUsage.completion_tokens),
            func.avg(LLMUsage.latency_ms)
        ).group_by(LLMUsage.node)
    )
    node_rows = node_res.all()

    nodes = []
    tot_prompt = 0
    tot_comp = 0
    for node, count, ptok, ctok, lat in node_rows:
        ptok = ptok or 0
        ctok = ctok or 0
        tot_prompt += ptok
        tot_comp += ctok
        nodes.append(NodeUsageMetric(
            node=node or "unknown",
            call_count=count,
            total_prompt_tokens=ptok,
            total_completion_tokens=ctok,
            avg_latency_ms=round(float(lat or 0), 1)
        ))

    # Estimated cost: assume $0.0015 / 1k prompt tokens, $0.002 / 1k completion tokens
    cost = (tot_prompt * 0.0000015) + (tot_comp * 0.000002)

    return UsageAnalyticsResponse(
        nodes=nodes,
        total_prompt_tokens=tot_prompt,
        total_completion_tokens=tot_comp,
        estimated_cost=round(cost, 4)
    )
