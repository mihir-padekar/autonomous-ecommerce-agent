from typing import TypedDict


class WorkflowState(TypedDict):
    query: str
    workflow_type: str
    data: dict
    policy: str
    analysis: str
    action: str
    report: str