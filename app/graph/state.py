from typing import Annotated, Any, Dict, List, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    LangGraph execution state for the Operations Copilot.
    """
    # Chat message history maintained via add_messages reducer
    messages: Annotated[List[BaseMessage], add_messages]

    # Unique thread identifier for conversation persistence & checkpointing
    thread_id: str

    # Structured details of any pending write operation awaiting approval
    pending_approval: Optional[Dict[str, Any]]

    # Approval resolution status: None | "pending" | "approved" | "rejected"
    approval_status: Optional[str]

    # Recorded audit log events during graph execution
    audit_log: List[Dict[str, Any]]

