from typing import Any, Dict, List, Literal, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.graph.workflow import graph, resume_agent

router = APIRouter(prefix="/approvals", tags=["Human-in-the-Loop Approvals"])


class ApprovalDecisionRequest(BaseModel):
    thread_id: str = Field(description="Identifier of the paused conversation thread")
    decision: Literal["approved", "rejected"] = Field(description="Decision applied to the pending write operation")
    approved_by: str = Field(default="Operations Supervisor", description="Name/ID of the reviewing authority")
    notes: Optional[str] = Field(default="", description="Audit comments or justification for decision")


class ApprovalDecisionResponse(BaseModel):
    status: str
    thread_id: str
    decision_applied: str
    response: str
    audit_log: List[Dict[str, Any]] = []


@router.get("/pending")
async def list_pending_approvals():
    """
    Returns diagnostic information on whether the system is operational
    and ready to process approvals.
    """
    return {
        "status": "ready",
        "message": "Send approval decisions to POST /api/v1/approvals/resume with thread_id and decision."
    }


@router.post("/resume", response_model=ApprovalDecisionResponse)
async def submit_approval_decision(req: ApprovalDecisionRequest):
    """
    Resumes a paused operations workflow with an approval or rejection.
    If approved, executes the write tool on the database.
    If rejected, cancels the action and prompts the agent to respond accordingly.
    """
    result = resume_agent(
        thread_id=req.thread_id,
        decision=req.decision,
        approved_by=req.approved_by,
        notes=req.notes
    )

    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))

    return ApprovalDecisionResponse(
        status=result["status"],
        thread_id=result["thread_id"],
        decision_applied=result.get("decision_applied", req.decision),
        response=result.get("response", ""),
        audit_log=result.get("audit_log", [])
    )

