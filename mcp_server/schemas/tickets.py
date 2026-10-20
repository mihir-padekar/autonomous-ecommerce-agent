from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ComplaintLookupFilter(BaseModel):
    customer_id: Optional[int] = Field(default=None, description="Filter by customer ID")
    order_id: Optional[int] = Field(default=None, description="Filter by order ID")
    category: Optional[str] = Field(default=None, description="Complaint category, e.g. 'Delivery Delay'")
    status: Optional[str] = Field(default=None, description="Complaint status, e.g. 'Open', 'Resolved'")
    limit: int = Field(default=5, ge=1, le=15, description="Number of recent complaints to return (default 5, max 15)")


class ComplaintItem(BaseModel):
    complaint_id: int
    customer_id: int
    customer_name: str
    order_id: int
    complaint_text: str
    category: str
    priority: str
    status: str
    created_at: str


class TicketLookupFilter(BaseModel):
    ticket_id: Optional[int] = Field(default=None, description="Specific ticket ID to lookup")
    priority: Optional[str] = Field(default=None, description="Priority filter, e.g. 'Critical', 'High', 'Medium', 'Low'")
    status: Optional[str] = Field(default=None, description="Ticket status, e.g. 'Open', 'In Progress', 'Resolved'")
    assigned_team: Optional[str] = Field(default=None, description="Filter by assigned operations team")
    limit: int = Field(default=5, ge=1, le=15, description="Number of recent tickets to return (default 5, max 15)")


class TicketItem(BaseModel):
    ticket_id: int
    complaint_id: int
    issue_type: str
    priority: str
    assigned_team: str
    status: str
    created_at: str
    resolved_at: Optional[str] = None


class EscalateTicketInput(BaseModel):
    ticket_id: int = Field(description="Unique ID of the ticket to escalate")
    escalation_reason: str = Field(min_length=10, description="Justification explaining why tier 1 cannot resolve or why SLA is breached")
    target_team: str = Field(default="Tier 2 Senior Operations", description="Target team or escalation tier")
    new_priority: str = Field(default="Critical", description="Updated priority (e.g., 'High', 'Critical')")

    @field_validator("new_priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        valid_priorities = {"Low", "Medium", "High", "Critical"}
        if v.capitalize() not in valid_priorities:
            raise ValueError(f"Priority '{v}' invalid. Must be one of {valid_priorities}")
        return v.capitalize()

