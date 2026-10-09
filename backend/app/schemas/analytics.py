from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class CategoryBreakdown(BaseModel):
    category: str
    count: int
    percentage: float

class StatusBreakdown(BaseModel):
    status: str
    count: int

class AnalyticsSummaryResponse(BaseModel):
    total_tickets: int
    escalation_rate: float
    avg_critic_score: float
    avg_loops_per_ticket: float
    avg_latency_ms: float
    total_tokens_used: int
    categories: List[CategoryBreakdown]
    statuses: List[StatusBreakdown]

class NodeUsageMetric(BaseModel):
    node: str
    call_count: int
    total_prompt_tokens: int
    total_completion_tokens: int
    avg_latency_ms: float

class UsageAnalyticsResponse(BaseModel):
    nodes: List[NodeUsageMetric]
    total_prompt_tokens: int
    total_completion_tokens: int
    estimated_cost: float
