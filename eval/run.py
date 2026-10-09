import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone

# Add backend directory to sys.path so we can import app modules directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.db.session import engine, Base, AsyncSessionLocal
from app.services.eval_service import eval_service
from app.rag.ingest import ingestion_service
from app.cli import seed_data, ingest_samples
from app.core.logging import setup_logging

async def execute_eval_run(dataset_path: str, critic_enabled: bool, label: str):
    setup_logging("WARNING")
    print(f"[+] Starting Evaluation Run: '{label}' (Critic: {'ON' if critic_enabled else 'OFF'})...")

    # Initialize tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed and ingest if empty
    async with AsyncSessionLocal() as session:
        await ingestion_service.refresh_bm25_index(session)

    # Load dataset
    if not os.path.exists(dataset_path):
        print(f"[ERROR] Dataset file not found: {dataset_path}")
        return

    with open(dataset_path, "r", encoding="utf-8") as f:
        cases_data = json.load(f)

    async with AsyncSessionLocal() as session:
        ds = await eval_service.load_dataset_from_json(
            session=session,
            name=f"Dataset {label}",
            description=f"Auto-loaded from {dataset_path}",
            cases_data=cases_data
        )

        run = await eval_service.run_evaluation(
            session=session,
            dataset_id=ds.id,
            label=label,
            critic_enabled=critic_enabled
        )

        summary = json.loads(run.summary_metrics) if run.summary_metrics else {}
        results = await eval_service.get_run_results(session, run.id)

    # Output Markdown Report
    os.makedirs("eval/results", exist_ok=True)
    report_path = f"eval/results/{label}.md"

    md_content = f"""# Evaluation Run Report: `{label}`

- **Timestamp:** {datetime.now(timezone.utc).isoformat()}
- **Critic Enabled:** {'Yes (Full Loop)' if critic_enabled else 'No (Baseline Single-Pass)'}
- **Total Test Cases:** {summary.get('total_cases', 0)}
- **Passed Cases:** {summary.get('passed_cases', 0)}

## Summary Metrics

| Metric | Measured Value | Target Baseline |
|--------|----------------|-----------------|
| **Routing Accuracy** | {summary.get('routing_accuracy', 0.0) * 100:.1f}% | > 90.0% |
| **Escalation Accuracy** | {summary.get('escalation_accuracy', 0.0) * 100:.1f}% | > 90.0% |
| **Faithfulness Score** | {summary.get('avg_faithfulness', 0.0) * 100:.1f}% | > 85.0% |
| **Hallucination Rate** | {summary.get('hallucination_rate', 0.0) * 100:.1f}% | < 15.0% |
| **Average Critic Loops** | {summary.get('avg_loops', 1.0)} | <= 1.5 |
| **Latency p50 / p95** | {summary.get('avg_latency_ms', 0)} ms / {summary.get('p95_latency_ms', 0)} ms | < 2500 ms |

## Case-by-Case Breakdown

| Case Code | Expected Cat | Actual Cat | Critic Score | Loops | Latency (ms) | Pass / Fail |
|-----------|--------------|------------|--------------|-------|--------------|-------------|
"""

    for r in results:
        pass_icon = "[PASS]" if r.passed else "[FAIL]"
        md_content += f"| `{r.case_id[:8]}` | {r.actual_category} | {r.actual_category} | {r.critic_score or 0.0:.2f} | {r.loops} | {r.latency_ms} ms | {pass_icon} |\n"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[OK] Evaluation completed! Report written to {report_path}")
    print(json.dumps(summary, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Support Copilot Evaluation Runner")
    parser.add_argument("--dataset", default="eval/dataset.json", help="Path to evaluation dataset JSON")
    parser.add_argument("--critic", choices=["on", "off"], default="on", help="Enable or disable critic fact-checking loop")
    parser.add_argument("--label", default="baseline-eval", help="Label name for the evaluation run")

    args = parser.parse_args()
    asyncio.run(execute_eval_run(args.dataset, args.critic == "on", args.label))

if __name__ == "__main__":
    main()
