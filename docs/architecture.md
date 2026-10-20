# Master System Architecture: Autonomous E-Commerce Operations Copilot

## 1. Overview & Core Philosophy

The **Autonomous E-Commerce Operations Copilot** is a production-grade AI system engineered to resolve natural language operations queries, audit warehouse delays, cross-reference SLA policies, and execute sensitive customer support mutations under strict human oversight.

Unlike basic conversational bots, this system enforces **Principle of Least Privilege**:
1. **Read-Only Actions** (warehouse analytics, order status tracking, vector policy search) execute autonomously in real time.
2. **Risky Write Actions** (issuing customer refunds, escalating tickets to Tier 2, changing fulfillment status) pause automatically for **Human-in-the-Loop (HITL)** approval.
3. Every step is traced via **Langfuse**, logged into **structured JSON**, and protected by **prompt injection and SLA guardrails**.

---

## 2. High-Level System Architecture

```mermaid
flowchart TD
    subgraph ClientLayer["Client & Governance Layer"]
        User["Operations User / Recruiter"]
        Supervisor["Human Supervisor (HITL Cockpit)"]
        StreamlitUI["Dual-Pane Streamlit UI (demo_app.py)"]
        FastAPIEndpoint["FastAPI REST API (/api/v1)"]
    end

    subgraph SecurityObservability["Safety & Observability Perimeter"]
        InputGuard["Input Moderation (Prompt Injection & SQL Defense)"]
        OutputGuard["Output Sanitizer (Credential Redaction)"]
        PolicyGuard["Business Policy SLA Checker"]
        JSONLogger["Structured JSON Logger"]
        LangfuseTracer["Langfuse Distributed Tracing"]
    end

    subgraph AgentOrchestration["LangGraph ReAct Agent"]
        StateStore[("MemorySaver Checkpointer")]
        AgentNode["Agent Reasoning Node (Groq Qwen 27B / Llama 70B)"]
        FallbackLLM["Fallback LLM (OpenAI OSS 120B / Llama 8B)"]
        RouterCondition{"Tool Call Needed?"}
        ToolExecutor["Tool Executor Node"]
        InterruptGate["LangGraph interrupt() Gate"]
    end

    subgraph MCPToolLayer["FastMCP Tool Server"]
        MCPRead["Read Tools: get_warehouse_delay_summary, get_order_details, lookup_policy"]
        MCPWrite["Write Tools: issue_refund, escalate_ticket, update_order_status"]
    end

    subgraph DataStorage["Data & Knowledge Layer"]
        PostgresDB[("PostgreSQL (Neon Cloud DB)")]
        ChromaStore[("ChromaDB Vector Store (MiniLM Embeddings)")]
    end

    User --> StreamlitUI
    StreamlitUI --> InputGuard
    InputGuard --> AgentNode
    AgentNode -.-> FallbackLLM
    AgentNode --> RouterCondition
    RouterCondition -- "Read Tool" --> ToolExecutor --> MCPRead --> PostgresDB & ChromaStore
    RouterCondition -- "Risky Write Tool" --> PolicyGuard --> InterruptGate
    InterruptGate --> StateStore
    InterruptGate -.-> Supervisor
    Supervisor -- "Approve / Reject" --> FastAPIEndpoint --> StateStore --> ToolExecutor --> MCPWrite --> PostgresDB
    ToolExecutor --> OutputGuard --> StreamlitUI
    AgentNode & ToolExecutor -.-> LangfuseTracer & JSONLogger
```

---

## 3. The LangGraph State Machine & HITL Protocol

The agent uses a cyclic StateGraph maintaining typed `AgentState`:
```python
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    thread_id: str
    pending_approval: Optional[Dict[str, Any]]
    approval_status: Optional[str]
    audit_log: List[Dict[str, Any]]
```

### The Interrupt / Resume Lifecycle
1. When the agent selects `issue_refund` or `escalate_ticket`, `tool_executor_node` checks `mcp_client.is_approval_required(tool_name)`.
2. The node runs `verify_refund_policy` or `verify_escalation_policy` and constructs a rich approval payload.
3. It calls `interrupt(approval_request)`. The thread state is snapshotted to `MemorySaver`.
4. The client receives `status="pending_approval"`.
5. When the supervisor reviews the action card and clicks **Approve** or **Reject**:
   ```python
   graph.invoke(Command(resume={"decision": "approved", "approved_by": "Alex"}), config={"configurable": {"thread_id": tid}})
   ```
6. The graph resumes from the exact paused node, executes the tool on the database if approved, writes an immutable `WorkflowLog` entry, and delivers the confirmation message.

---

## 4. MCP Tool Catalog & Permission Matrix

| Tool Name | Type | Permission Level | Trigger Criteria | Target Data Store |
| :--- | :---: | :---: | :--- | :--- |
| `get_warehouse_delay_summary` | Read | Autonomous | Delay analytics, warehouse ranking | PostgreSQL (`orders`) |
| `get_order_details` | Read | Autonomous | Single order lookup, delivery status | PostgreSQL (`orders`, `tickets`) |
| `get_customer_complaints` | Read | Autonomous | Complaint history, category search | PostgreSQL (`complaints`) |
| `get_ticket_details` | Read | Autonomous | Support tickets, team assignment | PostgreSQL (`tickets`) |
| `lookup_policy` | Read | Autonomous | SLA rules, return windows, escalations | ChromaDB (`refund_policy.pdf`, etc.) |
| `issue_refund` | Write | **HITL Approval Required** | Delayed order refund, defective item | PostgreSQL (`workflow_log`) |
| `escalate_ticket` | Write | **HITL Approval Required** | SLA breach, priority reassignment | PostgreSQL (`tickets`, `workflow_log`) |
| `update_order_status` | Write | **HITL Approval Required** | Delivery status change, cancellation | PostgreSQL (`orders`, `workflow_log`) |

---

## 5. Security & Guardrails Architecture

1. **Input Moderation**:
   - Regex patterns detect directive injection (`"ignore all previous instructions"`, `"DAN mode"`).
   - SQL keyword detection prevents injection payloads (`UNION SELECT`, `DROP TABLE`).
   - Size limit: 4,000 characters.
2. **Business Policy Compliance**:
   - `verify_refund_policy`: Checks if delay $\ge 5$ days or if defective/damaged claims are documented. Flags requests exceeding \$1,000.00.
   - `verify_escalation_policy`: Rejects escalations for already resolved tickets.
3. **Output Credential Redaction**:
   - Outbound responses are stripped of API keys (`gsk_...`), tokens, and database connection strings before display.

---

## 6. Live Deployment Guide (100% Free)

### Streamlit Community Cloud (Recommended)
1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and click **New App**.
3. Select your repository, branch (`main`), and set **Main file path** to `demo_app.py`.
4. Under **Advanced Settings > Secrets**, paste your environment variables:
   ```toml
   GROQ_API_KEY = "gsk_..."
   DATABASE_URL = "postgresql://neondb_owner:...@ep-flat-thunder...neon.tech/neondb?sslmode=require"
   PRIMARY_MODEL = "qwen/qwen3.8-27b"
   FALLBACK_MODEL = "openai/gpt-oss-120b"
   ```
5. Click **Deploy!** Your app will be live at `https://<your-app-name>.streamlit.app`.