from fastapi import APIRouter
from sqlalchemy import text
from app.database.session import SessionLocal

router = APIRouter(tags=["Health & Diagnostics"])


@router.get("/health")
async def health_check():
    """
    Liveness and database connectivity probe.
    """
    db_status = "unknown"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "Autonomous E-Commerce Operations Copilot",
        "database": db_status
    }

