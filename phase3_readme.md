# Phase 3: LangGraph ReAct Agent with Human-In-The-Loop (HITL)

## 1. Executive Summary

In Phase 3, we transitioned from the legacy linear 8-node waterfall pipeline to an **autonomous ReAct (Reason + Act) agent architecture** powered by **LangGraph** and bound to our **FastMCP tool server**. 

Crucially, we implemented an enterprise-grade **Human-in-the-Loop (HITL)** safety mechanism using LangGraph's native `interrupt()` and `Command(resume=...)` primitives. Read-only operations resolve autonomously, while risky mutations (issuing refunds, escalating tickets, updating order delivery states) automatically halt execution, snapshot thread state to memory, and await verified operator confirmation.

---

## 2. What We Built

### A. Resilient LLM Provider Factory (`app/core/llm.py`)
- Configured a multi-tier LLM fallback chain using `langchain-groq`.
- Primary reasoning model: `qwen/qwen3.8-27b` (or `llama-3.3-70b-versatile` if configured via env).
- Fallback model: `openai/gpt-oss-120b` (or `llama-3.1-8b-instant`).
- Utilizes `.with_fallbacks()` so temporary rate limit spikes or transient gateway timeouts automatically roll over to the backup model without failing user requests.

### B. Typed State Architecture (`app/graph/state.py`)
Defined `AgentState` containing:
- `messages`: Append-only message history managed via `add_messages` reducer.
- `thread_id`: Unique identifier tracking the user session and checkpointer snapshot.
- `pending_approval`: Structured metadata describing proposed write operations.
- `approval_status`: Cycle status (`None`, `"pending"`, `"approved"`, `"rejected"`).
- `audit_log`: Chronological list of all executed and rejected tool actions.

### C. ReAct Graph Nodes & Router (`app/graph/nodes.py`)
- **`agent_node`**: Binds the 8 MCP tools to the LLM and processes message history under an Operations Copilot system prompt.
- **`tool_executor_node`**: Inspects tool calls:
  - If tool is **read-only** (`get_warehouse_delay_summary`, `get_order_details`, `lookup_policy`, etc.): executes immediately and appends a `ToolMessage`.
  - If tool is **risky write** (`issue_refund`, `escalate_ticket`, `update_order_status`): pauses execution via `interrupt(approval_request)`. When resumed with an approval or rejection, it applies the human supervisor's decision and logs an audit record.
- **`router_condition`**: Conditional edge determining whether to loop into `tool_executor` or finish at `__end__`.

### D. Workflow Engine & Dispatchers (`app/graph/workflow.py`)
- Compiles the `StateGraph` with a `MemorySaver` checkpointer for thread-level state persistence.
- **`run_agent(query, thread_id)`**: Runs the agent turn until completion or an approval pause, returning `status="completed"` or `status="pending_approval"`.
- **`resume_agent(thread_id, decision, approved_by, notes)`**: Resumes paused threads via `Command(resume=...)`, feeding human authorization back into the active tool execution step.

### E. Production REST API (`app/api/`)
- [`app/api/v1/agent.py`](file:///d:/1_CDAC_notes/Project/autonomous-ecommerce-agent/app/api/v1/agent.py): `POST /api/v1/agent/chat` executes user requests and flags pending approval actions.
- [`app/api/v1/approvals.py`](file:///d:/1_CDAC_notes/Project/autonomous-ecommerce-agent/app/api/v1/approvals.py): `POST /api/v1/approvals/resume` allows supervisors to approve or reject pending actions.
- [`app/api/v1/health.py`](file:///d:/1_CDAC_notes/Project/autonomous-ecommerce-agent/app/api/v1/health.py): `GET /api/v1/health` verifies API readiness and live PostgreSQL connectivity.
- [`app/api/server.py`](file:///d:/1_CDAC_notes/Project/autonomous-ecommerce-agent/app/api/server.py): FastAPI server factory mounting middleware, OpenAPI documentation, and v1 routes.

---

## 3. How We Did It: ReAct Loop & HITL State Machine

```mermaid
flowchart TD
    Start([User Request]) --> AgentNode[Agent Reasoning Node]
    
    AgentNode --> Decision{Tool Call Needed?}
    Decision -- No --> Deliver[Deliver Response to User]
    Deliver --> Conclude([End])
    
    Decision -- Yes --> CheckTool{Tool Type?}
    
    CheckTool -- "Read-Only (delay summary, order lookup, SLA policy)" --> AutoExec[Execute Read Tool Automatically]
    AutoExec --> AgentNode
    
    CheckTool -- "Risky Write (refund, escalation, status update)" --> InterruptNode[Trigger LangGraph interrupt()]
    
    InterruptNode --> PauseState[(Thread Paused in MemorySaver)]
    PauseState --> Supervisor{Human Supervisor Decision}
    
    Supervisor -- "Approved" --> ResumeApprove[Resume: Execute Write Tool on DB with approved_by]
    Supervisor -- "Rejected" --> ResumeReject[Resume: Cancel Write & Prompt Agent with Justification]
    
    ResumeApprove --> RecordAudit[Write Immutable WorkflowLog Entry]
    ResumeReject --> RecordAudit
    RecordAudit --> AgentNode
```

### The Interrupt / Resume Code Pattern

1. **Pausing on Risky Actions** (`app/graph/nodes.py`):
```python
if mcp_client.is_approval_required(tool_name):
    approval_request = {
        "action": "human_approval_required",
        "tool_name": tool_name,
        "tool_args": tool_args,
        "prompt": f"Review required for {tool_name}"
    }
    # Halts execution and saves state to MemorySaver
    human_decision = interrupt(approval_request)
    
    if human_decision.get("decision") == "approved":
        # Execute tool with supervisor metadata
        ...
```

2. **Resuming with Command** (`app/graph/workflow.py`):
```python
def resume_agent(thread_id: str, decision: str, approved_by: str, notes: str):
    config = {"configurable": {"thread_id": thread_id}}
    resume_payload = {
        "decision": decision.lower(),
        "approved_by": approved_by,
        "notes": notes
    }
    # Resumes execution from the exact point of interruption
    graph.invoke(Command(resume=resume_payload), config=config)
```

---

## 4. Why We Did It (Engineering Rationale & Tradeoffs)

| Metric / Dimension | Legacy Waterfall Pipeline | Phase 3 ReAct + HITL Architecture |
| :--- | :--- | :--- |
| **Token Efficiency & Latency** | Every prompt ran through 8 nodes sequentially (Planner, Database, Analysis, Policy, Compliance, Executive Summary, Chat, Report), consuming thousands of tokens even for simple lookups. | Dynamic tool-calling invokes only the tools required to satisfy user intent. Read-only answers return in 1-2 turns. |
| **Operational Safety** | No write actions were possible; adding write actions to a linear pipeline would execute mutations without confirmation. | Zero unapproved mutations: LangGraph `interrupt()` enforces a strict human approval checkpoint for all writes before database mutation. |
| **Fault Resilience** | Single Groq model failure would crash the entire request. | Resilient model chain with `.with_fallbacks()` ensures seamless failover during rate limit spikes or transient downtime. |
| **Auditability** | Logs were scattered dicts in python code. | Thread states and human approval decisions are checkpointed and recorded with reviewer names, reasons, and timestamps in PostgreSQL `workflow_log`. |

---

## 5. Verification & Test Results

### A. Integration Test Suite (`tests/integration/test_agent_workflow.py`)
Tested end-to-end against live Groq API and Neon PostgreSQL:
```bash
pytest tests/integration/test_agent_workflow.py -v
```
Output:
```text
============================= test session starts =============================
tests/integration/test_agent_workflow.py::test_read_only_agent_query PASSED [ 50%]
tests/integration/test_agent_workflow.py::test_write_action_interrupts_and_resumes_with_rejection PASSED [100%]

============================= 2 passed in 42.21s ==============================
```

### B. Health Probe Verification
```bash
python -c "from fastapi.testclient import TestClient; from app.api.server import app; client = TestClient(app); print(client.get('/api/v1/health').json())"
```
Output:
```json
{"status": "healthy", "service": "Autonomous E-Commerce Operations Copilot", "database": "connected"}
```

---

## 6. Next Phase: Phase 4 Roadmap

With the ReAct loop, MCP client, and Human-in-the-Loop workflows verified, we move to **Phase 4: Guardrails & Observability**:
1. **Langfuse Distributed Tracing**: Attaching trace callbacks to LangGraph runs for latency spans, token analytics, and cost tracking.
2. **Structured JSON Logging**: Standardizing logger outputs with trace correlation IDs.
3. **Input Moderation Guardrails**: Prompt injection defense and input sanitization (`guardrails/input_moderation.py`).
4. **Policy Compliance Guardrails**: Pre-execution validation ensuring refunds and escalations comply with SLA thresholds (`guardrails/policy_compliance.py`).

