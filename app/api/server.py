from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.agent import router as agent_router
from app.api.v1.approvals import router as approvals_router
from app.api.v1.health import router as health_router
from app.core.config import settings


def create_app() -> FastAPI:
    """
    Factory function initializing the production FastAPI application.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=(
            "Autonomous E-Commerce Operations Copilot powered by LangGraph, "
            "FastMCP tools, and Human-in-the-Loop safety controls."
        ),
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Cross-Origin Resource Sharing
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount v1 Routers
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(agent_router, prefix="/api/v1")
    app.include_router(approvals_router, prefix="/api/v1")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.server:app", host="0.0.0.0", port=8000, reload=True)

