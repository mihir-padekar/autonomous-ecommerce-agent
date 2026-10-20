# Phase 1: Architectural Audit & Production Restructure

## 1. Executive Summary

This phase lays the foundational architecture to transition the **Autonomous E-Commerce Operations Copilot** from a linear prototype script into a production-grade, observable, guard-railed multi-tool agent system driven by the **Model Context Protocol (MCP)** and **LangGraph Human-in-the-Loop (HITL)** workflows.

---

## 2. What We Did

1. **System Architecture & Codebase Audit**:
   - Analyzed existing data models (`Order`, `Complaint`, `Ticket`, `WorkflowLog`, `ChatHistory`) in PostgreSQL.
   - Audited 450+ lines of SQL & analytical ORM queries across warehouse delay tracking, customer complaints, and SLA violation computations.
   - Inspected the legacy 8-node linear LangGraph waterfall (`planner` → `database` → `analysis` → `policy` → `compliance` → `executive_summary` → `chat_response` → `report`).
   - Identified critical structural gaps: lack of tool protocol standardization, absence of write/mutation capabilities, missing human approval gating, and lack of distributed tracing.

2. **Established Production-Grade Directory Structure**:
   Created a decoupled, maintainable directory hierarchy separating application logic, tool servers, guardrails, observability, and evaluations:
   - `app/`: Core FastAPI service, LangGraph state & ReAct agent loops, database models, and RAG retrieval services.
   - `mcp_server/`: Dedicated FastMCP server exposing operations tools with strict Pydantic v2 schemas and permission boundaries.
   - `guardrails/`: Input moderation, prompt injection mitigation, and business policy compliance validators.
   - `observability/`: Langfuse distributed tracing integration and structured JSON logging.
   - `evals/`: Authoritative RAG & routing evaluation datasets, RAGAs metric runners, and failure taxonomy definitions.
   - `tests/`: Automated unit and integration testing suite for tools, schemas, and graph nodes.
   - `docs/`: System architecture documentation, state machine diagrams, and failure mode analysis.

3. **Core Application & Database Foundations**:
   - Implemented `app/core/config.py` using **Pydantic v2 `BaseSettings`**, establishing environment-driven configurations for Groq primary (`llama-3.3-70b-versatile`) and fallback (`llama-3.1-8b-instant`) models, Langfuse observability credentials, and FastMCP endpoints.
   - Modularized `app/database/session.py` and `app/database/models.py`, preserving complete schema compatibility with the existing PostgreSQL instance.

4. **Evaluation Asset Consolidation**:
   - Centralized authoritative benchmark datasets (`eval_dataset.json`, `eval_rag_authoritative.json`, `eval_routing_dataset.json`) into `evals/datasets/`.
   - Structured the evaluation runner harness into `evals/runners/run_evaluation.py`.

5. **Dependency Modernization**:
   - Updated `requirements.txt` to include `mcp>=1.2.0`, `langfuse`, `pydantic-settings`, `pytest`, and `pytest-asyncio`.

---

## 3. How We Did It

### Step 1: Non-Breaking Parallel Restructure
To protect working database connections and data assets (such as the ChromaDB vector store and Neon PostgreSQL tables), the restructure was conducted non-destructively:
- The legacy `backend/` directory remains intact as a reference baseline while the new `app/` and `mcp_server/` modules are established.
- All newly created directories were equipped with `__init__.py` markers to ensure compliant Python package resolution.

### Step 2: Settings & Environment Configuration with Pydantic v2
Configured typed settings in `app/core/config.py`:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    PROJECT_NAME: str = "Autonomous E-Commerce Operations Copilot"
    DATABASE_URL: str
    GROQ_API_KEY: str
    PRIMARY_MODEL: str = "llama-3.3-70b-versatile"
    FALLBACK_MODEL: str = "llama-3.1-8b-instant"
    MCP_SERVER_NAME: str = "ecommerce-operations-tools"
    ...
```

### Step 3: Verification
Executed smoke tests against the new configuration and database layers:
- Validated that `Settings` cleanly parses `.env`.
- Verified that SQLAlchemy engine initialization against Neon PostgreSQL succeeds with connection pooling (`pool_pre_ping=True`, `pool_recycle=300`).

---

## 4. Why We Did It (Engineering Rationale & Architectural Decisions)

| Design Decision | Previous Prototype State | Production Target (Why We Changed It) |
| :--- | :--- | :--- |
| **Tool Protocol (MCP)** | Agents directly imported raw Python SQL query functions from `backend/database/queries.py`. | **Official FastMCP Server**: Decouples business tools from agent implementation. Enables external systems, desktop clients, and other agents to consume warehouse, order, and ticket tools uniformly via a standardized JSON-RPC protocol. |
| **Agent Execution Pattern** | Rigid 8-step linear pipeline that executed every node (including report generation) for every user message. | **Dynamic ReAct Tool Loop**: The agent inspects user intent, selects relevant tools dynamically, and loops until resolution without wasted tokens or unnecessary latency. |
| **Safety & Human-in-the-Loop** | Read-only analytics with zero mutation capabilities. | **Separation of Read vs Write Tools + LangGraph Interrupt**: Read tools execute automatically. High-risk write tools (`issue_refund`, `escalate_ticket`, `update_order_status`) pause the workflow via LangGraph `interrupt()`, waiting for human review. |
| **Input/Output Validation** | Unstructured dictionaries passed between graph nodes. | **Pydantic v2 Schemas**: Strict validation of tool arguments and return values prevents hallucinated parameters, SQL injection risks, and schema drift. |
| **Observability** | Synchronous table inserts into a single `workflow_log` DB table. | **Langfuse Distributed Tracing**: Granular latency spans, token usage accounting, prompt version tracking, and automated failure classification. |
| **Evaluation Strategy** | Loose script files in root directory hitting rate limits. | **Structured `evals/` Harness**: Dedicated datasets and metrics measuring routing accuracy, retrieval Hit@k, and generation faithfulness with automated regression tests. |

---

## 5. Next Phase: Phase 2 Roadmap

With Phase 1 complete and verified, the next phase will implement:
1. **Pydantic v2 Tool Schemas**: Defining request and response contracts for all operational tools (`app/mcp_server/schemas/`).
2. **FastMCP Server**: Implementing read-only tools (warehouse delays, order status, SLA lookup) and risky write tools (refund issuance, ticket escalation).
3. **MCP Client Integration**: Developing the client adapter allowing the LangGraph agent to dynamically discover and call tools over the MCP protocol.

