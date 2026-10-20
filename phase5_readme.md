# Phase 5: Evaluation Suite & Published Failure Analysis

## 1. Executive Summary

In Phase 5, we established a **standardized, regression-gated evaluation harness** and authored a comprehensive **Failure Mode Analysis** for the Operations Copilot. 

We solved the persistent rate limit issues encountered with external LLM-as-a-judge frameworks by transitioning to a deterministic, high-throughput benchmark methodology that computes **Keyword Hit Rate**, **Reference Fact Coverage**, and **Tool Routing Accuracy** with zero external API burn. 

Every deviation is classified under a formal **Failure Mode Taxonomy** and preserved in reproducible JSON artefacts in `evals/results/`.

---

## 2. What We Built

### A. Failure Mode Taxonomy (`evals/failure_taxonomy.py`)
Established an exhaustive classification schema for platform failures:
- **Retrieval Failures**: `RETRIEVAL_MISS`, `RETRIEVAL_LOW_RECALL`, `RETRIEVAL_WRONG_SOURCE`.
- **Generation Failures**: `HALLUCINATION`, `INCOMPLETE_ANSWER`, `WRONG_NUMBER`, `REFUSAL`.
- **Tool Routing Failures**: `WRONG_TOOL_SELECTED`, `TOOL_ARG_ERROR`, `TOOL_EXECUTION_ERROR`.
- **Guardrail Failures**: `FALSE_POSITIVE_BLOCK`, `CREDENTIAL_LEAK`.
- Pydantic models: `RAGEvalResult`, `RoutingEvalResult`, and `EvalSummary`.

### B. RAG Retrieval Evaluation Runner (`evals/runners/eval_rag.py`)
- Evaluates the ChromaDB vector store against the 15-sample authoritative dataset (`evals/datasets/eval_rag_authoritative.json`).
- Measures:
  - **Keyword Hit**: Expected policy keywords present in top-k chunks.
  - **Fact Coverage**: Percentage of required business facts covered by retrieved context.
  - **Latency (ms)** per query.
- Saves structured reports to `evals/results/rag-eval-<id>.json`.

### C. Tool Routing Evaluation Runner (`evals/runners/eval_routing.py`)
- Evaluates intent matching and tool selection across 35 test cases (`evals/datasets/eval_routing_dataset.json`).
- Groups performance across 6 categories: `orders`, `complaints`, `tickets`, `analytics`, `policy`, and `chat`.
- Saves structured reports to `evals/results/routing-eval-<id>.json`.

### D. Unified Evaluation Suite CLI (`evals/runners/run_eval_suite.py`)
- Single command execution for CI/CD and developer testing:
  ```bash
  python -m evals.runners.run_eval_suite           # Full suite
  python -m evals.runners.run_eval_suite --rag     # RAG only
  python -m evals.runners.run_eval_suite --routing # Routing only
  ```

### E. Published Failure Analysis Report (`docs/failure_analysis.md`)
- Authoritative documentation detailing root causes and production engineering mitigations:
  - Analysis of `RETRIEVAL_LOW_RECALL` in dense table excerpts.
  - Analysis of cross-domain polysemy in tool routing (`ROUTE_004`).
  - Analysis of Groq 429 TPM/RPM quota exhaustion and the multi-tier fallback solution.

### F. Unit Test Suite (`tests/unit/test_eval_taxonomy.py`)
- 5 automated unit tests validating taxonomy enum serialization, failure classification, and routing prediction.

---

## 3. Benchmark Verification Results

### A. Tool Routing Evaluation Run
```bash
python -m evals.runners.run_eval_suite --routing
```
**Results**:
```text
======================================================================
  ROUTING EVAL COMPLETE
  Overall Accuracy : 97.1%  (34/35 correct)
  Per-Category     : {'policy': 0.8, 'orders': 1.0, 'complaints': 1.0, 'tickets': 1.0, 'analytics': 1.0, 'chat': 1.0}
  Failure Breakdown: {'NONE': 34, 'WRONG_TOOL_SELECTED': 1}
======================================================================
```

### B. RAG Retrieval Evaluation Run
```bash
python -m evals.runners.run_eval_suite --rag
```
**Results**:
```text
======================================================================
  RAG EVAL COMPLETE
  Accuracy        : 80.0%  (12/15 passed)
  Keyword Hit Rate: 80.0%
  Avg Fact Cover  : 85.6%
  Failure Breakdown: {'NONE': 12, 'RETRIEVAL_LOW_RECALL': 3}
======================================================================
```

### C. Unit Test Suite
```bash
pytest tests/unit/test_eval_taxonomy.py -v
```
**Results**:
```text
============================== 5 passed in 0.68s ==============================
```

---

## 4. Why We Did It (Engineering Rationale)

| Challenge | Prototype Bottleneck | Phase 5 Production Solution |
| :--- | :--- | :--- |
| **Rate Limit Aborts** | External LLM evaluator frameworks sent rapid sequential calls to Groq, crashing with 429 rate limit errors. | Shifted offline regression benchmarks to deterministic keyword hits and reference fact coverage, running in seconds with 0 API tokens consumed. |
| **Lack of Failure Categorization** | Evals produced simple binary pass/fail without diagnostic taxonomy. | Systematic `FailureMode` taxonomy pinpointing exact subsystem breakdowns (`RETRIEVAL_LOW_RECALL`, `WRONG_TOOL_SELECTED`). |
| **CI/CD Regression Gating** | No automated quality checks on tool definitions or prompt changes. | Standardized evaluation runner returns machine-readable JSON summaries ready for GitHub Actions gating. |

---

## 5. Next Phase: Phase 6 Roadmap

With evaluations complete and failure analysis published, we conclude with **Phase 6: Docker Compose Packaging, CI/CD, & Portfolio Documentation**:
1. **Multi-Service Docker Compose** (`docker-compose.yml`): Packaging FastAPI app, PostgreSQL database, FastMCP server, and Langfuse tracing.
2. **Dockerfile & Container Optimizations**: Multi-stage build for rapid container startup.
3. **Architecture Portfolio Documentation** (`docs/architecture.md`): End-to-end system design diagrams, state machine specifications, and API documentation.

