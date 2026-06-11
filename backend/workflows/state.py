from typing import TypedDict


class WorkflowState(TypedDict):
    query: str
    workflow_type: str
    query_function: str
    orders: list
    complaints: list
    tickets: list
    data: dict
    policy_source: str
    policy_page: int
    policy: str
    policy_chunks: list
    compliance_status: str
    compliance_reason: str
    compliance_score: int
    analysis: dict
    executive_summary: str
    report: str