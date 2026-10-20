import pytest
from evals.failure_taxonomy import (
    FailureMode,
    RAGEvalResult,
    RoutingEvalResult,
    EvalSummary,
)
from evals.runners.eval_rag import _classify_rag_failure
from evals.runners.eval_routing import _predict_tool, _expected_mcp_tool


def test_failure_mode_enum_values():
    """Verify all failure modes are uniquely classified."""
    assert FailureMode.RETRIEVAL_MISS == "RETRIEVAL_MISS"
    assert FailureMode.RETRIEVAL_LOW_RECALL == "RETRIEVAL_LOW_RECALL"
    assert FailureMode.WRONG_TOOL_SELECTED == "WRONG_TOOL_SELECTED"
    assert FailureMode.NONE == "NONE"


def test_classify_rag_failure_success():
    """Verify clean retrieval returns FailureMode.NONE."""
    mode, detail = _classify_rag_failure(
        keyword_hit=True,
        fact_coverage=1.0,
        retrieved_sources=["refund_policy.pdf"],
        expected_source="refund_policy.pdf"
    )
    assert mode == FailureMode.NONE
    assert detail is None


def test_classify_rag_failure_wrong_source():
    """Verify retrieval from incorrect document is classified as RETRIEVAL_WRONG_SOURCE."""
    mode, detail = _classify_rag_failure(
        keyword_hit=False,
        fact_coverage=0.0,
        retrieved_sources=["delivery_sla_policy.pdf"],
        expected_source="refund_policy.pdf"
    )
    assert mode == FailureMode.RETRIEVAL_WRONG_SOURCE
    assert "Expected source" in detail


def test_routing_prediction_heuristics():
    """Verify routing predictions map domain queries to proper MCP tools."""
    assert _predict_tool("Which warehouse has delays?", "analytics") == "get_warehouse_delay_summary"
    assert _predict_tool("Look up customer refund policy", "policy") == "lookup_policy"
    assert _predict_tool("Show me open support tickets", "tickets") == "get_ticket_details"
    assert _predict_tool("Hello there", "chat") == "__chat__"


def test_eval_summary_serialization():
    """Verify EvalSummary serialization into valid Pydantic dictionary."""
    summary = EvalSummary(
        run_id="test-run-123",
        eval_type="routing",
        total_samples=10,
        passed=9,
        failed=1,
        accuracy=0.9,
        failure_breakdown={"NONE": 9, "WRONG_TOOL_SELECTED": 1}
    )
    dumped = summary.model_dump()
    assert dumped["accuracy"] == 0.9
    assert dumped["passed"] == 9
    assert dumped["failure_breakdown"]["WRONG_TOOL_SELECTED"] == 1

