# Phase 2: FastMCP Tool Server & Pydantic v2 Schemas

## 1. Executive Summary

In Phase 2, we engineered a production-grade **FastMCP Tool Server** utilizing the official Model Context Protocol (MCP) Python SDK (`mcp.server.mcpserver.MCPServer`), reinforced with strict **Pydantic v2** validation contracts. 

We established a zero-trust safety boundary that separates **autonomous read-only queries** from **risky mutation actions** (refunds, ticket escalations, status updates) which require explicit **Human-in-the-Loop (HITL)** approval before touching the database.

---

## 2. What We Built

### A. Pydantic v2 Validation Schemas (`mcp_server/schemas/`)
- [`common.py`](file:///d:/1_CDAC_notes/Project/autonomous-ecommerce-agent/mcp_server/schemas/common.py): Defines `ToolActionType` (`READ_ONLY` vs `WRITE_APPROVAL_REQUIRED`), `RiskLevel`, and the standardized `ToolResponse` envelope.
- [`orders.py`](file:///d:/1_CDAC_notes/Project/autonomous-ecommerce-agent/mcp_server/schemas/orders.py): Request/response contracts with validators for warehouse delay analysis, order lookup, status transitions, and refund requests.
- [`tickets.py`](file:///d:/1_CDAC_notes/Project/autonomous-ecommerce-agent/mcp_server/schemas/tickets.py): Typed schemas for complaints, support ticket filtering, and priority escalations.
- [`policies.py`](file:///d:/1_CDAC_notes/Project/autonomous-ecommerce-agent/mcp_server/schemas/policies.py): Typed input and chunk models for semantic RAG policy lookups.

### B. Read-Only Tools (`mcp_server/tools/read_tools.py`)
All read tools execute autonomously without pause (`requires_human_approval=False`):
1. **`get_warehouse_delay_summary`**: Aggregates total orders, delayed shipment counts, and average delay days grouped by warehouse.
2. **`get_order_details`**: Fetches comprehensive order tracking data, delay days, and linked complaints/tickets.
3. **`get_customer_complaints`**: Retrieves complaints by customer, order, category, or status.
4. **`get_ticket_details`**: Retrieves support tickets with priority and team assignments.
5. **`lookup_policy`**: Queries the ChromaDB vector store for authoritative policy clauses (delivery SLAs, refund eligibility, escalation matrices).

### C. Risky Write Tools (`mcp_server/tools/write_tools.py`)
All mutation tools are gated behind human authorization (`requires_human_approval=True`):
1. **`issue_refund`**: Prepares and validates a customer refund. When unapproved, it returns a proposed action payload with an audit trail; upon supervisor confirmation, it records the refund transaction in PostgreSQL `workflow_log`.
2. **`escalate_ticket`**: Proposes or executes reassignment of critical tickets to Tier 2 operations teams.
3. **`update_order_status`**: Validates status transitions (`Delivered`, `Delayed`, `Cancelled`, `In Transit`) and logs fulfillment changes.

### D. Official FastMCP Server & Client Bridge
- [`mcp_server/server.py`](file:///d:/1_CDAC_notes/Project/autonomous-ecommerce-agent/mcp_server/server.py): FastMCP server exposing tools via `@server.tool()` decorators and supporting stdio/SSE transports.
- [`mcp_server/client.py`](file:///d:/1_CDAC_notes/Project/autonomous-ecommerce-agent/mcp_server/client.py): High-level client adapter providing tool discovery and converting MCP tools into LangChain `StructuredTool` instances ready for LangGraph agent binding.

### E. Unit Test Suite
- [`tests/unit/test_mcp_tools.py`](file:///d:/1_CDAC_notes/Project/autonomous-ecommerce-agent/tests/unit/test_mcp_tools.py): 5 automated test cases testing read tools, approval pauses, and LangChain tool conversion. All passing with zero warnings.

---

## 3. How We Did It

### The Two-Phase Proposal/Execution Protocol
To allow an AI agent to suggest actions without executing unapproved side effects, write tools implement a two-phase protocol:

```
[Agent invokes write tool without approved_by]
                  │
                  ▼
   Pydantic Input Validation
                  │
                  ▼
Does order/ticket exist in DB? ──► No ──► ToolResponse(success=False, error)
                  │ Yes
                  ▼
Is approved_by provided?
       ├── NO  ──► Return ToolResponse(
       │                 action_type="write_approval_required",
       │                 requires_human_approval=True,
       │                 message="ACTION REQUIRED: Proposed refund for Order...",
       │                 audit_trail={...}
       │           ) [Halts for LangGraph interrupt]
       │
       └── YES ──► Mutate DB, write immutable WorkflowLog audit entry,
                   and return ToolResponse(success=True, execution_status="COMPLETED")
```

### LangChain StructuredTool Bridging
In [`mcp_server/client.py`](file:///d:/1_CDAC_notes/Project/autonomous-ecommerce-agent/mcp_server/client.py), each registered MCP tool is wrapped dynamically using `StructuredTool.from_function`:
```python
tool_instance = StructuredTool.from_function(
    func=wrapper,
    name=tool_name,
    description=meta["description"],
    args_schema=SCHEMA_MAP.get(tool_name)
)
```
This enables the LangGraph ReAct agent in Phase 3 to bind directly to MCP tools without custom glue code.

---

## 4. Why We Did It (Engineering Rationale)

| Architectural Goal | Previous Prototype Limitation | Phase 2 Implementation Advantage |
| :--- | :--- | :--- |
| **Separation of Privilege** | Read and write actions had no distinction in raw Python scripts. | Read tools execute autonomously, while state mutations are strictly gated by `ToolActionType.WRITE_APPROVAL_REQUIRED`. |
| **Safety & Auditability** | No record of why or by whom a state change was proposed or approved. | Every mutation produces a structured `audit_trail` and writes an immutable log row into `WorkflowLog` upon approval. |
| **Protocol Portability** | Agents were coupled to internal database helper functions. | Any MCP-compliant client (Claude Desktop, external microservices, LangGraph) can connect to `mcp_server/server.py` over standard JSON-RPC. |
| **Type Integrity** | Unchecked dictionary parameters caused runtime KeyError exceptions. | Pydantic v2 validates types, regex, minimum string lengths, and numeric ranges before any tool logic runs. |

---

## 5. Test Verification Results

Automated tests verified via `pytest`:
```bash
pytest tests/unit/test_mcp_tools.py -v
```
Output:
```text
tests/unit/test_mcp_tools.py::test_warehouse_delay_summary_read_only PASSED [ 20%]
tests/unit/test_mcp_tools.py::test_order_details_lookup PASSED           [ 40%]
tests/unit/test_mcp_tools.py::test_issue_refund_requires_approval_by_default PASSED [ 60%]
tests/unit/test_mcp_tools.py::test_escalate_ticket_requires_approval PASSED [ 80%]
tests/unit/test_mcp_tools.py::test_mcp_client_tool_discovery PASSED      [100%]
============================== 5 passed in 4.04s ==============================
```

---

## 6. Next Phase: Phase 3 Roadmap

With Phase 2 complete, we are ready for **Phase 3: LangGraph ReAct Agent with Human-In-The-Loop (HITL)**:
1. **LLM Factory**: Primary model Groq Llama 3.3 70B (`llama-3.3-70b-versatile`) with automatic fallback to Llama 3.1 8B (`llama-3.1-8b-instant`).
2. **ReAct Agent Loop**: LangGraph StateGraph binding the 8 MCP tools.
3. **HITL Interruption**: Implementing `interrupt()` when write tools are selected, resuming execution upon human approval or cancellation.
4. **FastAPI Endpoints**: Chat query endpoint `/api/v1/agent/chat` and approval endpoint `/api/v1/approvals/resume`.

