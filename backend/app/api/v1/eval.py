import json
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import User, EvalRun
from app.schemas.eval import (
    EvalDatasetOut, EvalRunCreateRequest, EvalRunOut, EvalRunDetailResponse, EvalResultOut
)
from app.services.eval_service import eval_service
from app.api.deps import require_roles
from app.core.errors import NotFoundError

router = APIRouter()

@router.get("/datasets", response_model=List[EvalDatasetOut])
async def list_eval_datasets(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["admin"]))
):
    datasets = await eval_service.list_datasets(db)
    return [EvalDatasetOut.model_validate(ds) for ds in datasets]

@router.post("/datasets", response_model=EvalDatasetOut)
async def upload_eval_dataset(
    file: UploadFile = File(...),
    name: str = "Benchmark Dataset",
    description: str = "Standard 50-case customer support test set",
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["admin"]))
):
    content = await file.read()
    cases_data = json.loads(content.decode("utf-8"))
    ds = await eval_service.load_dataset_from_json(db, name, description, cases_data)
    return EvalDatasetOut.model_validate(ds)

@router.post("/runs", response_model=EvalRunOut)
async def create_eval_run(
    req: EvalRunCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["admin"]))
):
    run = await eval_service.run_evaluation(
        session=db,
        dataset_id=req.dataset_id,
        label=req.label,
        critic_enabled=req.critic_enabled
    )
    summary_dict = json.loads(run.summary_metrics) if run.summary_metrics else None
    run_out = EvalRunOut.model_validate(run)
    run_out.summary_metrics = summary_dict
    return run_out

@router.get("/runs", response_model=List[EvalRunOut])
async def list_eval_runs(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["admin"]))
):
    result = await db.execute(select(EvalRun).order_by(EvalRun.created_at.desc()))
    runs = result.scalars().all()
    output = []
    for r in runs:
        r_out = EvalRunOut.model_validate(r)
        r_out.summary_metrics = json.loads(r.summary_metrics) if r.summary_metrics else None
        output.append(r_out)
    return output

@router.get("/runs/{run_id}", response_model=EvalRunDetailResponse)
async def get_eval_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["admin"]))
):
    run = await eval_service.get_run_detail(db, run_id)
    if not run:
        raise NotFoundError(f"Eval run {run_id} not found")
    results = await eval_service.get_run_results(db, run_id)

    formatted_results = []
    for res in results:
        formatted_results.append(EvalResultOut(
            id=res.id,
            case_id=res.case_id,
            actual_category=res.actual_category,
            actual_route=res.actual_route,
            actual_answer=res.actual_answer,
            critic_score=res.critic_score,
            loops=res.loops,
            latency_ms=res.latency_ms,
            passed=res.passed,
            metrics=json.loads(res.metrics) if res.metrics else None
        ))

    summary_dict = json.loads(run.summary_metrics) if run.summary_metrics else None
    run_out = EvalRunOut.model_validate(run)
    run_out.summary_metrics = summary_dict

    return EvalRunDetailResponse(
        **run_out.model_dump(),
        results=formatted_results
    )
