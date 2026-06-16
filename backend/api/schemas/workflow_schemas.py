from pydantic import BaseModel
from datetime import datetime


class WorkflowHistoryResponse(BaseModel):

    workflow_id: str
    workflow_name: str
    user_query: str

    status: str

    started_at: datetime

    completed_at: datetime | None

    duration_seconds: float | None

    class Config:
        from_attributes = True


class WorkflowLogResponse(BaseModel):

    agent_name: str

    action: str

    status: str

    execution_time: float

    timestamp: datetime

    class Config:
        from_attributes = True