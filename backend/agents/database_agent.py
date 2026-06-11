from backend.database.db import SessionLocal

from backend.database.queries import (
    get_delayed_orders,
    get_open_complaints,
    get_open_tickets
)

def database_agent(state):

    db = SessionLocal()

    workflow = state["workflow_type"]

    try:

        if workflow == "delayed_orders":

            state["orders"] = get_delayed_orders(db)

        elif workflow == "complaint_analysis":

            state["complaints"] = get_open_complaints(db)

        elif workflow == "ticket_analysis":

            state["tickets"] = get_open_tickets(db)

        return state

    finally:

        db.close()