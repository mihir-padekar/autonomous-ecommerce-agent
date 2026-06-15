from backend.database.db import SessionLocal

from backend.database.queries import (
    get_delayed_orders,
    get_high_delay_orders,

    get_open_complaints,
    get_critical_complaints,
    get_high_and_critical_complaints,

    get_open_tickets,
    get_critical_open_tickets,

    get_order_status_summary,
    get_complaint_priority_summary,

    get_warehouse_delay_summary,
    get_top_delayed_products,

    get_full_dashboard_summary
)

QUERY_MAP = {

    "get_delayed_orders":
        get_delayed_orders,

    "get_high_delay_orders":
        get_high_delay_orders,

    "get_open_complaints":
        get_open_complaints,

    "get_critical_complaints":
        get_critical_complaints,

    "get_high_and_critical_complaints":
        get_high_and_critical_complaints,

    "get_open_tickets":
        get_open_tickets,

    "get_critical_open_tickets":
        get_critical_open_tickets,

    "get_order_status_summary":
        get_order_status_summary,

    "get_complaint_priority_summary":
        get_complaint_priority_summary,

    "get_warehouse_delay_summary":
        get_warehouse_delay_summary,

    "get_top_delayed_products":
        get_top_delayed_products,

    "get_full_dashboard_summary":
        get_full_dashboard_summary
}

def database_agent(state):

    db = SessionLocal()

    try:

        query_function = state["query_function"]

        if query_function not in QUERY_MAP:

            state["error"] = (
                f"Unsupported query function: {query_function}"
            )

            state["workflow_type"] = "unknown"

            return state

        func = QUERY_MAP[query_function]

        result = func(db)

        state["data"] = result

        return state

    finally:

        db.close()