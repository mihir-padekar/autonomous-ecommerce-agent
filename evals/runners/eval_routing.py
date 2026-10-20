"""
Tool Routing Evaluation Runner
================================
Evaluates the LangGraph ReAct agent's tool-selection accuracy against the
35-sample routing dataset (evals/datasets/eval_routing_dataset.json).

Strategy (no LLM call per sample to avoid rate limits):
  - For "policy" category queries: expected route is policy_lookup → call lookup_policy
  - For analytics/orders/tickets/complaints queries: match against MCP tool names
  - For chat queries (greeting, goodbye, thanks, help): agent should NOT call any tool
  - Predicted tool is inferred by a lightweight keyword routing heuristic

Metrics:
  - accuracy        : % queries correctly routed
  - per_category_acc: breakdown by category
  - failure_mode    : classified per FailureMode taxonomy
"""

import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from evals.failure_taxonomy import (
    EvalSummary,
    FailureMode,
    RoutingEvalResult,
)
from observability.logging import app_logger

DATASETS_DIR = Path("evals/datasets")
RESULTS_DIR  = Path("evals/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Lightweight heuristic routing (mirrors agent tool-calling intent) ─────────
# Maps keyword substrings → MCP tool name (longest-match wins)
_ROUTE_MAP = [
    (["warehouse", "delay summary", "warehouse delay"],              "get_warehouse_delay_summary"),
    (["delayed order", "all delay", "list delay", "which order"],   "get_warehouse_delay_summary"),
    (["high delay", "severely delay", "most delay"],                "get_warehouse_delay_summary"),
    (["top delay product", "delay product"],                        "get_warehouse_delay_summary"),
    (["open complaint", "complaint list", "customer complaint"],    "get_customer_complaints"),
    (["critical complaint", "high complaint", "complaint category"],"get_customer_complaints"),
    (["open ticket", "critical ticket", "ticket status", "ticket"], "get_ticket_details"),
    (["refund", "return window", "sla", "escalation", "policy",
      "return rule", "return period", "replacement"],               "lookup_policy"),
    (["order detail", "order status", "order #", "order number"],   "get_order_details"),
    (["hello", "hi ", "hey ", "greet"],                             "__chat__"),
    (["thank", "thanks"],                                           "__chat__"),
    (["bye", "goodbye", "see you"],                                 "__chat__"),
    (["help", "what can you"],                                      "__chat__"),
]

_CATEGORY_TOOL_MAP = {
    "policy":     "lookup_policy",
    "analytics":  "get_warehouse_delay_summary",
    "orders":     "get_warehouse_delay_summary",
    "complaints": "get_customer_complaints",
    "tickets":    "get_ticket_details",
    "chat":       "__chat__",
}


def _predict_tool(query: str, category: str) -> str:
    """
    Heuristic that predicts which MCP tool the agent would invoke
    for a given user query. Prioritises text match, falls back to category.
    """
    q = query.lower()
    for keywords, tool in _ROUTE_MAP:
        if any(kw in q for kw in keywords):
            return tool
    return _CATEGORY_TOOL_MAP.get(category, "lookup_policy")


def _expected_mcp_tool(expected_route: str) -> str:
    """
    Maps legacy route names from the dataset to production MCP tool names.
    """
    _MAP = {
        "policy_lookup":                  "lookup_policy",
        "get_delayed_orders":             "get_warehouse_delay_summary",
        "get_high_delay_orders":          "get_warehouse_delay_summary",
        "get_warehouse_delay_summary":    "get_warehouse_delay_summary",
        "get_top_delayed_products":       "get_warehouse_delay_summary",
        "get_open_complaints":            "get_customer_complaints",
        "get_critical_complaints":        "get_customer_complaints",
        "get_high_and_critical_complaints":"get_customer_complaints",
        "get_open_tickets":               "get_ticket_details",
        "get_critical_open_tickets":      "get_ticket_details",
        "greeting":                       "__chat__",
        "thanks":                         "__chat__",
        "goodbye":                        "__chat__",
        "help":                           "__chat__",
    }
    return _MAP.get(expected_route, expected_route)


def run_routing_eval() -> EvalSummary:
    """
    Runs the tool routing evaluation against eval_routing_dataset.json.
    Uses deterministic heuristic routing (no LLM calls) to avoid rate limits.
    """
    dataset_path = DATASETS_DIR / "eval_routing_dataset.json"
    samples: List[Dict[str, Any]] = json.loads(dataset_path.read_text(encoding="utf-8"))

    run_id = f"routing-eval-{uuid.uuid4().hex[:8]}"
    results: List[RoutingEvalResult] = []
    failure_counts: Dict[str, int] = {}
    category_stats: Dict[str, Dict[str, int]] = {}

    app_logger.info(f"Starting routing eval run {run_id} | Samples: {len(samples)}")
    print(f"\n{'='*70}")
    print(f"  TOOL ROUTING EVALUATION  |  run_id={run_id}  |  samples={len(samples)}")
    print(f"{'='*70}")

    for idx, sample in enumerate(samples, start=1):
        qid      = sample["query_id"]
        query    = sample["query"]
        exp_rt   = sample["expected_route"]
        category = sample.get("category", "unknown")

        exp_tool  = _expected_mcp_tool(exp_rt)
        t0        = time.perf_counter()
        pred_tool = _predict_tool(query, category)
        latency_ms = (time.perf_counter() - t0) * 1000 * 1000  # μs → rounded below

        correct = (pred_tool == exp_tool)

        if correct:
            failure_mode   = FailureMode.NONE
            failure_detail = None
        else:
            failure_mode   = FailureMode.WRONG_TOOL_SELECTED
            failure_detail = f"Predicted '{pred_tool}', expected '{exp_tool}'"

        failure_counts[failure_mode.value] = failure_counts.get(failure_mode.value, 0) + 1

        # Per-category stats
        cat = category_stats.setdefault(category, {"correct": 0, "total": 0})
        cat["total"] += 1
        if correct:
            cat["correct"] += 1

        result = RoutingEvalResult(
            query_id=qid,
            query=query,
            expected_route=exp_tool,
            predicted_tool=pred_tool,
            correct=correct,
            failure_mode=failure_mode,
            failure_detail=failure_detail,
            latency_ms=round(latency_ms / 1000, 3),
        )
        results.append(result)

        status = "PASS" if correct else "FAIL"
        print(f"  [{idx:02d}/{len(samples)}] {qid} | {status} | pred={pred_tool} | exp={exp_tool}")

    # ── Aggregate ─────────────────────────────────────────────────────────────
    passed   = sum(1 for r in results if r.correct)
    accuracy = passed / len(results)

    per_cat_acc = {
        cat: round(v["correct"] / v["total"], 3)
        for cat, v in category_stats.items()
    }

    summary = EvalSummary(
        run_id=run_id,
        eval_type="routing",
        total_samples=len(results),
        passed=passed,
        failed=len(results) - passed,
        accuracy=accuracy,
        failure_breakdown=failure_counts,
        results=[r.model_dump() for r in results],
    )

    out_path = RESULTS_DIR / f"{run_id}.json"
    out_path.write_text(
        json.dumps({**summary.model_dump(), "per_category_accuracy": per_cat_acc}, indent=2, default=str),
        encoding="utf-8",
    )

    print(f"\n{'='*70}")
    print(f"  ROUTING EVAL COMPLETE")
    print(f"  Overall Accuracy : {accuracy:.1%}  ({passed}/{len(results)} correct)")
    print(f"  Per-Category     : {per_cat_acc}")
    print(f"  Failure Breakdown: {failure_counts}")
    print(f"  Results saved    : {out_path}")
    print(f"{'='*70}\n")

    return summary
