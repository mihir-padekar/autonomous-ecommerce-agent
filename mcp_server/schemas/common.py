from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolActionType(str, Enum):
    """
    Classifies tool actions for execution safety.
    READ_ONLY actions execute autonomously without pause.
    WRITE_APPROVAL_REQUIRED actions must pause for Human-in-the-Loop review.
    """
    READ_ONLY = "read_only"
    WRITE_APPROVAL_REQUIRED = "write_approval_required"


class RiskLevel(str, Enum):
    """
    Risk classification for agent operations.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ToolResponse(BaseModel):
    """
    Standardized response envelope returned by all MCP tools.
    """
    success: bool = Field(description="Whether the tool execution succeeded")
    action_type: ToolActionType = Field(description="Action safety classification")
    tool_name: str = Field(description="Name of the executed tool")
    message: str = Field(description="Human-readable summary of the tool outcome")
    data: Optional[Any] = Field(default=None, description="Structured payload resulting from tool execution")
    requires_human_approval: bool = Field(default=False, description="Flag indicating if action requires HITL approval")
    audit_trail: Optional[Dict[str, Any]] = Field(default=None, description="Metadata for compliance audit logs")

