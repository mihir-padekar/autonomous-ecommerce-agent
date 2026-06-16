from pydantic import BaseModel


class DashboardReportResponse(BaseModel):

    workflow_type: str

    analysis: dict

    report: str