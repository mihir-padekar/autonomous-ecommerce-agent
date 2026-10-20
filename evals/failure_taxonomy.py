from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FailureMode(str, Enum):
    """
    Exhaustive taxonomy of observable failure modes in the Operations Copilot.
    Every test case failure must be classified exactly once.
    """
    # --- Retrieval Layer ---
    RETRIEVAL_MISS         = "RETRIEVAL_MISS"        # Top-k chunks did not contain the ground-truth passage
    RETRIEVAL_LOW_RECALL   = "RETRIEVAL_LOW_RECALL"  # Keywords present but ranked outside top-k
    RETRIEVAL_WRONG_SOURCE = "RETRIEVAL_WRONG_SOURCE"# Retrieved from wrong policy document

    # --- Generation / LLM Layer ---
    HALLUCINATION          = "HALLUCINATION"         # Answer asserts facts not in retrieved context
    INCOMPLETE_ANSWER      = "INCOMPLETE_ANSWER"     # Only partial facts from reference_facts found
    WRONG_NUMBER           = "WRONG_NUMBER"          # Numeric value (days, amount) is incorrect
    REFUSAL                = "REFUSAL"               # Model refuses to answer answerable question

    # --- Tool Routing Layer ---
    WRONG_TOOL_SELECTED    = "WRONG_TOOL_SELECTED"   # Agent called incorrect MCP tool
    TOOL_ARG_ERROR         = "TOOL_ARG_ERROR"        # Tool called with malformed or missing arguments
    TOOL_EXECUTION_ERROR   = "TOOL_EXECUTION_ERROR"  # Tool raised exception at runtime

    # --- Guardrail Layer ---
    FALSE_POSITIVE_BLOCK   = "FALSE_POSITIVE_BLOCK"  # Safe query blocked by moderation guardrail
    CREDENTIAL_LEAK        = "CREDENTIAL_LEAK"       # Sensitive data not redacted from output

    # --- None ---
    NONE                   = "NONE"                  # No failure — correct result


class RAGEvalResult(BaseModel):
    """Result for a single RAG retrieval + generation evaluation sample."""
    question_id: str
    user_input: str
    reference: str
    retrieved_chunks: List[str] = Field(default_factory=list)
    retrieved_sources: List[str] = Field(default_factory=list)
    keyword_hit: bool = False          # Expected keywords found in retrieved chunks
    fact_coverage: float = 0.0        # Fraction of reference_facts covered [0.0–1.0]
    failure_mode: FailureMode = FailureMode.NONE
    failure_detail: Optional[str] = None
    latency_ms: Optional[float] = None


class RoutingEvalResult(BaseModel):
    """Result for a single tool routing decision evaluation sample."""
    query_id: str
    query: str
    expected_route: str
    predicted_tool: Optional[str] = None
    correct: bool = False
    failure_mode: FailureMode = FailureMode.NONE
    failure_detail: Optional[str] = None
    latency_ms: Optional[float] = None


class EvalSummary(BaseModel):
    """Aggregated metrics across a full evaluation run."""
    run_id: str
    eval_type: str           # "rag" or "routing"
    total_samples: int
    passed: int
    failed: int
    accuracy: float          # passed / total_samples

    # RAG-specific
    avg_fact_coverage: Optional[float] = None
    keyword_hit_rate: Optional[float] = None

    # Failure breakdown
    failure_breakdown: Dict[str, int] = Field(default_factory=dict)

    # Per-result details
    results: List[Dict[str, Any]] = Field(default_factory=list)

