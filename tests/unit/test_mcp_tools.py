import pytest
from mcp_server.schemas.common import ToolActionType, ToolResponse
from mcp_server.tools.read_tools import (
    get_warehouse_delay_summary,
    get_order_details,
    get_customer_complaints,
    get_ticket_details,
    lookup_policy
)
from mcp_server.tools.write_tools import (
    issue_refund,
    escalate_ticket,
    update_order_status
)
from mcp_server.client import mcp_client


def test_warehouse_delay_summary_read_only():
    """Verify read-only warehouse summary runs and does not require approval."""
    resp = get_warehouse_delay_summary()
    assert isinstance(resp, ToolResponse)
    assert resp.success is True
    assert resp.action_type == ToolActionType.READ_ONLY
    assert resp.requires_human_approval is False
    assert "warehouses" in resp.data


def test_order_details_lookup():
    """Verify looking up order details returns structured payload."""
    resp = get_order_details(order_id=1)
    assert isinstance(resp, ToolResponse)
    assert resp.action_type == ToolActionType.READ_ONLY
    assert resp.requires_human_approval is False
    if resp.success:
        assert "order" in resp.data
        assert resp.data["order"]["order_id"] == 1


def test_issue_refund_requires_approval_by_default():
    """Verify write tool issue_refund requires human confirmation when approved_by is missing."""
    resp = issue_refund(
        order_id=1,
        reason="Customer requested refund due to delivery delay exceeding 7 days"
    )
    assert isinstance(resp, ToolResponse)
    assert resp.action_type == ToolActionType.WRITE_APPROVAL_REQUIRED
    assert resp.requires_human_approval is True
    assert "ACTION REQUIRED" in resp.message
    assert resp.audit_trail is not None


def test_escalate_ticket_requires_approval():
    """Verify escalate_ticket halts for human approval before mutating DB."""
    resp = escalate_ticket(
        ticket_id=1,
        escalation_reason="Repeated customer escalations without resolution by Tier 1",
        target_team="Tier 2 Senior Operations"
    )
    assert isinstance(resp, ToolResponse)
    assert resp.action_type == ToolActionType.WRITE_APPROVAL_REQUIRED
    assert resp.requires_human_approval is True
    assert "Proposed escalation" in resp.message


def test_mcp_client_tool_discovery():
    """Verify MCPClient exposes all 8 tools as LangChain StructuredTools."""
    tools = mcp_client.get_langchain_tools()
    tool_names = [t.name for t in tools]

    expected = [
        "get_warehouse_delay_summary",
        "get_order_details",
        "get_customer_complaints",
        "get_ticket_details",
        "lookup_policy",
        "issue_refund",
        "escalate_ticket",
        "update_order_status"
    ]

    for exp in expected:
        assert exp in tool_names, f"Tool {exp} missing from MCPClient tools"

    assert mcp_client.is_approval_required("issue_refund") is True
    assert mcp_client.is_approval_required("escalate_ticket") is True
    assert mcp_client.is_approval_required("get_warehouse_delay_summary") is False

