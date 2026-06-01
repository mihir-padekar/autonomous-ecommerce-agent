from langgraph.graph import StateGraph


workflow = StateGraph(dict)


# Planner Agent
def planner_node(state):
    print("Planner Agent Executed")
    return state


# Database Agent
def database_node(state):
    print("Database Agent Executed")
    return state


# Policy Agent
def policy_node(state):
    print("Policy Agent Executed")
    return state


# Analysis Agent
def analysis_node(state):
    print("Analysis Agent Executed")
    return state


# Action Agent
def action_node(state):
    print("Action Agent Executed")
    return state


# Report Agent
def report_node(state):
    print("Report Agent Executed")
    return state


workflow.add_node("planner", planner_node)
workflow.add_node("database", database_node)
workflow.add_node("policy", policy_node)
workflow.add_node("analysis", analysis_node)
workflow.add_node("action", action_node)
workflow.add_node("report", report_node)


workflow.set_entry_point("planner")

workflow.add_edge("planner", "database")
workflow.add_edge("database", "policy")
workflow.add_edge("policy", "analysis")
workflow.add_edge("analysis", "action")
workflow.add_edge("action", "report")

graph = workflow.compile()

# TEST
result = graph.invoke(
    {
        "query": "Find delayed orders"
    }
)

print(result)