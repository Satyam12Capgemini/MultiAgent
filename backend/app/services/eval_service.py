import time
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.models import EvalDataset, EvalCase, EvalRun, EvalResult
from app.graph.builder import support_graph
from app.core.errors import NotFoundError
from app.core.logging import logger

class EvalService:
    async def list_datasets(self, session: AsyncSession) -> List[EvalDataset]:
        result = await session.execute(select(EvalDataset).order_by(desc(EvalDataset.created_at)))
        return list(result.scalars().all())

    async def get_dataset(self, session: AsyncSession, dataset_id: str) -> EvalDataset:
        result = await session.execute(select(EvalDataset).where(EvalDataset.id == dataset_id))
        ds = result.scalar_one_or_none()
        if not ds:
            raise NotFoundError(f"Dataset {dataset_id} not found")
        return ds

    async def load_dataset_from_json(self, session: AsyncSession, name: str, description: str, cases_data: List[Dict[str, Any]]) -> EvalDataset:
        ds = EvalDataset(name=name, description=description)
        session.add(ds)
        await session.flush()

        for c in cases_data:
            case = EvalCase(
                dataset_id=ds.id,
                case_code=c.get("id"),
                message=c.get("message", ""),
                expected_category=c.get("expected_category", "general"),
                expected_route=c.get("expected_route", "general_agent"),
                expected_source_docs=json.dumps(c.get("expected_source_docs", [])),
                reference_answer=c.get("reference_answer", ""),
                should_escalate=c.get("should_escalate", False)
            )
            session.add(case)

        await session.commit()
        return ds

    async def run_evaluation(
        self,
        session: AsyncSession,
        dataset_id: str,
        label: str,
        critic_enabled: bool = True
    ) -> EvalRun:
        ds = await self.get_dataset(session, dataset_id)
        cases_res = await session.execute(select(EvalCase).where(EvalCase.dataset_id == dataset_id))
        cases = cases_res.scalars().all()

        run = EvalRun(
            dataset_id=dataset_id,
            label=label,
            critic_enabled=critic_enabled,
            status="running"
        )
        session.add(run)
        await session.commit()

        correct_routing = 0
        correct_escalation = 0
        total_faithfulness = 0.0
        total_loops = 0
        latencies = []
        passed_cases = 0

        for case in cases:
            start_t = time.time()
            sim_ticket_id = f"eval-t-{uuid.uuid4().hex[:8]}"
            sim_run_id = f"eval-r-{uuid.uuid4().hex[:8]}"

            initial_state = {
                "ticket_id": sim_ticket_id,
                "thread_id": sim_ticket_id,
                "customer_id": "cust-eval",
                "run_id": sim_run_id,
                "seq": 0,
                "messages": [{"role": "customer", "content": case.message}],
                "loops": 0
            }

            try:
                final_state = await support_graph.ainvoke(initial_state)
                latency_ms = int((time.time() - start_t) * 1000)
                latencies.append(latency_ms)

                actual_cat = final_state.get("category", "")
                actual_answer = final_state.get("final_answer") or final_state.get("answer", "")
                actual_score = final_state.get("critic_score", 1.0) if critic_enabled else 0.8
                loops_taken = final_state.get("loops", 1)
                total_loops += loops_taken
                total_faithfulness += actual_score

                is_escalated = final_state.get("escalation_reason") is not None
                cat_match = (actual_cat == case.expected_category)
                esc_match = (is_escalated == case.should_escalate)

                if cat_match:
                    correct_routing += 1
                if esc_match:
                    correct_escalation += 1

                passed = cat_match and esc_match
                if passed:
                    passed_cases += 1

                eval_res = EvalResult(
                    run_id=run.id,
                    case_id=case.id,
                    actual_category=actual_cat,
                    actual_route=actual_cat + "_agent" if not is_escalated else "escalate",
                    actual_answer=actual_answer,
                    critic_score=actual_score,
                    loops=loops_taken,
                    latency_ms=latency_ms,
                    passed=passed,
                    metrics=json.dumps({"routing_correct": cat_match, "escalation_correct": esc_match})
                )
                session.add(eval_res)

            except Exception as e:
                logger.error(f"Eval case {case.id} failed: {e}")

        total_count = len(cases) or 1
        summary = {
            "total_cases": len(cases),
            "passed_cases": passed_cases,
            "routing_accuracy": round(correct_routing / total_count, 4),
            "escalation_accuracy": round(correct_escalation / total_count, 4),
            "avg_faithfulness": round(total_faithfulness / total_count, 4),
            "hallucination_rate": round(1.0 - (total_faithfulness / total_count), 4),
            "avg_loops": round(total_loops / total_count, 2),
            "avg_latency_ms": int(sum(latencies) / len(latencies)) if latencies else 0,
            "p95_latency_ms": sorted(latencies)[int(0.95 * len(latencies))] if latencies else 0
        }

        run.status = "completed"
        run.completed_at = datetime.now(timezone.utc)
        run.summary_metrics = json.dumps(summary)
        await session.commit()
        return run

    async def get_run_detail(self, session: AsyncSession, run_id: str) -> Optional[EvalRun]:
        result = await session.execute(select(EvalRun).where(EvalRun.id == run_id))
        return result.scalar_one_or_none()

    async def get_run_results(self, session: AsyncSession, run_id: str) -> List[EvalResult]:
        result = await session.execute(select(EvalResult).where(EvalResult.run_id == run_id))
        return list(result.scalars().all())

eval_service = EvalService()
