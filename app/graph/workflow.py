from typing import Any, Dict, Optional
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import Command
from app.graph.nodes import agent_node, router_condition, tool_executor_node
from app.graph.state import AgentState
from guardrails.input_moderation import moderate_input
from guardrails.policy_compliance import sanitize_agent_output
from observability.langfuse_tracer import trace_action
from observability.logging import app_logger


def build_workflow():
    """
    Constructs and compiles the Operations Copilot ReAct workflow
    with memory checkpointer and interrupt support.
    """
    builder = StateGraph(AgentState)

    # Register Nodes
    builder.add_node("agent", agent_node)
    builder.add_node("tool_executor", tool_executor_node)

    # Set Entry Point
    builder.set_entry_point("agent")

    # Routing Edge from Agent
    builder.add_conditional_edges(
        "agent",
        router_condition,
        {
            "tool_executor": "tool_executor",
            "__end__": END
        }
    )

    # Cycle Edge from Tool Executor back to Agent
    builder.add_edge("tool_executor", "agent")

    # In-memory checkpointer for thread persistence & HITL state
    checkpointer = MemorySaver()
    workflow = builder.compile(checkpointer=checkpointer)
    return workflow


# Compiled singleton graph
graph = build_workflow()


@trace_action(name="run_agent_turn")
def run_agent(query: str, thread_id: str) -> Dict[str, Any]:
    """
    Executes a turn in the Operations Copilot agent workflow for a given thread.
    Passes input through security guardrails before processing.
    """
    # 1. Input Moderation Guardrail Check
    moderation = moderate_input(query)
    if not moderation.allowed:
        app_logger.warning(
            f"Blocked query by guardrail: {moderation.reason}",
            extra={"thread_id": thread_id, "event": "GUARDRAIL_BLOCKED", "category": moderation.category}
        )
        return {
            "status": "completed",
            "thread_id": thread_id,
            "requires_action": False,
            "response": f"Security Guardrail: Request blocked. {moderation.reason}",
            "audit_log": [
                {
                    "event": "INPUT_MODERATION_BLOCKED",
                    "category": moderation.category,
                    "reason": moderation.reason
                }
            ]
        }

    app_logger.info(
        f"Processing agent query for thread {thread_id}",
        extra={"thread_id": thread_id, "event": "AGENT_RUN_START"}
    )

    config = {"configurable": {"thread_id": thread_id}}
    input_state = {
        "messages": [HumanMessage(content=moderation.sanitized_input)],
        "thread_id": thread_id
    }

    # Execute workflow until completion or interrupt pause
    graph.invoke(input_state, config=config)

    # Inspect execution snapshot
    snapshot = graph.get_state(config)

    if snapshot.next:
        # Graph paused at an interrupt
        interrupt_payloads = [
            i.value for task in snapshot.tasks for i in task.interrupts
        ]
        app_logger.info(
            f"Workflow paused awaiting supervisor approval on thread {thread_id}",
            extra={"thread_id": thread_id, "event": "HITL_PAUSE"}
        )
        return {
            "status": "pending_approval",
            "thread_id": thread_id,
            "requires_action": True,
            "approval_request": interrupt_payloads[0] if interrupt_payloads else None,
            "message": "Action paused. Supervisor approval required before mutating database state."
        }

    last_msg = snapshot.values["messages"][-1] if "messages" in snapshot.values and snapshot.values["messages"] else None
    raw_response = last_msg.content if last_msg else "Workflow concluded without response text."

    # 2. Output Sanitization Guardrail
    sanitized_response = sanitize_agent_output(raw_response)

    app_logger.info(
        f"Workflow turn concluded successfully on thread {thread_id}",
        extra={"thread_id": thread_id, "event": "AGENT_RUN_COMPLETE"}
    )

    return {
        "status": "completed",
        "thread_id": thread_id,
        "requires_action": False,
        "response": sanitized_response,
        "audit_log": snapshot.values.get("audit_log", [])
    }


@trace_action(name="resume_agent_turn")
def resume_agent(
    thread_id: str,
    decision: str,
    approved_by: str = "Operations Supervisor",
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Resumes an interrupted workflow thread with a human approval or rejection decision.
    """
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = graph.get_state(config)

    if not snapshot.next:
        err_msg = f"Thread '{thread_id}' is not paused for approval or has already finished."
        return {
            "status": "error",
            "thread_id": thread_id,
            "response": err_msg,
            "message": err_msg
        }

    app_logger.info(
        f"Resuming workflow thread {thread_id} with decision '{decision}' by {approved_by}",
        extra={"thread_id": thread_id, "event": "HITL_RESUME", "decision": decision}
    )

    resume_payload = {
        "decision": decision.lower(),
        "approved_by": approved_by,
        "notes": notes or ""
    }

    # Resume the workflow using LangGraph Command
    graph.invoke(Command(resume=resume_payload), config=config)

    final_snapshot = graph.get_state(config)

    if final_snapshot.next:
        interrupt_payloads = [
            i.value for task in final_snapshot.tasks for i in task.interrupts
        ]
        return {
            "status": "pending_approval",
            "thread_id": thread_id,
            "requires_action": True,
            "approval_request": interrupt_payloads[0] if interrupt_payloads else None,
            "response": "Action completed, but additional supervisor approval is required for the next step.",
            "message": "Action paused. Supervisor approval required before mutating database state.",
            "audit_log": final_snapshot.values.get("audit_log", [])
        }

    last_msg = final_snapshot.values["messages"][-1] if "messages" in final_snapshot.values else None
    raw_response = last_msg.content if last_msg else "Execution finished."

    sanitized_response = sanitize_agent_output(raw_response)

    return {
        "status": "completed",
        "thread_id": thread_id,
        "decision_applied": decision.lower(),
        "response": sanitized_response,
        "audit_log": final_snapshot.values.get("audit_log", [])
    }
