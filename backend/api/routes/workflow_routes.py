from fastapi import APIRouter

from backend.database.db import SessionLocal

from backend.database.models import (
    WorkflowExecution,
    WorkflowLog
)

from backend.api.schemas.workflow_schemas import (
    WorkflowHistoryResponse,
    WorkflowLogResponse
)

router = APIRouter(
    prefix="/workflows",
    tags=["Workflow"]
)

@router.get(
    "/history",
    response_model=list[WorkflowHistoryResponse]
)
def get_workflow_history():

    db = SessionLocal()

    try:

        workflows = (

            db.query(
                WorkflowExecution
            )

            .order_by(
                WorkflowExecution.started_at.desc()
            )

            .all()
        )

        return workflows

    finally:

        db.close()

@router.get(
    "/{workflow_id}",
    response_model=list[WorkflowLogResponse]
)
def get_workflow_details(
    workflow_id: str
):

    db = SessionLocal()

    try:

        logs = (

            db.query(
                WorkflowLog
            )

            .filter(
                WorkflowLog.workflow_id
                == workflow_id
            )

            .order_by(
                WorkflowLog.timestamp.asc()
            )

            .all()
        )

        return logs

    finally:

        db.close()