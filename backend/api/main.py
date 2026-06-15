from fastapi import FastAPI

from backend.api.routes.dashboard_routes import router as dashboard_router
from backend.api.routes.agent_routes import router as agent_router

app = FastAPI(
    title="Autonomous E-Commerce Agent API"
)

app.include_router(dashboard_router)
app.include_router(agent_router)