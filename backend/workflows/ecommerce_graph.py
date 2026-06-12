from langgraph.graph import StateGraph
from backend.agents.planner_agent import planner_agent
from backend.agents.database_agent import database_agent
from backend.agents.policy_agent import policy_agent
from backend.agents.analysis_agent import analysis_agent
from backend.agents.report_agent import report_agent
from backend.agents.compliance_agent import compliance_agent
from backend.agents.executive_summary_agent import executive_summary_agent
from backend.config.query_metadata import QUERY_METADATA

workflow = StateGraph(dict)


# Planner Agent
def planner_node(state):

    result = planner_agent(
        state["query"]
    )

    state["workflow_type"] = result["workflow_type"]

    state["query_function"] = result["query_function"]

    metadata = QUERY_METADATA[
    state["query_function"]
    ]

    state["data_type"] = metadata[
        "data_type"
    ]

    print("Workflow:", state["workflow_type"])
    print("Function:", state["query_function"])
    print("Data Type:", state["data_type"])

    return state

# Database Agent
def database_node(state):

    state = database_agent(state)

    return state


# Policy Agent
def policy_node(state):
    state = policy_agent(state)
    return state


# Analysis Agent
def analysis_node(state):
    state = analysis_agent(state)
    return state

# Compliance Agent
def compliance_node(state):
    state = compliance_agent(state)
    return state



# Report Agent
def report_node(state):
    state = report_agent(state)
    return state


workflow.add_node("planner", planner_node)
workflow.add_node("database", database_node)
workflow.add_node("policy", policy_node)
workflow.add_node("compliance",compliance_node)
workflow.add_node("analysis", analysis_node)
workflow.add_node("executive_summary", executive_summary_agent)
workflow.add_node("report", report_node)


workflow.set_entry_point("planner")

workflow.add_edge("planner", "database")
workflow.add_edge("database", "analysis")
workflow.add_edge("analysis", "policy")
workflow.add_edge("policy", "compliance")
workflow.add_edge("compliance", "executive_summary")
workflow.add_edge("executive_summary", "report")

workflow.set_finish_point("report")

graph = workflow.compile()



# TEST
result = graph.invoke(
    {
        "query": "show top delayed products"
    }
)

print(result["analysis"])
print(result["report"])
