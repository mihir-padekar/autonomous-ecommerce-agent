# app/database/models.py
# This file defines all 4 database tables as Python classes.
# SQLAlchemy will use these classes to create actual tables in PostgreSQL.

from sqlalchemy import Column, Integer, String, Text, Float, Date, DateTime, ForeignKey
from backend.database.db import Base


class Order(Base):
    """
    Represents the 'orders' table.
    Stores all customer order information.
    """
    __tablename__ = "orders"

    order_id                = Column(Integer, primary_key=True, index=True)
    customer_id             = Column(Integer, nullable=False)
    customer_name           = Column(String(100), nullable=False)
    product_name            = Column(String(200), nullable=False)
    order_date              = Column(Date, nullable=False)
    expected_delivery_date  = Column(Date, nullable=False)
    actual_delivery_date    = Column(Date, nullable=True)   # NULL if not yet delivered
    status                  = Column(String(50), nullable=False)  # Pending / Delayed / Delivered
    delay_days              = Column(Integer, default=0)
    warehouse               = Column(String(100), nullable=False)


class Complaint(Base):
    """
    Represents the 'complaints' table.
    Stores customer complaints linked to orders.
    """
    __tablename__ = "complaints"

    complaint_id    = Column(Integer, primary_key=True, index=True)
    customer_id     = Column(Integer, nullable=False)
    customer_name   = Column(String(100), nullable=False)
    order_id        = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    complaint_text  = Column(Text, nullable=False)
    category        = Column(String(100), nullable=False)   # e.g. Delivery Delay, Damaged Product
    priority        = Column(String(50), nullable=False)    # Low / Medium / High / Critical
    status          = Column(String(50), nullable=False)    # Open / In Progress / Resolved
    created_at      = Column(DateTime, nullable=False)


class Ticket(Base):
    """
    Represents the 'tickets' table.
    Each complaint generates a support ticket assigned to a team.
    """
    __tablename__ = "tickets"

    ticket_id       = Column(Integer, primary_key=True, index=True)
    complaint_id    = Column(Integer, ForeignKey("complaints.complaint_id"), nullable=False)
    issue_type      = Column(String(100), nullable=False)
    priority        = Column(String(50), nullable=False)
    assigned_team   = Column(String(100), nullable=False)   # e.g. Logistics Team, Returns Team
    status          = Column(String(50), nullable=False)
    created_at      = Column(DateTime, nullable=False)
    resolved_at     = Column(DateTime, nullable=True)       # NULL if not yet resolved


class WorkflowLog(Base):
    """
    Represents the 'workflow_logs' table.
    The AI agents will write their activity here automatically as they run.
    This table starts empty — agents fill it during execution.
    """
    __tablename__ = "workflow_log"

    log_id          = Column(Integer, primary_key=True, index=True, autoincrement=True)
    workflow_id     = Column(String(100), nullable=False)   # unique ID per workflow run
    user_query      = Column(Text, nullable=True)           # the original user question
    agent_name      = Column(String(100), nullable=False)   # which agent ran (e.g. DatabaseAgent)
    action          = Column(Text, nullable=False)          # what it did
    status          = Column(String(50), nullable=False)    # Success / Failed / In Progress
    execution_time  = Column(Float, nullable=True)          # how many seconds it took
    timestamp       = Column(DateTime, nullable=False)

class WorkflowExecution(Base):

    __tablename__ = "workflow_execution"

    execution_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    workflow_id = Column(
        String(100),
        unique=True,
        nullable=False
    )

    workflow_name = Column(
        String(100),
        nullable=False
    )

    user_query = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False
    )

    started_at = Column(
        DateTime,
        nullable=False
    )

    completed_at = Column(
        DateTime
    )

    duration_seconds = Column(
        Float
    )