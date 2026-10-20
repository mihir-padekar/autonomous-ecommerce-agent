"""
RAG Retrieval Evaluation Runner
================================
Evaluates the ChromaDB vector store retrieval pipeline against the 15-sample
authoritative dataset (evals/datasets/eval_rag_authoritative.json).

Metrics computed per sample:
  - keyword_hit  : Whether expected chunk keywords appear in top-k retrieved chunks
  - fact_coverage: Fraction of reference_facts found in retrieved text (0.0-1.0)
  - failure_mode : Classified per the FailureMode taxonomy

Aggregate metrics:
  - keyword_hit_rate  : % samples with keyword_hit = True
  - avg_fact_coverage : Mean fact_coverage across all samples
  - accuracy          : % samples with fact_coverage >= 0.5
  - failure_breakdown : Count per FailureMode
"""

import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from evals.failure_taxonomy import (
    EvalSummary,
    FailureMode,
    RAGEvalResult,
)
from mcp_server.tools.read_tools import lookup_policy
from observability.logging import app_logger

# ── Paths ────────────────────────────────────────────────────────────────────
DATASETS_DIR = Path("evals/datasets")
RESULTS_DIR  = Path("evals/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def _classify_rag_failure(
    keyword_hit: bool,
    fact_coverage: float,
    retrieved_sources: List[str],
    expected_source: str,
) -> tuple[FailureMode, str | None]:
    """Assign a single FailureMode to a RAG result."""
    if keyword_hit and fact_coverage >= 0.5:
        return FailureMode.NONE, None

    # Check if the right document was retrieved at all
    src_hit = any(expected_source.lower() in s.lower() for s in retrieved_sources)

    if not retrieved_sources:
        return FailureMode.RETRIEVAL_MISS, "No chunks retrieved from vector store."
    if not src_hit:
        return FailureMode.RETRIEVAL_WRONG_SOURCE, (
            f"Expected source '{expected_source}' not found in retrieved sources: {retrieved_sources}"
        )
    if not keyword_hit:
        return FailureMode.RETRIEVAL_LOW_RECALL, (
            "Expected keywords absent from top-k chunks despite correct source being retrieved."
        )
    # keyword hit but fact_coverage < 0.5
    return FailureMode.INCOMPLETE_ANSWER, (
        f"Only {fact_coverage:.0%} of reference facts covered by retrieved context."
    )


def run_rag_eval(top_k: int = 3, inter_query_delay_s: float = 0.5) -> EvalSummary:
    """
    Runs the full RAG retrieval evaluation against eval_rag_authoritative.json.
    """
    dataset_path = DATASETS_DIR / "eval_rag_authoritative.json"
    samples: List[Dict[str, Any]] = json.loads(dataset_path.read_text(encoding="utf-8"))

    run_id = f"rag-eval-{uuid.uuid4().hex[:8]}"
    results: List[RAGEvalResult] = []
    failure_counts: Dict[str, int] = {}

    app_logger.info(f"Starting RAG eval run {run_id} | Samples: {len(samples)} | top_k={top_k}")
    print(f"\n{'='*70}")
    print(f"  RAG RETRIEVAL EVALUATION  |  run_id={run_id}  |  samples={len(samples)}")
    print(f"{'='*70}")

    for idx, sample in enumerate(samples, start=1):
        qid     = sample["question_id"]
        query   = sample["user_input"]
        ref     = sample["reference"]
        facts   = sample.get("reference_facts", [])
        exp_src = sample.get("expected_source_document", "")
        exp_kws = sample.get("expected_chunk_keywords", [])

        t0 = time.perf_counter()
        tool_resp = lookup_policy(query=query, top_k=top_k)
        latency_ms = (time.perf_counter() - t0) * 1000

        retrieved_chunks  = [c["content"] for c in (tool_resp.data or {}).get("chunks", [])]
        retrieved_sources = [c["source"]  for c in (tool_resp.data or {}).get("chunks", [])]
        combined_text     = " ".join(retrieved_chunks).lower()

        # --- Keyword Hit -------------------------------------------------------
        keyword_hit = any(kw.lower() in combined_text for kw in exp_kws) if exp_kws else False

        # --- Fact Coverage -----------------------------------------------------
        if facts:
            covered = sum(1 for f in facts if f.split("=")[-1].strip().lower() in combined_text)
            fact_coverage = covered / len(facts)
        else:
            fact_coverage = 1.0 if keyword_hit else 0.0

        # --- Classify Failure --------------------------------------------------
        failure_mode, failure_detail = _classify_rag_failure(
            keyword_hit, fact_coverage, retrieved_sources, exp_src
        )
        failure_counts[failure_mode.value] = failure_counts.get(failure_mode.value, 0) + 1

        result = RAGEvalResult(
            question_id=qid,
            user_input=query,
            reference=ref,
            retrieved_chunks=retrieved_chunks,
            retrieved_sources=retrieved_sources,
            keyword_hit=keyword_hit,
            fact_coverage=fact_coverage,
            failure_mode=failure_mode,
            failure_detail=failure_detail,
            latency_ms=round(latency_ms, 1),
        )
        results.append(result)

        status = "PASS" if failure_mode == FailureMode.NONE else f"FAIL [{failure_mode.value}]"
        print(f"  [{idx:02d}/{len(samples)}] {qid} | keyword_hit={keyword_hit} | "
              f"fact_cov={fact_coverage:.0%} | {status} | {latency_ms:.0f}ms")

        if inter_query_delay_s > 0:
            time.sleep(inter_query_delay_s)

    # ── Aggregate ─────────────────────────────────────────────────────────────
    passed            = sum(1 for r in results if r.failure_mode == FailureMode.NONE)
    accuracy          = passed / len(results)
    keyword_hit_rate  = sum(1 for r in results if r.keyword_hit) / len(results)
    avg_fact_coverage = sum(r.fact_coverage for r in results) / len(results)

    summary = EvalSummary(
        run_id=run_id,
        eval_type="rag",
        total_samples=len(results),
        passed=passed,
        failed=len(results) - passed,
        accuracy=accuracy,
        avg_fact_coverage=avg_fact_coverage,
        keyword_hit_rate=keyword_hit_rate,
        failure_breakdown=failure_counts,
        results=[r.model_dump() for r in results],
    )

    # ── Persist results ────────────────────────────────────────────────────────
    out_path = RESULTS_DIR / f"{run_id}.json"
    out_path.write_text(
        json.dumps(summary.model_dump(), indent=2, default=str),
        encoding="utf-8",
    )

    print(f"\n{'='*70}")
    print(f"  RAG EVAL COMPLETE")
    print(f"  Accuracy        : {accuracy:.1%}  ({passed}/{len(results)} passed)")
    print(f"  Keyword Hit Rate: {keyword_hit_rate:.1%}")
    print(f"  Avg Fact Cover  : {avg_fact_coverage:.1%}")
    print(f"  Failure Breakdown: {failure_counts}")
    print(f"  Results saved   : {out_path}")
    print(f"{'='*70}\n")

    return summary
