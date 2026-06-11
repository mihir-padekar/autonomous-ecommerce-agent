def planner_agent(query):

    query = query.lower()

    if "delayed" in query:
        return "delayed_orders"

    elif "complaint" in query:
        return "complaint_analysis"

    elif "ticket" in query:
        return "ticket_analysis"
    elif "summary" in query:
        return "dashboard_summary"

    elif "dashboard" in query:
        return "dashboard_summary"
    return "general"