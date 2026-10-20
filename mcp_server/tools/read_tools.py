from typing import Any, Dict, List, Optional
from sqlalchemy import func, text
from app.database.session import SessionLocal
from app.database.models import Order, Complaint, Ticket
from mcp_server.schemas.common import ToolActionType, ToolResponse
from mcp_server.schemas.orders import (
    WarehouseDelayItem,
    WarehouseDelaySummaryResponse,
    OrderDetailsResponse,
)
from mcp_server.schemas.tickets import ComplaintItem, TicketItem
from mcp_server.schemas.policies import PolicyChunk, PolicyQueryResponse


# Lazy-loaded vector store instance
_vector_store = None

def _get_vector_store():
    global _vector_store
    if _vector_store is None:
        from backend.rag.vector_store import get_vector_store
        _vector_store = get_vector_store()
    return _vector_store


def get_warehouse_delay_summary(
    warehouse: Optional[str] = None,
    min_delay_days: int = 1,
    **kwargs
) -> ToolResponse:
    """
    Read-only tool: Returns aggregated delay statistics per warehouse.
    Auto-executes without requiring human approval.
    """
    db = SessionLocal()
    try:
        query_sql = """
            SELECT warehouse,
                   COUNT(*) AS total_orders,
                   SUM(CASE WHEN status = 'Delayed' THEN 1 ELSE 0 END) AS delayed_count,
                   ROUND(AVG(CASE WHEN delay_days >= :min_delay THEN delay_days END)::numeric, 2) AS avg_delay_days
            FROM orders
        """
        params: Dict[str, Any] = {"min_delay": min_delay_days}
        if warehouse:
            query_sql += " WHERE LOWER(warehouse) = LOWER(:wh)"
            params["wh"] = warehouse

        query_sql += " GROUP BY warehouse ORDER BY delayed_count DESC"

        result = db.execute(text(query_sql), params).fetchall()

        items: List[WarehouseDelayItem] = []
        total_delayed = 0
        most_delayed = None
        max_delayed_count = -1

        for row in result:
            wh_name = str(row[0])
            total = int(row[1])
            delayed = int(row[2]) if row[2] else 0
            avg_delay = float(row[3]) if row[3] else 0.0

            total_delayed += delayed
            if delayed > max_delayed_count:
                max_delayed_count = delayed
                most_delayed = wh_name

            items.append(
                WarehouseDelayItem(
                    warehouse=wh_name,
                    total_orders=total,
                    delayed_count=delayed,
                    avg_delay_days=avg_delay
                )
            )

        summary = WarehouseDelaySummaryResponse(
            warehouses=items,
            total_delayed_orders=total_delayed,
            most_delayed_warehouse=most_delayed
        )

        return ToolResponse(
            success=True,
            action_type=ToolActionType.READ_ONLY,
            tool_name="get_warehouse_delay_summary",
            message=f"Retrieved delay statistics for {len(items)} warehouse(s). Total delayed orders: {total_delayed}.",
            data=summary.model_dump(),
            requires_human_approval=False
        )
    except Exception as e:
        return ToolResponse(
            success=False,
            action_type=ToolActionType.READ_ONLY,
            tool_name="get_warehouse_delay_summary",
            message=f"Failed to fetch warehouse delay summary: {str(e)}",
            data=None,
            requires_human_approval=False
        )
    finally:
        db.close()


def get_order_details(order_id: int, **kwargs) -> ToolResponse:
    """
    Read-only tool: Looks up full details for a single order by ID.
    Auto-executes without requiring human approval.
    """
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            return ToolResponse(
                success=False,
                action_type=ToolActionType.READ_ONLY,
                tool_name="get_order_details",
                message=f"Order {order_id} not found in database.",
                data=None,
                requires_human_approval=False
            )

        # Also fetch linked complaints and tickets
        complaints = db.query(Complaint).filter(Complaint.order_id == order_id).all()
        complaint_ids = [c.complaint_id for c in complaints]
        tickets = db.query(Ticket).filter(Ticket.complaint_id.in_(complaint_ids)).all() if complaint_ids else []

        payload = {
            "order": {
                "order_id": order.order_id,
                "customer_id": order.customer_id,
                "customer_name": order.customer_name,
                "product_name": order.product_name,
                "order_date": str(order.order_date),
                "expected_delivery_date": str(order.expected_delivery_date),
                "actual_delivery_date": str(order.actual_delivery_date) if order.actual_delivery_date else None,
                "status": order.status,
                "delay_days": order.delay_days or 0,
                "warehouse": order.warehouse,
                "is_delayed": (order.status == "Delayed" or (order.delay_days and order.delay_days > 0))
            },
            "linked_complaints": [
                {
                    "complaint_id": c.complaint_id,
                    "category": c.category,
                    "priority": c.priority,
                    "status": c.status,
                    "complaint_text": c.complaint_text
                }
                for c in complaints
            ],
            "linked_tickets": [
                {
                    "ticket_id": t.ticket_id,
                    "issue_type": t.issue_type,
                    "priority": t.priority,
                    "assigned_team": t.assigned_team,
                    "status": t.status
                }
                for t in tickets
            ]
        }

        return ToolResponse(
            success=True,
            action_type=ToolActionType.READ_ONLY,
            tool_name="get_order_details",
            message=f"Found Order {order_id} ({order.status}, warehouse: {order.warehouse}).",
            data=payload,
            requires_human_approval=False
        )
    except Exception as e:
        return ToolResponse(
            success=False,
            action_type=ToolActionType.READ_ONLY,
            tool_name="get_order_details",
            message=f"Error looking up order {order_id}: {str(e)}",
            data=None,
            requires_human_approval=False
        )
    finally:
        db.close()


def get_customer_complaints(
    customer_id: Optional[int] = None,
    order_id: Optional[int] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 5,
    **kwargs
) -> ToolResponse:
    """
    Read-only tool: Looks up customer complaints filtered by customer, order, category, or status.
    Auto-executes without requiring human approval.
    """
    db = SessionLocal()
    try:
        q = db.query(Complaint)
        if customer_id is not None:
            q = q.filter(Complaint.customer_id == customer_id)
        if order_id is not None:
            q = q.filter(Complaint.order_id == order_id)
        if category:
            q = q.filter(func.lower(Complaint.category) == category.lower())
        if status:
            q = q.filter(func.lower(Complaint.status) == status.lower())

        total_count = q.count()
        safe_limit = max(1, min(int(limit or 5), 10))
        results = q.order_by(Complaint.complaint_id.desc()).limit(safe_limit).all()

        complaints_data = [
            ComplaintItem(
                complaint_id=c.complaint_id,
                customer_id=c.customer_id,
                customer_name=c.customer_name,
                order_id=c.order_id,
                complaint_text=c.complaint_text,
                category=c.category,
                priority=c.priority,
                status=c.status,
                created_at=str(c.created_at)
            ).model_dump()
            for c in results
        ]

        return ToolResponse(
            success=True,
            action_type=ToolActionType.READ_ONLY,
            tool_name="get_customer_complaints",
            message=f"Retrieved {len(complaints_data)} of {total_count} matching complaint(s) (showing most recent {len(complaints_data)}).",
            data={"complaints": complaints_data, "total_count": total_count},
            requires_human_approval=False
        )
    except Exception as e:
        return ToolResponse(
            success=False,
            action_type=ToolActionType.READ_ONLY,
            tool_name="get_customer_complaints",
            message=f"Error retrieving complaints: {str(e)}",
            data=None,
            requires_human_approval=False
        )
    finally:
        db.close()


def get_ticket_details(
    ticket_id: Optional[int] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    assigned_team: Optional[str] = None,
    limit: int = 5,
    **kwargs
) -> ToolResponse:
    """
    Read-only tool: Looks up support tickets.
    Auto-executes without requiring human approval.
    """
    db = SessionLocal()
    try:
        q = db.query(Ticket)
        if ticket_id is not None:
            q = q.filter(Ticket.ticket_id == ticket_id)
        if priority:
            q = q.filter(func.lower(Ticket.priority) == priority.lower())
        if status:
            q = q.filter(func.lower(Ticket.status) == status.lower())
        if assigned_team:
            q = q.filter(func.lower(Ticket.assigned_team).contains(assigned_team.lower()))

        total_count = q.count()
        safe_limit = max(1, min(int(limit or 5), 10))
        results = q.order_by(Ticket.ticket_id.desc()).limit(safe_limit).all()

        tickets_data = [
            TicketItem(
                ticket_id=t.ticket_id,
                complaint_id=t.complaint_id,
                issue_type=t.issue_type,
                priority=t.priority,
                assigned_team=t.assigned_team,
                status=t.status,
                created_at=str(t.created_at),
                resolved_at=str(t.resolved_at) if t.resolved_at else None
            ).model_dump()
            for t in results
        ]

        return ToolResponse(
            success=True,
            action_type=ToolActionType.READ_ONLY,
            tool_name="get_ticket_details",
            message=f"Retrieved {len(tickets_data)} of {total_count} matching ticket(s) (showing most recent {len(tickets_data)}).",
            data={"tickets": tickets_data, "total_count": total_count},
            requires_human_approval=False
        )
    except Exception as e:
        return ToolResponse(
            success=False,
            action_type=ToolActionType.READ_ONLY,
            tool_name="get_ticket_details",
            message=f"Error retrieving ticket details: {str(e)}",
            data=None,
            requires_human_approval=False
        )
    finally:
        db.close()


def lookup_policy(
    query: str,
    category: Optional[str] = None,
    top_k: int = 3,
    **kwargs
) -> ToolResponse:
    """
    Read-only tool: Retrieves authoritative business policy chunks from the ChromaDB vector store.
    Auto-executes without requiring human approval.
    """
    try:
        vs = _get_vector_store()
        search_query = query
        if category:
            search_query = f"{category}: {query}"

        docs = vs.similarity_search(search_query, k=top_k)
        chunks: List[PolicyChunk] = []
        for doc in docs:
            source = doc.metadata.get("source", "knowledge_base") if hasattr(doc, "metadata") else "knowledge_base"
            chunks.append(
                PolicyChunk(
                    content=doc.page_content.strip(),
                    source=source
                )
            )

        resp = PolicyQueryResponse(
            query=query,
            chunks=chunks,
            summary_hint=f"Found {len(chunks)} relevant policy excerpt(s)."
        )

        return ToolResponse(
            success=True,
            action_type=ToolActionType.READ_ONLY,
            tool_name="lookup_policy",
            message=f"Retrieved {len(chunks)} policy reference(s) for query: '{query}'.",
            data=resp.model_dump(),
            requires_human_approval=False
        )
    except Exception as e:
        return ToolResponse(
            success=False,
            action_type=ToolActionType.READ_ONLY,
            tool_name="lookup_policy",
            message=f"Failed to lookup policy in vector store: {str(e)}",
            data=None,
            requires_human_approval=False
        )

