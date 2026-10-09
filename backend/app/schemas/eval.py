from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel

class EvalCaseOut(BaseModel):
    id: str
    case_code: Optional[str] = None
    message: str
    expected_category: str
    expected_route: str
    expected_source_docs: Optional[List[str]] = None
    reference_answer: Optional[str] = None
    should_escalate: bool

    class Config:
        from_attributes = True

class EvalDatasetOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    case_count: Optional[int] = None

    class Config:
        from_attributes = True

class EvalRunCreateRequest(BaseModel):
    dataset_id: str
    critic_enabled: bool = True
    label: str

class EvalRunOut(BaseModel):
    id: str
    dataset_id: str
    label: str
    critic_enabled: bool
    status: str
    summary_metrics: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EvalResultOut(BaseModel):
    id: str
    case_id: str
    actual_category: Optional[str] = None
    actual_route: Optional[str] = None
    actual_answer: Optional[str] = None
    critic_score: Optional[float] = None
    loops: int
    latency_ms: int
    passed: bool
    metrics: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class EvalRunDetailResponse(EvalRunOut):
    results: List[EvalResultOut] = []
