from pydantic import BaseModel,Field
from typing import Dict, Any


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        description="Natural language query for the agent"
    )


class QueryResponse(BaseModel):
    workflow_type: str
    analysis: Dict[str, Any]
    report: str