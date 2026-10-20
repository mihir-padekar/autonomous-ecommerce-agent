"""
Unified Evaluation Suite Entry Point
=====================================
Runs both the RAG retrieval and routing evaluation suites,
merges the results, and writes a summary JSON artefact.

Usage:
    python -m evals.runners.run_eval_suite           # full suite
    python -m evals.runners.run_eval_suite --rag     # RAG only
    python -m evals.runners.run_eval_suite --routing # routing only
"""

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from evals.runners.eval_rag     import run_rag_eval
from evals.runners.eval_routing import run_routing_eval

RESULTS_DIR = Path("evals/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Autonomous Operations Copilot — Eval Suite")
    parser.add_argument("--rag",     action="store_true", help="Run RAG evaluation only")
    parser.add_argument("--routing", action="store_true", help="Run routing evaluation only")
    parser.add_argument("--top-k",  type=int, default=3,  help="Top-k chunks for RAG retrieval (default=3)")
    parser.add_argument("--delay",  type=float, default=0.3, help="Inter-query delay seconds (default=0.3)")
    args = parser.parse_args()

    run_both = not args.rag and not args.routing

    suite_id  = f"suite-{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now(timezone.utc).isoformat()
    suite_out: dict = {"suite_id": suite_id, "timestamp": timestamp, "runs": {}}

    if run_both or args.rag:
        print("\n>>> Running RAG Retrieval Evaluation...")
        rag_summary = run_rag_eval(top_k=args.top_k, inter_query_delay_s=args.delay)
        suite_out["runs"]["rag"] = {
            "run_id":          rag_summary.run_id,
            "accuracy":        f"{rag_summary.accuracy:.1%}",
            "keyword_hit_rate":f"{rag_summary.keyword_hit_rate:.1%}",
            "avg_fact_coverage":f"{rag_summary.avg_fact_coverage:.1%}",
            "total_samples":   rag_summary.total_samples,
            "passed":          rag_summary.passed,
            "failed":          rag_summary.failed,
            "failure_breakdown": rag_summary.failure_breakdown,
        }

    if run_both or args.routing:
        print("\n>>> Running Tool Routing Evaluation...")
        routing_summary = run_routing_eval()
        suite_out["runs"]["routing"] = {
            "run_id":         routing_summary.run_id,
            "accuracy":       f"{routing_summary.accuracy:.1%}",
            "total_samples":  routing_summary.total_samples,
            "passed":         routing_summary.passed,
            "failed":         routing_summary.failed,
            "failure_breakdown": routing_summary.failure_breakdown,
        }

    out_path = RESULTS_DIR / f"{suite_id}.json"
    out_path.write_text(json.dumps(suite_out, indent=2, default=str), encoding="utf-8")

    print(f"\n{'='*70}")
    print(f"  EVAL SUITE COMPLETE  |  suite_id={suite_id}")
    for eval_type, data in suite_out["runs"].items():
        print(f"  {eval_type.upper():<10} accuracy={data['accuracy']}  passed={data['passed']}/{data['total_samples']}")
    print(f"  Suite report: {out_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()

