import asyncio
from typing import Any, Dict, List, Optional
from mcp.server.mcpserver import MCPServer
from mcp_server.schemas.common import ToolActionType, ToolResponse
from mcp_server.tools.read_tools import (
    get_warehouse_delay_summary,
    get_order_details,
    get_customer_complaints,
    get_ticket_details,
    lookup_policy,
)
from mcp_server.tools.write_tools import (
    issue_refund,
    escalate_ticket,
    update_order_status,
)


# Initialize FastMCP Server instance
server = MCPServer("ecommerce-operations-tools")


# ==============================================================================
# TOOL REGISTRATIONS (Official MCP SDK @server.tool)
# ==============================================================================

@server.tool()
def mcp_get_warehouse_delay_summary(
    warehouse: Optional[str] = None,
    min_delay_days: int = 1
) -> Dict[str, Any]:
    """
    [READ-ONLY / AUTO-EXECUTE]
    Fetches aggregate delivery delay metrics and warehouse performance statistics.
    """
    response = get_warehouse_delay_summary(warehouse=warehouse, min_delay_days=min_delay_days)
    return response.model_dump()


@server.tool()
def mcp_get_order_details(order_id: int) -> Dict[str, Any]:
    """
    [READ-ONLY / AUTO-EXECUTE]
    Retrieves full order information, fulfillment status, delivery timeline, and linked complaints/tickets.
    """
    response = get_order_details(order_id=order_id)
    return response.model_dump()


@server.tool()
def mcp_get_customer_complaints(
    customer_id: Optional[int] = None,
    order_id: Optional[int] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """
    [READ-ONLY / AUTO-EXECUTE]
    Retrieves customer complaints filtered by customer, order, category, or status.
    """
    response = get_customer_complaints(
        customer_id=customer_id,
        order_id=order_id,
        category=category,
        status=status,
        limit=limit
    )
    return response.model_dump()


@server.tool()
def mcp_get_ticket_details(
    ticket_id: Optional[int] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    assigned_team: Optional[str] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """
    [READ-ONLY / AUTO-EXECUTE]
    Retrieves operations support tickets filtered by ID, priority, status, or assigned team.
    """
    response = get_ticket_details(
        ticket_id=ticket_id,
        priority=priority,
        status=status,
        assigned_team=assigned_team,
        limit=limit
    )
    return response.model_dump()


@server.tool()
def mcp_lookup_policy(
    query: str,
    category: Optional[str] = None,
    top_k: int = 3
) -> Dict[str, Any]:
    """
    [READ-ONLY / AUTO-EXECUTE]
    Performs semantic vector search across authoritative policy manuals (delivery SLAs, refund policies, escalation matrices).
    """
    response = lookup_policy(query=query, category=category, top_k=top_k)
    return response.model_dump()


@server.tool()
def mcp_issue_refund(
    order_id: int,
    reason: str,
    refund_amount: Optional[float] = None,
    customer_id: Optional[int] = None,
    approved_by: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    [RISKY WRITE / HUMAN APPROVAL REQUIRED]
    Proposes or executes an order refund for a customer.
    When proposed without approval, returns a structured approval request payload.
    """
    response = issue_refund(
        order_id=order_id,
        reason=reason,
        refund_amount=refund_amount,
        customer_id=customer_id,
        approved_by=approved_by,
        **kwargs
    )
    return response.model_dump()


@server.tool()
def mcp_escalate_ticket(
    ticket_id: int,
    escalation_reason: str,
    target_team: str = "Tier 2 Senior Operations",
    new_priority: str = "High",
    approved_by: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    [RISKY WRITE / HUMAN APPROVAL REQUIRED]
    Proposes or executes a priority escalation and reassignment for a support ticket.
    When proposed without approval, pauses for human approval.
    """
    response = escalate_ticket(
        ticket_id=ticket_id,
        escalation_reason=escalation_reason,
        target_team=target_team,
        new_priority=new_priority,
        approved_by=approved_by,
        **kwargs
    )
    return response.model_dump()


@server.tool()
def mcp_update_order_status(
    order_id: int,
    new_status: str,
    reason: str,
    approved_by: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    [RISKY WRITE / HUMAN APPROVAL REQUIRED]
    Proposes or updates an order delivery status (e.g. Delivered, Delayed, Cancelled).
    Pauses for human approval when unconfirmed.
    """
    response = update_order_status(
        order_id=order_id,
        new_status=new_status,
        reason=reason,
        approved_by=approved_by,
        **kwargs
    )
    return response.model_dump()


# ==============================================================================
# UNIFIED REGISTRY & EXECUTION INTERFACE
# ==============================================================================

TOOL_REGISTRY = {
    "get_warehouse_delay_summary": {
        "function": get_warehouse_delay_summary,
        "action_type": ToolActionType.READ_ONLY,
        "requires_approval": False,
        "description": "Get delay statistics and delayed order counts grouped by warehouse."
    },
    "get_order_details": {
        "function": get_order_details,
        "action_type": ToolActionType.READ_ONLY,
        "requires_approval": False,
        "description": "Get complete order information, delay days, and linked tickets."
    },
    "get_customer_complaints": {
        "function": get_customer_complaints,
        "action_type": ToolActionType.READ_ONLY,
        "requires_approval": False,
        "description": "Fetch customer complaints by customer, order, or category."
    },
    "get_ticket_details": {
        "function": get_ticket_details,
        "action_type": ToolActionType.READ_ONLY,
        "requires_approval": False,
        "description": "Fetch support ticket details and assignment."
    },
    "lookup_policy": {
        "function": lookup_policy,
        "action_type": ToolActionType.READ_ONLY,
        "requires_approval": False,
        "description": "Vector semantic search across SLA, refund, and escalation documents."
    },
    "issue_refund": {
        "function": issue_refund,
        "action_type": ToolActionType.WRITE_APPROVAL_REQUIRED,
        "requires_approval": True,
        "description": "Issue or propose a customer refund (Requires Human Approval)."
    },
    "escalate_ticket": {
        "function": escalate_ticket,
        "action_type": ToolActionType.WRITE_APPROVAL_REQUIRED,
        "requires_approval": True,
        "description": "Escalate support ticket to Tier 2 (Requires Human Approval)."
    },
    "update_order_status": {
        "function": update_order_status,
        "action_type": ToolActionType.WRITE_APPROVAL_REQUIRED,
        "requires_approval": True,
        "description": "Modify order delivery status (Requires Human Approval)."
    }
}


def list_operations_tools() -> List[Dict[str, Any]]:
    """Returns a list of all registered tools with metadata."""
    return [
        {
            "name": name,
            "description": meta["description"],
            "action_type": meta["action_type"].value,
            "requires_human_approval": meta["requires_approval"]
        }
        for name, meta in TOOL_REGISTRY.items()
    ]


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> ToolResponse:
    """Executes a registered tool by name with arguments dictionary."""
    if tool_name not in TOOL_REGISTRY:
        return ToolResponse(
            success=False,
            action_type=ToolActionType.READ_ONLY,
            tool_name=tool_name,
            message=f"Tool '{tool_name}' is not registered on this MCP server.",
            data=None,
            requires_human_approval=False
        )

    tool_entry = TOOL_REGISTRY[tool_name]
    func = tool_entry["function"]
    return func(**arguments)


if __name__ == "__main__":
    print(f"Starting FastMCP Server '{server.name}' with {len(TOOL_REGISTRY)} tools...")
    asyncio.run(server.run_stdio_async())

