import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage, ToolMessage
from langgraph.types import interrupt
from app.core.llm import get_llm
from app.graph.state import AgentState
from mcp_server.client import mcp_client


SYSTEM_PROMPT = """You are an Autonomous Operations Copilot for an enterprise e-commerce platform.
Your objective is to answer operational questions, investigate delivery delays, and perform policy-compliant customer service actions.

You have access to the following MCP tools:
- get_warehouse_delay_summary: Query delayed shipment statistics and warehouse performance.
- get_order_details: Retrieve full order fulfillment information and linked complaints/tickets.
- get_customer_complaints: Search complaints by customer, order, category, or status.
- get_ticket_details: Search operations support tickets.
- lookup_policy: Search authoritative PDF manuals (SLA delivery windows, refund policies, escalation matrices).
- issue_refund: Propose an order refund (Gated: requires human supervisor confirmation).
- escalate_ticket: Propose ticket escalation to Tier 2 (Gated: requires human supervisor confirmation).
- update_order_status: Modify order delivery status (Gated: requires human supervisor confirmation).

Guidelines:
1. Always base factual statements on data returned by your tools. Do not invent order IDs, delay days, or policy terms.
2. For refund or escalation requests:
   - FIRST verify the order/ticket using get_order_details or get_ticket_details.
   - SECOND verify eligibility with lookup_policy.
   - THIRD invoke the appropriate write tool (issue_refund, escalate_ticket, or update_order_status).
3. If an action was rejected by a human supervisor, politely explain the rejection reason to the user without attempting to force the action again.
4. Keep answers professional, concise, and structured with bullet points where appropriate.
"""


def _trim_history_safely(messages: List[BaseMessage], max_tokens: int = 3200) -> List[BaseMessage]:
    """
    Trims conversation history to stay safely under Groq's input token per minute (ITPM) limit,
    while preserving the SystemMessage and ensuring tool_calls / ToolMessages remain valid pairs.
    """
    if len(messages) <= 4:
        return messages

    def approx_token_counter(msgs: List[BaseMessage]) -> int:
        total = 0
        for m in msgs:
            txt = m.content if isinstance(m.content, str) else str(m.content)
            total += len(txt) // 4 + 10
            if isinstance(m, AIMessage) and m.tool_calls:
                total += len(str(m.tool_calls)) // 4
        return total

    try:
        from langchain_core.messages import trim_messages
        trimmed = trim_messages(
            messages,
            max_tokens=max_tokens,
            strategy="last",
            token_counter=approx_token_counter,
            include_system=True,
            allow_partial=False
        )
        return trimmed
    except Exception:
        # Fallback window: keep system prompt + last 6 messages
        if messages and isinstance(messages[0], SystemMessage):
            return [messages[0]] + messages[-6:]
        return messages[-6:]


def agent_node(state: AgentState) -> Dict[str, Any]:
    """
    LLM reasoning node: evaluates message history and decides whether
    to respond directly or call one or more MCP tools.
    """
    llm = get_llm()
    tools = mcp_client.get_langchain_tools()
    llm_with_tools = llm.bind_tools(tools)

    messages = list(state.get("messages", []))
    # Ensure system prompt is present at the beginning
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    # Safely trim conversation history to fit within Groq's free tier token budget
    safe_messages = _trim_history_safely(messages, max_tokens=3200)

    response: AIMessage = llm_with_tools.invoke(safe_messages)
    return {"messages": [response]}


def tool_executor_node(state: AgentState) -> Dict[str, Any]:
    """
    Executes tools requested by the agent node.
    Read-only tools execute automatically.
    Risky write tools pause execution via LangGraph interrupt() awaiting human review.
    """
    messages = state.get("messages", [])
    if not messages:
        return {}

    last_message = messages[-1]
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return {}

    tool_results: List[ToolMessage] = []
    audit_events: List[Dict[str, Any]] = list(state.get("audit_log", []))

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]

        is_write = mcp_client.is_approval_required(tool_name)

        if is_write:
            # Evaluate policy compliance guardrail before presenting to supervisor
            compliance_info = {"is_compliant": True, "reasons": [], "risk_level": "LOW"}
            if tool_name == "issue_refund":
                from guardrails.policy_compliance import verify_refund_policy
                res = verify_refund_policy(
                    order_id=tool_args.get("order_id", 0),
                    reason=tool_args.get("reason", ""),
                    refund_amount=tool_args.get("refund_amount")
                )
                compliance_info = res.model_dump()
            elif tool_name == "escalate_ticket":
                from guardrails.policy_compliance import verify_escalation_policy
                res = verify_escalation_policy(
                    ticket_id=tool_args.get("ticket_id", 0),
                    escalation_reason=tool_args.get("escalation_reason", ""),
                    target_team=tool_args.get("target_team", "Tier 2")
                )
                compliance_info = res.model_dump()

            # Construct approval payload presented to human reviewer
            approval_request = {
                "action": "human_approval_required",
                "tool_name": tool_name,
                "tool_args": tool_args,
                "tool_call_id": tool_id,
                "compliance_check": compliance_info,
                "prompt": f"Review required: Agent requested to execute write action '{tool_name}' with parameters {tool_args}."
            }

            # PAUSE execution until resumed by human supervisor
            human_decision = interrupt(approval_request)

            decision_type = human_decision.get("decision", "rejected").lower()
            reviewer = human_decision.get("approved_by", "Operations Supervisor")
            notes = human_decision.get("notes", "")

            if decision_type == "approved":
                # Execute tool with human approval metadata
                exec_args = dict(tool_args)
                exec_args["approved_by"] = reviewer
                result = mcp_client.call_tool(tool_name, **exec_args)

                audit_events.append({
                    "action": tool_name,
                    "status": "APPROVED_AND_EXECUTED",
                    "approved_by": reviewer,
                    "notes": notes,
                    "payload": tool_args,
                    "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
                })

                payload_str = json.dumps(result.model_dump(), default=str)
                if len(payload_str) > 2500:
                    payload_str = payload_str[:2500] + "\n... [Remaining data truncated for token safety]"

                tool_results.append(
                    ToolMessage(
                        content=payload_str,
                        tool_call_id=tool_id,
                        name=tool_name
                    )
                )
            else:
                # Human rejected action
                rejection_msg = {
                    "success": False,
                    "message": f"Action '{tool_name}' was REJECTED by supervisor ({reviewer}). Justification: {notes or 'No reason provided'}. Changes were NOT applied.",
                    "action_type": "write_approval_required",
                    "requires_human_approval": False
                }

                audit_events.append({
                    "action": tool_name,
                    "status": "REJECTED",
                    "approved_by": reviewer,
                    "notes": notes,
                    "payload": tool_args,
                    "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
                })

                tool_results.append(
                    ToolMessage(
                        content=json.dumps(rejection_msg),
                        tool_call_id=tool_id,
                        name=tool_name
                    )
                )
        else:
            # Auto-execute read-only tool
            result = mcp_client.call_tool(tool_name, **tool_args)
            payload_str = json.dumps(result.model_dump(), default=str)
            if len(payload_str) > 2500:
                payload_str = payload_str[:2500] + "\n... [Remaining data truncated for token safety]"

            tool_results.append(
                ToolMessage(
                    content=payload_str,
                    tool_call_id=tool_id,
                    name=tool_name
                )
            )

    return {
        "messages": tool_results,
        "pending_approval": None,
        "audit_log": audit_events
    }


def router_condition(state: AgentState) -> Literal["tool_executor", "__end__"]:
    """
    Determines next step in the ReAct loop:
    If the agent requested tool execution, transition to tool_executor.
    Otherwise, end execution and deliver response to user.
    """
    messages = state.get("messages", [])
    if not messages:
        return "__end__"

    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tool_executor"
    return "__end__"

