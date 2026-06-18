import uuid


from langgraph.graph import StateGraph
from backend.agents.planner_agent import planner_agent
from backend.agents.database_agent import database_agent
from backend.agents.policy_agent import policy_agent
from backend.agents.analysis_agent import analysis_agent
from backend.agents.report_agent import report_agent
from backend.agents.compliance_agent import compliance_agent
from backend.agents.executive_summary_agent import executive_summary_agent
from backend.agents.chat_response_agent import chat_response_agent
from backend.config.query_metadata import QUERY_METADATA
from datetime import datetime

from backend.database.db import SessionLocal
from backend.database.models import (
    WorkflowExecution,
    WorkflowLog
)
import time

from backend.services.workflow_logger import (
    create_execution,
    complete_execution,
    log_agent_step
)

def create_execution(
    workflow_id,
    workflow_name,
    query
):
    db = SessionLocal()

    try:

        execution = WorkflowExecution(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            user_query=query,
            status="RUNNING",
            started_at=datetime.utcnow()
        )

        db.add(execution)
        db.commit()

    finally:
        db.close()


def complete_execution(
    workflow_id,
    status="COMPLETED"
):
    db = SessionLocal()

    try:

        execution = (
            db.query(WorkflowExecution)
            .filter(
                WorkflowExecution.workflow_id == workflow_id
            )
            .first()
        )

        if execution:

            execution.status = status

            execution.completed_at = datetime.utcnow()

            execution.duration_seconds = (
                execution.completed_at
                - execution.started_at
            ).total_seconds()

            db.commit()

    finally:
        db.close()


def log_agent_step(
    workflow_id,
    query,
    agent_name,
    action,
    status,
    execution_time
):
    db = SessionLocal()

    try:

        log = WorkflowLog(
            workflow_id=workflow_id,
            user_query=query,
            agent_name=agent_name,
            action=action,
            status=status,
            execution_time=execution_time,
            timestamp=datetime.utcnow()
        )

        db.add(log)
        db.commit()

    finally:
        db.close()

workflow = StateGraph(dict)


# Planner Agent
def planner_node(state):

    start = time.time()

    workflow_id = str(uuid.uuid4())

    state["workflow_id"] = workflow_id

    result = planner_agent(
        query=state["query"],
        history=state.get("history", [])
    )

    state["query_function"] = result["query_function"]

    if state["query_function"] not in QUERY_METADATA:

        raise ValueError(
            f"Unsupported query: {state['query']}"
        )

    metadata = QUERY_METADATA[
        state["query_function"]
    ]

    state["workflow_type"] = metadata["workflow"]

    state["data_type"] = metadata["data_type"]

    state["summary_type"] = metadata.get(
        "summary_type"
    )

    create_execution(
        workflow_id,
        state["workflow_type"],
        state["query"]
    )

    state["summary_type"] = metadata.get(
        "summary_type"
    )

    log_agent_step(
        workflow_id=workflow_id,
        query=state["query"],
        agent_name="Planner Agent",
        action="Determine workflow",
        status="SUCCESS",
        execution_time=round(
            time.time() - start,
            3
        )
    )

    return state

# Database Agent
def database_node(state):

    start = time.time()

    state = database_agent(state)

    log_agent_step(
        workflow_id=state["workflow_id"],
        query=state["query"],
        agent_name="Database Agent",
        action="Fetch database records",
        status="SUCCESS",
        execution_time=round(
            time.time() - start,
            3
        )
    )

    return state


# Policy Agent
def policy_node(state):

    start = time.time()

    state = policy_agent(state)

    log_agent_step(
        workflow_id=state["workflow_id"],
        query=state["query"],
        agent_name="Policy Agent",
        action="Retrieve policy context",
        status="SUCCESS",
        execution_time=round(
            time.time() - start,
            3
        )
    )

    return state

# Analysis Agent
def analysis_node(state):

    start = time.time()

    state = analysis_agent(state)

    log_agent_step(
        workflow_id=state["workflow_id"],
        query=state["query"],
        agent_name="Analysis Agent",
        action="Analyze operational data",
        status="SUCCESS",
        execution_time=round(
            time.time() - start,
            3
        )
    )

    return state

# Compliance Agent
def compliance_node(state):

    start = time.time()

    state = compliance_agent(state)

    log_agent_step(
        workflow_id=state["workflow_id"],
        query=state["query"],
        agent_name="Compliance Agent",
        action="Evaluate compliance",
        status="SUCCESS",
        execution_time=round(
            time.time() - start,
            3
        )
    )

    return state

def executive_summary_node(state):

    start = time.time()

    state = executive_summary_agent(state)

    log_agent_step(
        workflow_id=state["workflow_id"],
        query=state["query"],
        agent_name="Executive Summary Agent",
        action="Generate executive summary",
        status="SUCCESS",
        execution_time=round(
            time.time() - start,
            3
        )
    )

    return state

# Report Agent
def report_node(state):

    start = time.time()

    state = report_agent(state)

    log_agent_step(
        workflow_id=state["workflow_id"],
        query=state["query"],
        agent_name="Report Agent",
        action="Generate final report",
        status="SUCCESS",
        execution_time=round(
            time.time() - start,
            3
        )
    )

    complete_execution(
        state["workflow_id"]
    )

    return state


workflow.add_node("planner", planner_node)
workflow.add_node("database", database_node)
workflow.add_node("policy", policy_node)
workflow.add_node("compliance",compliance_node)
workflow.add_node("analysis", analysis_node)
workflow.add_node("executive_summary", executive_summary_node)
workflow.add_node("chat_response",chat_response_agent)
workflow.add_node("report", report_node)


workflow.set_entry_point("planner")

workflow.add_edge("planner", "database")
workflow.add_edge("database", "analysis")
workflow.add_edge("analysis", "policy")
workflow.add_edge("policy", "compliance")
workflow.add_edge("compliance", "executive_summary")
workflow.add_edge("executive_summary","chat_response")
workflow.add_edge("chat_response", "report")

workflow.set_finish_point("report")

graph = workflow.compile()


"""
# TEST
result = graph.invoke(
    {
        "query": "Show executive dashboard"
    }
)

print(result["analysis"])
print(result["report"])
"""