from backend.rag.retriever_service import retrieve_policy


def policy_agent(state):

    workflow = state["workflow_type"]

    policy_query_map = {

    "order_analysis":
        "delivery SLA escalation rules for delayed orders",

        "complaint_analysis":
            "customer complaint escalation policy",

        "ticket_analysis":
            "critical ticket handling and escalation policy"
    }

    query = policy_query_map.get(
        workflow,
        state["query"]
    )

    chunks = retrieve_policy(query)

    state["policy_chunks"] = chunks

    if chunks:

        top_chunk = chunks[0]

        state["policy"] = top_chunk["content"]

        state["policy_source"] = (
            top_chunk["source"]
            .split("\\")[-1]
        )

        state["policy_page"] = top_chunk["page"]

    else:

        state["policy"] = ""
        state["policy_source"] = ""
        state["policy_page"] = 0

    return state    