from fastapi import FastAPI

from backend.api.routes.dashboard_routes import router as dashboard_router
from backend.api.routes.agent_routes import router as agent_router
from backend.api.routes.workflow_routes import router as workflow_router
from backend.api.routes.report_routes import (
    router as report_router
)
from backend.api.routes.insight_routes import(router as insight_router)
app = FastAPI(
    title="Autonomous E-Commerce Agent API"
)

app.include_router(dashboard_router)
app.include_router(agent_router)
app.include_router(workflow_router)
app.include_router(report_router)
app.include_router(insight_router)