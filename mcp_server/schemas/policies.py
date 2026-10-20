from typing import List, Optional
from pydantic import BaseModel, Field


class PolicyQueryInput(BaseModel):
    query: str = Field(min_length=3, description="Natural language policy question or keyword search (e.g. 'refund policy for delays over 5 days')")
    category: Optional[str] = Field(
        default=None,
        description="Policy domain to filter or prioritize (e.g. 'refund', 'delivery_sla', 'escalation', 'catalog')"
    )
    top_k: int = Field(default=3, ge=1, le=10, description="Number of authoritative policy chunks to return")


class PolicyChunk(BaseModel):
    content: str = Field(description="Policy excerpt text")
    source: str = Field(description="Document source name or file path")
    relevance_score: Optional[float] = Field(default=None, description="Similarity score")


class PolicyQueryResponse(BaseModel):
    query: str
    chunks: List[PolicyChunk]
    summary_hint: Optional[str] = None

