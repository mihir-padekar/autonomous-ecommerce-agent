import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.graph.workflow import run_agent

router = APIRouter(prefix="/agent", tags=["Operations Agent"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, description="Natural language user prompt")
    session_id: Optional[str] = Field(default=None, description="Optional conversation session or thread ID")


class ChatResponse(BaseModel):
    status: str = Field(description="'completed' or 'pending_approval'")
    thread_id: str
    requires_action: bool = False
    response: Optional[str] = None
    approval_request: Optional[Dict[str, Any]] = None
    audit_log: Optional[List[Dict[str, Any]]] = None


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(req: ChatRequest):
    """
    Executes an operations copilot turn.
    Automatically executes read-only tools or pauses when human approval is required.
    """
    thread_id = req.session_id or f"sess-{uuid.uuid4().hex[:10]}"
    try:
        result = run_agent(query=req.message, thread_id=thread_id)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

