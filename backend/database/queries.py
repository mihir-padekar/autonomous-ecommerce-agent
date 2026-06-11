# backend/database/queries.py
# ============================================================
# All reusable query functions used by the AI agents.
# Organised into sections:
#   - Orders
#   - Complaints
#   - Tickets
#   - Workflow Logs
#   - Analytics / Summary
# ============================================================

from sqlalchemy.orm import Session
from sqlalchemy import text, func
from backend.database.models import Order, Complaint, Ticket, WorkflowLog
from datetime import datetime
from typing import Optional


# ═══════════════════════════════════════════════════════════
# ORDER QUERIES
# ═══════════════════════════════════════════════════════════

def get_all_orders(db: Session) -> list[Order]:
    """Return all orders."""
    return db.query(Order).all()


def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
    """Return a single order by its ID. Returns None if not found."""
    return db.query(Order).filter(Order.order_id == order_id).first()


def get_orders_by_customer(db: Session, customer_id: int) -> list[Order]:
    """Return all orders placed by a specific customer."""
    return db.query(Order).filter(Order.customer_id == customer_id).all()


def get_orders_by_status(db: Session, status: str) -> list[Order]:
    """
    Return orders filtered by status.
    Valid values: 'Delivered', 'Delayed', 'Pending'
    """
    return db.query(Order).filter(Order.status == status).all()


def get_delayed_orders(db: Session) -> list[Order]:
    """Return all orders with status = 'Delayed'."""
    return db.query(Order).filter(Order.status == "Delayed").all()


def get_pending_orders(db: Session) -> list[Order]:
    """Return all orders with status = 'Pending'."""
    return db.query(Order).filter(Order.status == "Pending").all()


def get_high_delay_orders(db: Session, min_delay_days: int = 5) -> list[Order]:
    """
    Return orders delayed by at least min_delay_days.
    Default threshold is 5 days.
    Used by agents to flag severely delayed shipments.
    """
    return (db.query(Order)
              .filter(Order.delay_days >= min_delay_days)
              .order_by(Order.delay_days.desc())
              .all())


def get_orders_by_warehouse(db: Session, warehouse: str) -> list[Order]:
    """Return all orders dispatched from a specific warehouse."""
    return db.query(Order).filter(Order.warehouse == warehouse).all()


def get_delayed_orders_by_warehouse(db: Session, warehouse: str) -> list[Order]:
    """Return delayed orders from a specific warehouse."""
    return (db.query(Order)
              .filter(Order.status == "Delayed", Order.warehouse == warehouse)
              .all())


def get_orders_paginated(db: Session, page: int = 1, page_size: int = 50) -> list[Order]:
    """
    Return orders in pages. Used by the frontend dashboard.
    page=1 returns rows 1-50, page=2 returns 51-100, etc.
    """
    offset = (page - 1) * page_size
    return db.query(Order).offset(offset).limit(page_size).all()


def count_orders_by_status(db: Session) -> dict:
    """
    Return a dict with counts per status.
    Example: {'Delivered': 650, 'Delayed': 200, 'Pending': 150}
    """
    results = (db.query(Order.status, func.count(Order.order_id))
                 .group_by(Order.status)
                 .all())
    return {status: count for status, count in results}


# ═══════════════════════════════════════════════════════════
# COMPLAINT QUERIES
# ═══════════════════════════════════════════════════════════

def get_all_complaints(db: Session) -> list[Complaint]:
    """Return all complaints."""
    return db.query(Complaint).all()


def get_complaint_by_id(db: Session, complaint_id: int) -> Optional[Complaint]:
    """Return a single complaint by its ID."""
    return db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()


def get_complaints_by_order(db: Session, order_id: int) -> list[Complaint]:
    """Return all complaints linked to a specific order."""
    return db.query(Complaint).filter(Complaint.order_id == order_id).all()


def get_complaints_by_customer(db: Session, customer_id: int) -> list[Complaint]:
    """Return all complaints raised by a specific customer."""
    return db.query(Complaint).filter(Complaint.customer_id == customer_id).all()


def get_open_complaints(db: Session) -> list[Complaint]:
    """Return all complaints with status = 'Open'."""
    return db.query(Complaint).filter(Complaint.status == "Open").all()


def get_complaints_by_status(db: Session, status: str) -> list[Complaint]:
    """Return complaints filtered by status: 'Open', 'In Progress', 'Resolved'."""
    return db.query(Complaint).filter(Complaint.status == status).all()


def get_complaints_by_priority(db: Session, priority: str) -> list[Complaint]:
    """Return complaints filtered by priority: 'Low', 'Medium', 'High', 'Critical'."""
    return db.query(Complaint).filter(Complaint.priority == priority).all()


def get_critical_complaints(db: Session) -> list[Complaint]:
    """Return all Critical priority complaints. Used by agents for urgent escalation."""
    return get_complaints_by_priority(db, "Critical")


def get_high_and_critical_complaints(db: Session) -> list[Complaint]:
    """Return High and Critical priority open complaints."""
    return (db.query(Complaint)
              .filter(Complaint.priority.in_(["High", "Critical"]),
                      Complaint.status != "Resolved")
              .order_by(Complaint.created_at.asc())
              .all())


def get_complaints_by_category(db: Session, category: str) -> list[Complaint]:
    """
    Return complaints filtered by category.
    Valid values: 'Delivery Delay', 'Damaged Product', 'Wrong Item',
                  'Defective Product', 'Missing Item'
    """
    return db.query(Complaint).filter(Complaint.category == category).all()


def count_complaints_by_status(db: Session) -> dict:
    """Return complaint counts grouped by status."""
    results = (db.query(Complaint.status, func.count(Complaint.complaint_id))
                 .group_by(Complaint.status)
                 .all())
    return {status: count for status, count in results}


def count_complaints_by_category(db: Session) -> dict:
    """Return complaint counts grouped by category."""
    results = (db.query(Complaint.category, func.count(Complaint.complaint_id))
                 .group_by(Complaint.category)
                 .all())
    return {cat: count for cat, count in results}


# ═══════════════════════════════════════════════════════════
# TICKET QUERIES
# ═══════════════════════════════════════════════════════════

def get_all_tickets(db: Session) -> list[Ticket]:
    """Return all tickets."""
    return db.query(Ticket).all()


def get_ticket_by_id(db: Session, ticket_id: int) -> Optional[Ticket]:
    """Return a single ticket by its ID."""
    return db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()


def get_tickets_by_complaint(db: Session, complaint_id: int) -> list[Ticket]:
    """Return the ticket linked to a specific complaint."""
    return db.query(Ticket).filter(Ticket.complaint_id == complaint_id).all()


def get_open_tickets(db: Session) -> list[Ticket]:
    """Return all tickets with status = 'Open'."""
    return db.query(Ticket).filter(Ticket.status == "Open").all()


def get_tickets_by_status(db: Session, status: str) -> list[Ticket]:
    """Return tickets filtered by status: 'Open', 'In Progress', 'Resolved'."""
    return db.query(Ticket).filter(Ticket.status == status).all()


def get_tickets_by_team(db: Session, team: str) -> list[Ticket]:
    """
    Return tickets assigned to a specific team.
    Valid values: 'Logistics Team', 'Returns Team', 'Quality Team', 'Customer Support'
    """
    return db.query(Ticket).filter(Ticket.assigned_team == team).all()


def get_unresolved_tickets(db: Session) -> list[Ticket]:
    """Return tickets that have not been resolved yet."""
    return db.query(Ticket).filter(Ticket.resolved_at == None).all()


def get_critical_open_tickets(db: Session) -> list[Ticket]:
    """Return Critical priority tickets that are still Open or In Progress."""
    return (db.query(Ticket)
              .filter(Ticket.priority == "Critical", Ticket.status != "Resolved")
              .all())


def count_tickets_by_team(db: Session) -> dict:
    """Return ticket counts grouped by assigned team."""
    results = (db.query(Ticket.assigned_team, func.count(Ticket.ticket_id))
                 .group_by(Ticket.assigned_team)
                 .all())
    return {team: count for team, count in results}


# ═══════════════════════════════════════════════════════════
# WORKFLOW LOG QUERIES
# ═══════════════════════════════════════════════════════════

def log_agent_action(
    db: Session,
    workflow_id: str,
    agent_name: str,
    action: str,
    status: str,
    execution_time: float = 0.0,
    user_query: str = None
) -> WorkflowLog:
    """
    Insert a new log entry when an agent performs an action.

    Called by agents like this:
        log_agent_action(db, "wf-001", "DatabaseAgent",
                         "Fetched 47 delayed orders", "Success", 0.23,
                         user_query="Show me all delayed orders")
    """
    log = WorkflowLog(
        workflow_id    = workflow_id,
        user_query     = user_query,
        agent_name     = agent_name,
        action         = action,
        status         = status,
        execution_time = execution_time,
        timestamp      = datetime.utcnow()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_all_logs(db: Session) -> list[WorkflowLog]:
    """Return all workflow logs, newest first."""
    return db.query(WorkflowLog).order_by(WorkflowLog.timestamp.desc()).all()


def get_logs_by_agent(db: Session, agent_name: str) -> list[WorkflowLog]:
    """Return logs for a specific agent (e.g. 'DatabaseAgent')."""
    return (db.query(WorkflowLog)
              .filter(WorkflowLog.agent_name == agent_name)
              .order_by(WorkflowLog.timestamp.desc())
              .all())


def get_logs_by_workflow(db: Session, workflow_id: str) -> list[WorkflowLog]:
    """Return all log entries for one complete workflow run."""
    return (db.query(WorkflowLog)
              .filter(WorkflowLog.workflow_id == workflow_id)
              .order_by(WorkflowLog.timestamp.asc())
              .all())


def get_failed_logs(db: Session) -> list[WorkflowLog]:
    """Return all log entries where an agent action failed."""
    return db.query(WorkflowLog).filter(WorkflowLog.status == "Failed").all()


def get_recent_logs(db: Session, limit: int = 50) -> list[WorkflowLog]:
    """Return the most recent N log entries. Default: last 50."""
    return (db.query(WorkflowLog)
              .order_by(WorkflowLog.timestamp.desc())
              .limit(limit)
              .all())


# ═══════════════════════════════════════════════════════════
# ANALYTICS / SUMMARY QUERIES  (Raw SQL — faster for dashboards)
# ═══════════════════════════════════════════════════════════

def get_order_status_summary(db: Session) -> list[dict]:
    """Returns count of orders grouped by status."""
    result = db.execute(text("""
        SELECT status, COUNT(*) AS count
        FROM orders
        GROUP BY status
        ORDER BY count DESC
    """))
    return [{"status": row[0], "count": row[1]} for row in result]


def get_complaint_category_summary(db: Session) -> list[dict]:
    """Returns count of complaints grouped by category."""
    result = db.execute(text("""
        SELECT category, COUNT(*) AS count
        FROM complaints
        GROUP BY category
        ORDER BY count DESC
    """))
    return [{"category": row[0], "count": row[1]} for row in result]


def get_warehouse_delay_summary(db: Session) -> list[dict]:
    """Returns average delay days per warehouse, for delayed orders only."""
    result = db.execute(text("""
        SELECT warehouse,
               COUNT(*)                          AS total_orders,
               SUM(CASE WHEN status = 'Delayed' THEN 1 ELSE 0 END) AS delayed_count,
               ROUND(AVG(CASE WHEN delay_days > 0 THEN delay_days END)::numeric, 2) AS avg_delay_days
        FROM orders
        GROUP BY warehouse
        ORDER BY delayed_count DESC
    """))
    return [
        {
            "warehouse":      row[0],
            "total_orders":   row[1],
            "delayed_count":  row[2],
            "avg_delay_days": float(row[3]) if row[3] else 0.0,
        }
        for row in result
    ]


def get_top_delayed_products(db: Session, limit: int = 10) -> list[dict]:
    """Returns the products with the most delayed orders."""
    result = db.execute(text("""
        SELECT product_name,
               COUNT(*) AS delayed_count,
               ROUND(AVG(delay_days)::numeric, 1) AS avg_delay_days
        FROM orders
        WHERE status = 'Delayed'
        GROUP BY product_name
        ORDER BY delayed_count DESC
        LIMIT :limit
    """), {"limit": limit})
    return [
        {"product": row[0], "delayed_count": row[1], "avg_delay_days": float(row[2])}
        for row in result
    ]


def get_daily_order_counts(db: Session) -> list[dict]:
    """Returns number of orders placed per day. Used for trend charts."""
    result = db.execute(text("""
        SELECT order_date, COUNT(*) AS order_count
        FROM orders
        GROUP BY order_date
        ORDER BY order_date ASC
    """))
    return [{"date": str(row[0]), "count": row[1]} for row in result]


def get_complaint_priority_summary(db: Session) -> list[dict]:
    """Returns complaint counts grouped by priority."""
    result = db.execute(text("""
        SELECT priority, COUNT(*) AS count
        FROM complaints
        GROUP BY priority
        ORDER BY CASE priority
            WHEN 'Critical' THEN 1
            WHEN 'High'     THEN 2
            WHEN 'Medium'   THEN 3
            WHEN 'Low'      THEN 4
        END
    """))
    return [{"priority": row[0], "count": row[1]} for row in result]


def get_full_dashboard_summary(db: Session) -> dict:
    """
    Single function that returns everything the dashboard needs.
    Called once to populate all metrics cards on the frontend.
    """
    return {
        "order_status":         get_order_status_summary(db),
        "complaint_categories": get_complaint_category_summary(db),
        "complaint_priorities": get_complaint_priority_summary(db),
        "warehouse_delays":     get_warehouse_delay_summary(db),
        "top_delayed_products": get_top_delayed_products(db, limit=5),
        "ticket_teams":         count_tickets_by_team(db),
    }