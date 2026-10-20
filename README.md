# Autonomous E-Commerce Operations Copilot ⚡
### Enterprise Production-Grade, Observable & Guard-Railed Operations Intelligence Platform

An autonomous operations intelligence platform powered by **Model Context Protocol (FastMCP)**, **LangGraph ReAct Orchestration**, **Human-in-the-Loop (HITL) Governance**, **Security Guardrails**, **Langfuse Distributed Tracing**, and an **Obsidian Dark B2B Control Cockpit**.
Live Demo link - https://autonomous-ecommerce-agent-ewct4oenj3qhgiuvejwwcy.streamlit.app/
---
# UI/Working 

<img width="1917" height="867" alt="Screenshot 2026-10-20 120639" src="https://github.com/user-attachments/assets/dcda6722-43f6-4535-b661-c8773d958be9" />
<img width="1917" height="862" alt="Screenshot 2026-10-20 121535" src="https://github.com/user-attachments/assets/31678f3f-ba24-4036-af62-16ffa43dfdef" />
<img width="1917" height="865" alt="Screenshot 2026-10-20 121607" src="https://github.com/user-attachments/assets/394daad7-5cbe-4b65-8f97-97b3884fd4e9" />


## 📑 Project Phase Documentation

This repository has been comprehensively structured and built across 6 discrete phases. Each phase contains its own architectural specification and implementation log:

| Phase | Readme Document | Focus Area | Deliverables |
| :--- | :--- | :--- | :--- |
| **Phase 1** | [phase1_readme.md](phase1_readme.md) | **Audit & Modular Restructuring** | Unified config, database schema isolation, environment sanitation |
| **Phase 2** | [phase2_readme.md](phase2_readme.md) | **FastMCP Server & Safety Segregation** | Pydantic v2 schemas, read-only tools vs. gated write actions |
| **Phase 3** | [phase3_readme.md](phase3_readme.md) | **LangGraph ReAct & HITL Architecture** | ReAct cycle, Groq LLM fallback chain, `interrupt()` & `Command(resume=...)` |
| **Phase 4** | [phase4_readme.md](phase4_readme.md) | **Security Guardrails & Observability** | Input moderation (SQL/Jailbreak), SLA policy verification, Langfuse tracing |
| **Phase 5** | [phase5_readme.md](phase5_readme.md) | **Deterministic Evaluation Harness** | 35-sample routing & 15-sample RAG eval, failure taxonomy, 97.1% accuracy |
| **Phase 6** | [phase6_readme.md](phase6_readme.md) | **Dual-Pane UI & Production Packaging** | Obsidian Dark Streamlit app, multi-stage Dockerfile, cloud deployment guide |

---

## 🏛️ High-Level System Architecture

```text
                                  +---------------------------------------+
                                  |       Dual-Pane Operator UI           |
                                  |  (Chat Interface + Supervisor Cockpit)|
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |       Security Guardrails Layer       |
                                  |  • Jailbreak & Prompt Injection Check |
                                  |  • SQL Query Injection Guard          |
                                  |  • PII & Credential Sanitization      |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |        LangGraph ReAct Loop           |
                                  |   (Memory Checkpointer State Graph)   |
                                  |                                       |
                                  |   Primary: Groq Qwen 2.5 27B          |
                                  |   Fallback: Groq GPT-OSS 120B         |
                                  +---------+-------------------+---------+
                                            |                   |
                     [Read-Only Tools]      |                   | [Mutating Write Tools]
                            |               |                   |
                            v               |                   v
                +-----------------------+   |       +-----------------------+
                | FastMCP Read Executor |   |       |   LangGraph Interrupt |
                |  • Warehouse Delays   |   |       |   (HITL Pause Point)  |
                |  • Order Details      |   |       +-----------+-----------+
                |  • Support Tickets    |   |                   |
                |  • Policy Vector RAG  |   |                   v
                +-----------+-----------+   |       +-----------------------+
                            |               |       | Human Supervisor      |
                            |               |       | Approval / Rejection  |
                            |               |       +-----------+-----------+
                            |               |                   |
                            |               |                   v
                            |               |       +-----------------------+
                            |               |       | FastMCP Write Executor|
                            |               |       |  • Issue Refund       |
                            |               |       |  • Escalate Ticket    |
                            |               |       |  • Update Order Status|
                            |               |       +-----------+-----------+
                            |               |                   |
                            +---------------+-------------------+
                                            |
                                            v
                                  +---------------------------------------+
                                  |   Telemetry & Distributed Tracing     |
                                  |  • Langfuse Cloud Action Traces       |
                                  |  • Structured JSON Audit Logs         |
                                  +---------------------------------------+
```

---

## 🗂️ Clean Repository Structure

```text
autonomous-ecommerce-agent/
├── app/
│   ├── core/                  # Pydantic v2 application settings & LLM fallback factory
│   │   ├── config.py
│   │   └── llm.py
│   ├── database/              # Neon PostgreSQL SQLAlchemy models & session
│   │   ├── models.py
│   │   └── session.py
│   └── graph/                 # LangGraph ReAct agent, state schema, and runner
│       ├── nodes.py
│       ├── state.py
│       └── workflow.py
├── demo_app.py                # Dual-Pane Obsidian B2B Streamlit Cockpit
├── Dockerfile                 # Multi-stage production container
├── docker-compose.yml         # Container composition
├── docs/                      # Architectural specifications & failure analysis
│   ├── architecture.md
│   └── failure_analysis.md
├── evals/                     # Deterministic Evaluation Harness
│   ├── datasets/              # Benchmark test datasets (RAG & Routing)
│   ├── results/               # Stored run summaries and metrics
│   ├── failure_taxonomy.py    # Standardized failure classification
│   └── runners/               # Modular evaluation runners
├── guardrails/                # Security moderation & business policy verification
│   ├── input_moderation.py
│   └── policy_compliance.py
├── knowledge_base/            # Authoritative business PDF manuals
│   └── policies/
├── mcp_server/                # Model Context Protocol (FastMCP) server
│   ├── client.py              # LangChain StructuredTool adapter
│   ├── server.py              # FastMCP tool registrations & safety metadata
│   ├── schemas/               # Strict Pydantic v2 argument schemas
│   └── tools/                 # Read-only vs. gated write tool implementations
├── observability/             # Langfuse distributed tracing & JSON logging
│   ├── langfuse_tracer.py
│   └── logging.py
├── scripts/                   # Utility and dataset generation scripts
├── tests/                     # Automated pytest suite (23 passing tests)
│   ├── unit/                  # Guardrails, MCP tools, and telemetry tests
│   └── integration/           # Multi-turn LangGraph ReAct execution tests
├── .env.example               # Safe environment variable configuration template
├── .gitignore                 # Enterprise-grade git ignore definitions
├── phase1_readme.md ... phase6_readme.md
└── requirements.txt
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.11 & 3.13)
- [Groq Cloud API Key](https://console.groq.com) (Free tier)
- Neon Serverless PostgreSQL (or local PostgreSQL)

### 2. Installation & Setup
```bash
# Clone the repository
git clone https://github.com/your-username/autonomous-ecommerce-agent.git
cd autonomous-ecommerce-agent

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate       # On Linux/macOS
venv\Scripts\activate          # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```
Edit `.env`:
```ini
GROQ_API_KEY="gsk_your_groq_key_here"
DATABASE_URL="postgresql://user:password@ep-sample.region.neon.tech/neondb?sslmode=require"
PRIMARY_MODEL="qwen/qwen3.8-27b"
FALLBACK_MODEL="openai/gpt-oss-120b"
```

### 4. Run the Dual-Pane Control Cockpit
Launch the Streamlit B2B operations cockpit:
```bash
streamlit run demo_app.py
```
Open your browser at `http://localhost:8501`.

---

## 🐳 Docker Containerization

To run the full stack inside an isolated container:
```bash
docker compose up --build
```
The application will be accessible at `http://localhost:8501`.

---

## 🧪 Testing & Evaluation

### Run Automated Pytest Suite
Run the 23 unit and integration tests:
```bash
pytest tests/ -v
```
All unit tests for guardrails, MCP schemas, LangGraph state, and multi-turn workflows pass with 100% success.

### Run Deterministic Evaluation Suite
Execute the deterministic evaluation harness against the authoritative RAG & routing benchmarks:
```bash
# Run the complete evaluation suite
python -m evals.runners.run_eval_suite

# Run RAG evaluation only
python -m evals.runners.run_eval_suite --rag

# Run Tool Routing evaluation only
python -m evals.runners.run_eval_suite --routing
```

**Benchmark Results:**
- **Tool Routing Accuracy**: `97.1%` (34/35 queries correctly routed)
- **RAG Policy Precision**: `80.0%` with `85.6%` average factual keyword coverage
- **Security Guardrail Block Rate**: `100%` on SQL injection and prompt jailbreaks

---

## 🛡️ Human-In-The-Loop (HITL) Governance

All operations that modify database state (such as issuing refunds, escalating tickets to Tier 2, or updating delivery status) are intercepted and held in a paused state using LangGraph's `interrupt()` primitive.

Operators use the **Supervisor Cockpit** on the right pane of the UI to:
1. Review the proposed action and exact SQL/tool parameters.
2. Inspect the pre-computed policy compliance check.
3. Supply supervisor notes and click **Approve Action** or **Reject Action**.
4. The agent dynamically resumes via `Command(resume=...)` and executes or safely aborts the operation.

---

## 📄 License
This project is licensed under the MIT License.
