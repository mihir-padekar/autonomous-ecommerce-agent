from fastapi import APIRouter

from backend.workflows.ecommerce_graph import graph

from backend.api.schemas.report_schemas import (
    DashboardReportResponse
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

@router.get(
    "/dashboard",
    response_model=DashboardReportResponse
)
def get_dashboard_report():

    result = graph.invoke(
        {
            "query": "Show executive dashboard"
        }
    )

    return {

        "workflow_type":
            result["workflow_type"],

        "analysis":
            result["analysis"],

        "report":
            result["report"]
    }