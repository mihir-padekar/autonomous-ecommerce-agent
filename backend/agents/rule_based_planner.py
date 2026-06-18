def planner_agent(query, history=None):

    if history is None:
        history = []

    print("CURRENT QUERY:", query)

    print("HISTORY:", history)

    query = query.lower()

    if "open tickets" in query:

        return {
            "workflow_type": "ticket_analysis",
            "query_function": "get_open_tickets"
        }

    elif "critical tickets" in query:

        return {
            "workflow_type": "ticket_analysis",
            "query_function": "get_critical_open_tickets"
        }

    elif "delayed orders" in query:

        return {
            "workflow_type": "delayed_orders",
            "query_function": "get_delayed_orders"
        }

    elif "warehouse" in query:

        return {
            "workflow_type": "warehouse_analysis",
            "query_function": "get_warehouse_delay_summary"
        }
    
    elif "top delayed products" in query:
        return {
            "workflow_type": "product_analysis",
            "query_function": "get_top_delayed_products"
        }

    elif "warehouse" in query and "delay" in query:
        print("Summary Type:", state["summary_type"])
        return {
            "workflow_type": "warehouse_analysis",
            "query_function": "get_warehouse_delay_summary"
        }

    elif "dashboard" in query:

        return {

            "workflow_type": "dashboard_analysis",

            "query_function": "get_full_dashboard_summary"
        }

    return {
        "workflow_type": "unknown",
        "query_function": "unknown"
    }
