import os
import sys
import time
import uuid
import streamlit as st
import pandas as pd

# Set page config for a widescreen B2B SaaS experience
st.set_page_config(
    page_title="Operations Copilot | Autonomous E-Commerce",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Obsidian Dark B2B Theme
st.markdown("""
<style>
    /* Global Obsidian Theme */
    .stApp {
        background-color: #0B0F17;
        color: #E2E8F0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top Header */
    .main-header {
        border-bottom: 1px solid #1E293B;
        padding-bottom: 12px;
        margin-bottom: 20px;
    }
    .main-title {
        font-size: 24px;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: -0.5px;
    }
    .sub-title {
        font-size: 13px;
        color: #94A3B8;
    }
    
    /* Status Badges */
    .badge-read {
        background-color: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-write {
        background-color: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-pass {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-fail {
        background-color: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }
    
    /* Control Cockpit Card */
    .cockpit-card {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
    }
    .approval-alert {
        background: rgba(245, 158, 11, 0.08);
        border: 1px solid #F59E0B;
        border-radius: 8px;
        padding: 16px;
        margin-top: 10px;
        margin-bottom: 16px;
    }
    
    /* Metric Cards */
    .metric-box {
        background: #131D2E;
        border: 1px solid #1E293B;
        padding: 12px;
        border-radius: 6px;
        text-align: center;
    }
    .metric-value {
        font-size: 20px;
        font-weight: 700;
        color: #F8FAFC;
    }
    .metric-label {
        font-size: 11px;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# Import backend agent modules
from app.graph.workflow import run_agent, resume_agent
from app.core.config import settings

# Initialize Session State
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"session-{uuid.uuid4().hex[:8]}"
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 Hello! I am your **Autonomous E-Commerce Operations Copilot**.\n\nI can analyze warehouse delivery delays, track orders and complaints, consult SLA policies, and perform operational tasks like issuing refunds and escalating tickets under human supervision.\n\n*Try asking:*\n- *'Which warehouses have the most delayed orders this week?'*\n- *'Check details for Order #1'*\n- *'Issue a full refund for Order #1 due to severe delivery delay'*"
        }
    ]
if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = None
if "audit_history" not in st.session_state:
    st.session_state.audit_history = []
if "query_count" not in st.session_state:
    st.session_state.query_count = 0
if "hitl_interventions" not in st.session_state:
    st.session_state.hitl_interventions = 0

# --- Top App Header ---
st.markdown("""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div class="main-title">⚡ Autonomous E-Commerce Operations Copilot</div>
            <div class="sub-title">Model Context Protocol (MCP) • LangGraph ReAct Agent • Human-In-The-Loop Governance</div>
        </div>
        <div>
            <span class="badge-read">PRIMARY: Groq Qwen 27B</span> &nbsp;
            <span class="badge-pass">DATABASE: Connected</span> &nbsp;
            <span class="badge-write">HITL: Active</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Sidebar / Controls ---
with st.sidebar:
    st.markdown("### 🎛️ Session Controls")
    st.markdown(f"**Session ID:** `{st.session_state.thread_id}`")
    
    if st.button("🔄 Reset Conversation Thread", use_container_width=True):
        st.session_state.thread_id = f"session-{uuid.uuid4().hex[:8]}"
        st.session_state.messages = [
            {"role": "assistant", "content": "Thread reset. How can I assist you with operations today?"}
        ]
        st.session_state.pending_approval = None
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Live Session Metrics")
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{st.session_state.query_count}</div>
            <div class="metric-label">Queries</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{st.session_state.hitl_interventions}</div>
            <div class="metric-label">HITL Pauses</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🛡️ Active Safety Controls")
    st.markdown("""
    - **Prompt Injection Defense**: Active
    - **Credential Redaction**: Enabled
    - **Max Auto-Refund Limit**: \$1,000.00
    - **SLA Delay Policy Gate**: $\\ge$ 5 Days
    """)
    
    st.markdown("---")
    st.markdown("### 🔗 Architecture Links")
    st.markdown("- [FastAPI Docs (Local)](http://localhost:8000/docs)")
    st.markdown("- [Failure Analysis Report](file:///docs/failure_analysis.md)")
    st.markdown("- [Source Code (GitHub)](https://github.com/)")

# --- Dual-Pane Layout ---
col_chat, col_cockpit = st.columns([6, 4], gap="large")

# ==============================================================================
# LEFT PANE: Conversational Copilot
# ==============================================================================
with col_chat:
    st.markdown("#### 💬 Operations Command Stream")
    
    # Message History Container
    chat_container = st.container(height=520)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Chat Input
    user_prompt = st.chat_input("Ask about delays, look up policies, or propose refunds...", disabled=(st.session_state.pending_approval is not None))

    if user_prompt:
        # Append User Message
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        st.session_state.query_count += 1
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_prompt)

            with st.chat_message("assistant"):
                with st.spinner("🤖 Copilot reasoning & inspecting tools..."):
                    t0 = time.perf_counter()
                    try:
                        response = run_agent(query=user_prompt, thread_id=st.session_state.thread_id)
                        latency = (time.perf_counter() - t0)

                        if response["status"] == "pending_approval":
                            st.session_state.hitl_interventions += 1
                            st.session_state.pending_approval = response["approval_request"]
                            assistant_text = (
                                f"⚠️ **Action Proposed**: I have prepared the requested operation: `{response['approval_request']['tool_name']}`.\n\n"
                                f"Because this action mutates operational state, **it has been paused for Human-in-the-Loop approval** in the right-hand panel."
                            )
                            st.markdown(assistant_text)
                            st.session_state.messages.append({"role": "assistant", "content": assistant_text})
                        else:
                            reply = response["response"]
                            st.markdown(reply)
                            st.caption(f"⚡ Turn completed in {latency:.2f}s")
                            st.session_state.messages.append({"role": "assistant", "content": reply})
                            
                            # Synchronize cumulative audit log from state (do not duplicate)
                            if "audit_log" in response:
                                st.session_state.audit_history = list(response["audit_log"])
                    except Exception as exc:
                        err_msg = str(exc)
                        if "413" in err_msg or "rate_limit_exceeded" in err_msg:
                            friendly_msg = (
                                "⚠️ **Groq Rate Limit Reached (Free Tier)**: "
                                "Groq's on-demand per-minute token quota was temporarily exceeded. "
                                "Please wait 15–20 seconds and retry, or click **🔄 Reset Conversation Thread** in the sidebar."
                            )
                        else:
                            friendly_msg = f"❌ **Execution Error**: {err_msg}"
                        st.error(friendly_msg)
                        st.session_state.messages.append({"role": "assistant", "content": friendly_msg})

        st.rerun()

# ==============================================================================
# RIGHT PANE: Supervisor Approval & Audit Cockpit
# ==============================================================================
with col_cockpit:
    st.markdown("#### 🛡️ Supervisor Cockpit & Governance")

    # 1. PENDING APPROVAL CARD
    if st.session_state.pending_approval:
        req = st.session_state.pending_approval
        tool_name = req.get("tool_name", "Unknown Tool")
        args = req.get("tool_args", {})
        comp = req.get("compliance_check", {})
        is_compliant = comp.get("is_compliant", True)
        reasons = comp.get("reasons", [])
        risk_level = comp.get("risk_level", "LOW")

        st.markdown(f"""
        <div class="approval-alert">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#F59E0B; font-size:14px;">⚠️ APPROVAL REQUIRED</span>
                <span class="badge-write">RISK: {risk_level}</span>
            </div>
            <div style="font-size:13px; color:#E2E8F0; margin-top:8px;">
                <strong>Action:</strong> <code>{tool_name}</code>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("🔍 Proposed Tool Parameters", expanded=True):
            st.json(args)

        with st.expander("📋 SLA Policy Compliance Check", expanded=True):
            if is_compliant:
                st.markdown("<span class='badge-pass'>✓ SLA COMPLIANT</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='badge-fail'>✗ SLA VIOLATION FLAGGED</span>", unsafe_allow_html=True)
            for r in reasons:
                st.markdown(f"- {r}")

        supervisor_name = st.text_input("Reviewer Name / ID", value="Supervisor Alex", key="sup_name")
        supervisor_notes = st.text_area("Review Comments / Notes", placeholder="e.g. Approved per Section 4.2 of delivery SLA...", key="sup_notes")

        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("✅ Approve & Execute", use_container_width=True, type="primary"):
                with st.spinner("Executing approved action on database..."):
                    res = resume_agent(
                        thread_id=st.session_state.thread_id,
                        decision="approved",
                        approved_by=supervisor_name,
                        notes=supervisor_notes
                    )
                    st.session_state.pending_approval = None
                    if res.get("status") == "error":
                        st.error(res.get("response", "Error resuming workflow."))
                    else:
                        reply_text = res.get("response", res.get("message", "Action approved and executed."))
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"✅ **Approved by {supervisor_name}**: {reply_text}"
                        })
                        if "audit_log" in res:
                            st.session_state.audit_history = list(res["audit_log"])
                        st.success("Action executed and recorded in audit log!")
                    time.sleep(0.8)
                    st.rerun()

        with btn_c2:
            if st.button("❌ Reject Proposal", use_container_width=True):
                with st.spinner("Cancelling action..."):
                    res = resume_agent(
                        thread_id=st.session_state.thread_id,
                        decision="rejected",
                        approved_by=supervisor_name,
                        notes=supervisor_notes or "Rejected by supervisor"
                    )
                    st.session_state.pending_approval = None
                    if res.get("status") == "error":
                        st.error(res.get("response", "Error resuming workflow."))
                    else:
                        reply_text = res.get("response", res.get("message", "Action rejected. No changes applied."))
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"❌ **Rejected by {supervisor_name}**: {reply_text}"
                        })
                        if "audit_log" in res:
                            st.session_state.audit_history = list(res["audit_log"])
                        st.info("Action rejected. No database changes were applied.")
                    time.sleep(0.8)
                    st.rerun()

    else:
        st.markdown("""
        <div class="cockpit-card" style="text-align: center; color: #64748B;">
            <div style="font-size: 24px; margin-bottom: 6px;">🟢</div>
            <div style="font-size: 13px; font-weight: 600; color: #94A3B8;">System Idle / Safe</div>
            <div style="font-size: 11px; margin-top: 4px;">No write operations pending approval. Read-only queries resolve autonomously.</div>
        </div>
        """, unsafe_allow_html=True)

    # 2. AUDIT TRAIL STREAM
    st.markdown("##### 📜 Live Audit Trail")
    if st.session_state.audit_history:
        for idx, audit in enumerate(reversed(st.session_state.audit_history[-5:])):
            event = audit.get("action") or audit.get("event", "ACTION")
            status = audit.get("status", "EXECUTED")
            reviewer = audit.get("approved_by", "System")
            
            ts = audit.get("timestamp", "")
            ts_badge = f"<span style='color: #64748B; float: right; font-size: 11px;'>{ts}</span>" if ts else ""
            status_color = "#34D399" if "APPROVED" in status else "#F87171"
            st.markdown(f"""
            <div style="border-left: 3px solid {status_color}; padding-left: 10px; margin-bottom: 8px; font-size: 12px;">
                {ts_badge}
                <strong style="color: #F8FAFC;">{event}</strong> — <span style="color: {status_color};">{status}</span><br>
                <span style="color: #94A3B8;">Reviewer: {reviewer}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No audit events recorded in this session yet.")

