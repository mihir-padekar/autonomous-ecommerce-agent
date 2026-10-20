from datetime import datetime, timezone
from typing import Any, Dict, Optional
from app.database.session import SessionLocal
from app.database.models import Order, Ticket, Complaint, WorkflowLog
from mcp_server.schemas.common import ToolActionType, ToolResponse
from mcp_server.schemas.orders import RefundOrderInput, UpdateOrderStatusInput
from mcp_server.schemas.tickets import EscalateTicketInput


def issue_refund(
    order_id: int,
    reason: str,
    refund_amount: Optional[float] = None,
    customer_id: Optional[int] = None,
    approved_by: Optional[str] = None,
    **kwargs
) -> ToolResponse:
    """
    Risky write tool: Initiates or executes an order refund.
    PAUSES FOR HUMAN APPROVAL: Requires supervisor confirmation before funds are disbursed.
    """
    # Validate via Pydantic model
    validated = RefundOrderInput(
        order_id=order_id,
        reason=reason,
        refund_amount=refund_amount,
        customer_id=customer_id
    )

    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.order_id == validated.order_id).first()
        if not order:
            return ToolResponse(
                success=False,
                action_type=ToolActionType.WRITE_APPROVAL_REQUIRED,
                tool_name="issue_refund",
                message=f"Order {validated.order_id} not found. Cannot issue refund.",
                data=None,
                requires_human_approval=True
            )

        # Audit payload
        audit_data = {
            "order_id": order.order_id,
            "customer_name": order.customer_name,
            "customer_id": order.customer_id,
            "product_name": order.product_name,
            "order_status": order.status,
            "delay_days": order.delay_days,
            "refund_amount": validated.refund_amount or "Full Order Value",
            "justification": validated.reason,
            "approved_by": approved_by or "Pending Supervisor Approval",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # If approval has not been granted by a human yet
        if not approved_by:
            return ToolResponse(
                success=True,
                action_type=ToolActionType.WRITE_APPROVAL_REQUIRED,
                tool_name="issue_refund",
                message=(
                    f"ACTION REQUIRED: Proposed refund for Order {order.order_id} ({order.product_name}) "
                    f"to customer '{order.customer_name}'. Reason: '{validated.reason}'. "
                    f"Amount: {validated.refund_amount or 'Full'}. Execution paused for human approval."
                ),
                data=audit_data,
                requires_human_approval=True,
                audit_trail=audit_data
            )

        # Execute refund and log to audit trail
        log_entry = WorkflowLog(
            workflow_id=f"refund-order-{order.order_id}-{int(datetime.now(timezone.utc).timestamp())}",
            user_query=validated.reason,
            agent_name="MCP_WriteTools_RefundAgent",
            action=f"Refund issued for Order #{order.order_id} (Approved by: {approved_by}). Reason: {validated.reason}",
            status="Success",
            execution_time=0.1,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(log_entry)
        db.commit()

        audit_data["execution_status"] = "COMPLETED"
        audit_data["log_id"] = log_entry.log_id

        return ToolResponse(
            success=True,
            action_type=ToolActionType.WRITE_APPROVAL_REQUIRED,
            tool_name="issue_refund",
            message=f"Refund successfully executed and recorded for Order {order.order_id}. Approved by: {approved_by}.",
            data=audit_data,
            requires_human_approval=False,
            audit_trail=audit_data
        )
    except Exception as e:
        db.rollback()
        return ToolResponse(
            success=False,
            action_type=ToolActionType.WRITE_APPROVAL_REQUIRED,
            tool_name="issue_refund",
            message=f"Error executing refund for order {order_id}: {str(e)}",
            data=None,
            requires_human_approval=True
        )
    finally:
        db.close()


def escalate_ticket(
    ticket_id: int,
    escalation_reason: str,
    target_team: str = "Tier 2 Senior Operations",
    new_priority: str = "High",
    approved_by: Optional[str] = None,
    **kwargs
) -> ToolResponse:
    """
    Risky write tool: Escalates a support ticket to Tier 2 or designated senior team.
    PAUSES FOR HUMAN APPROVAL: Reallocates support priority and reassignment.
    """
    # Validate via Pydantic model
    validated = EscalateTicketInput(
        ticket_id=ticket_id,
        escalation_reason=escalation_reason,
        target_team=target_team,
        new_priority=new_priority
    )

    db = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.ticket_id == validated.ticket_id).first()
        if not ticket:
            return ToolResponse(
                success=False,
                action_type=ToolActionType.WRITE_APPROVAL_REQUIRED,
                tool_name="escalate_ticket",
                message=f"Ticket {validated.ticket_id} not found.",
                data=None,
                requires_human_approval=True
            )

        audit_data = {
            "ticket_id": ticket.ticket_id,
            "previous_team": ticket.assigned_team,
            "target_team": validated.target_team,
            "previous_priority": ticket.priority,
            "new_priority": validated.new_priority,
            "escalation_reason": validated.escalation_reason,
            "approved_by": approved_by or "Pending Supervisor Approval",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        if not approved_by:
            return ToolResponse(
                success=True,
                action_type=ToolActionType.WRITE_APPROVAL_REQUIRED,
                tool_name="escalate_ticket",
                message=(
                    f"ACTION REQUIRED: Proposed escalation of Ticket #{ticket.ticket_id} from '{ticket.assigned_team}' "
                    f"to '{validated.target_team}' (Priority: {validated.new_priority}). Reason: '{validated.escalation_reason}'. "
                    f"Execution paused for human approval."
                ),
                data=audit_data,
                requires_human_approval=True,
                audit_trail=audit_data
            )

        # Mutate database record upon confirmed approval
        ticket.assigned_team = validated.target_team
        ticket.priority = validated.new_priority
        ticket.status = "In Progress"

        log_entry = WorkflowLog(
            workflow_id=f"escalate-ticket-{ticket.ticket_id}-{int(datetime.now(timezone.utc).timestamp())}",
            user_query=validated.escalation_reason,
            agent_name="MCP_WriteTools_EscalationAgent",
            action=f"Ticket #{ticket.ticket_id} escalated to {validated.target_team} (Approved by: {approved_by})",
            status="Success",
            execution_time=0.08,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(log_entry)
        db.commit()

        audit_data["execution_status"] = "COMPLETED"
        audit_data["log_id"] = log_entry.log_id

        return ToolResponse(
            success=True,
            action_type=ToolActionType.WRITE_APPROVAL_REQUIRED,
            tool_name="escalate_ticket",
            message=f"Ticket #{ticket.ticket_id} successfully escalated to {validated.target_team} (Priority: {validated.new_priority}).",
            data=audit_data,
            requires_human_approval=False,
            audit_trail=audit_data
        )
    except Exception as e:
        db.rollback()
        return ToolResponse(
            success=False,
            action_type=ToolActionType.WRITE_APPROVAL_REQUIRED,
            tool_name="escalate_ticket",
            message=f"Error escalating ticket {ticket_id}: {str(e)}",
            data=None,
            requires_human_approval=True
        )
    finally:
        db.close()


def update_order_status(
    order_id: int,
    new_status: str,
    reason: str,
    approved_by: Optional[str] = None,
    **kwargs
) -> ToolResponse:
    """
    Risky write tool: Modifies an order fulfillment status (e.g. In Transit, Delivered, Cancelled).
    PAUSES FOR HUMAN APPROVAL: Order state transition requires operational review.
    """
    validated = UpdateOrderStatusInput(
        order_id=order_id,
        new_status=new_status,
        reason=reason
    )

    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.order_id == validated.order_id).first()
        if not order:
            return ToolResponse(
                success=False,
                action_type=ToolActionType.WRITE_APPROVAL_REQUIRED,
                tool_name="update_order_status",
                message=f"Order {validated.order_id} not found.",
                data=None,
                requires_human_approval=True
            )

        audit_data = {
            "order_id": order.order_id,
            "previous_status": order.status,
            "new_status": validated.new_status,
            "reason": validated.reason,
            "approved_by": approved_by or "Pending Supervisor Approval",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        if not approved_by:
            return ToolResponse(
                success=True,
                action_type=ToolActionType.WRITE_APPROVAL_REQUIRED,
                tool_name="update_order_status",
                message=(
                    f"ACTION REQUIRED: Proposed status change for Order #{order.order_id} from '{order.status}' "
                    f"to '{validated.new_status}'. Reason: '{validated.reason}'. Execution paused for human approval."
                ),
                data=audit_data,
                requires_human_approval=True,
                audit_trail=audit_data
            )

        order.status = validated.new_status
        if validated.new_status == "Delivered":
            order.actual_delivery_date = datetime.now(timezone.utc).date()

        log_entry = WorkflowLog(
            workflow_id=f"update-order-{order.order_id}-{int(datetime.now(timezone.utc).timestamp())}",
            user_query=validated.reason,
            agent_name="MCP_WriteTools_OrderAgent",
            action=f"Order #{order.order_id} status updated to {validated.new_status} (Approved by: {approved_by})",
            status="Success",
            execution_time=0.07,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(log_entry)
        db.commit()

        audit_data["execution_status"] = "COMPLETED"
        audit_data["log_id"] = log_entry.log_id

        return ToolResponse(
            success=True,
            action_type=ToolActionType.WRITE_APPROVAL_REQUIRED,
            tool_name="update_order_status",
            message=f"Order #{order.order_id} status changed to {validated.new_status}.",
            data=audit_data,
            requires_human_approval=False,
            audit_trail=audit_data
        )
    except Exception as e:
        db.rollback()
        return ToolResponse(
            success=False,
            action_type=ToolActionType.WRITE_APPROVAL_REQUIRED,
            tool_name="update_order_status",
            message=f"Error updating order status: {str(e)}",
            data=None,
            requires_human_approval=True
        )
    finally:
        db.close()
