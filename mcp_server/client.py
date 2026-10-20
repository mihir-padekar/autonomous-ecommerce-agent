from typing import Any, Callable, Dict, List, Optional
from langchain_core.tools import StructuredTool
from pydantic import BaseModel
from mcp_server.server import TOOL_REGISTRY, execute_tool, list_operations_tools
from mcp_server.schemas.common import ToolActionType, ToolResponse
from mcp_server.schemas.orders import (
    WarehouseDelayFilter,
    OrderLookupFilter,
    RefundOrderInput,
    UpdateOrderStatusInput,
)
from mcp_server.schemas.tickets import (
    TicketLookupFilter,
    ComplaintLookupFilter,
    EscalateTicketInput,
)
from mcp_server.schemas.policies import PolicyQueryInput


# Map of tool names to their Pydantic argument schemas
SCHEMA_MAP: Dict[str, type[BaseModel]] = {
    "get_warehouse_delay_summary": WarehouseDelayFilter,
    "get_order_details": OrderLookupFilter,
    "get_customer_complaints": ComplaintLookupFilter,
    "get_ticket_details": TicketLookupFilter,
    "lookup_policy": PolicyQueryInput,
    "issue_refund": RefundOrderInput,
    "escalate_ticket": EscalateTicketInput,
    "update_order_status": UpdateOrderStatusInput,
}


class MCPClient:
    """
    Client adapter connecting LangGraph agents to the FastMCP tool registry.
    Handles tool discovery, Pydantic argument validation, and safety interception.
    """

    def __init__(self, mode: str = "in_process"):
        self.mode = mode
        self.registry = TOOL_REGISTRY

    def list_tools(self) -> List[Dict[str, Any]]:
        """Returns metadata for all available MCP tools."""
        return list_operations_tools()

    def is_approval_required(self, tool_name: str) -> bool:
        """Checks if a tool is flagged as requiring Human-in-the-Loop confirmation."""
        meta = self.registry.get(tool_name)
        if not meta:
            return False
        return meta.get("requires_approval", False)

    def call_tool(self, tool_name: str, **kwargs) -> ToolResponse:
        """Executes a tool call and returns the standardized ToolResponse envelope."""
        return execute_tool(tool_name, kwargs)

    def get_langchain_tools(self) -> List[StructuredTool]:
        """
        Converts registered MCP tools into standard LangChain StructuredTools
        compatible with LangGraph ReAct agents and LLM tool binding.
        """
        langchain_tools: List[StructuredTool] = []

        for name, meta in self.registry.items():
            func = meta["function"]
            desc = meta["description"]
            schema = SCHEMA_MAP.get(name)

            def make_wrapper(tool_name: str) -> Callable[..., Dict[str, Any]]:
                def wrapper(**kwargs) -> Dict[str, Any]:
                    resp = execute_tool(tool_name, kwargs)
                    return resp.model_dump()
                wrapper.__name__ = tool_name
                wrapper.__doc__ = desc
                return wrapper

            tool_instance = StructuredTool.from_function(
                func=make_wrapper(name),
                name=name,
                description=desc,
                args_schema=schema
            )
            langchain_tools.append(tool_instance)

        return langchain_tools


# Default singleton client instance
mcp_client = MCPClient()

