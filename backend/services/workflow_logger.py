from datetime import datetime

from backend.database.db import SessionLocal

from backend.database.models import (
    WorkflowExecution,
    WorkflowLog
)

def create_execution(
    workflow_id,
    workflow_name,
    query
):

    db = SessionLocal()

    try:

        execution = WorkflowExecution(

            workflow_id=workflow_id,

            workflow_name=workflow_name,

            user_query=query,

            status="RUNNING",

            started_at=datetime.utcnow()
        )

        db.add(execution)

        db.commit()

    finally:

        db.close()

def complete_execution(
    workflow_id,
    status="COMPLETED"
):

    db = SessionLocal()

    try:

        execution = db.query(
            WorkflowExecution
        ).filter(
            WorkflowExecution.workflow_id == workflow_id
        ).first()

        if execution:

            execution.status = status

            execution.completed_at = datetime.utcnow()

            execution.duration_seconds = (

                execution.completed_at
                - execution.started_at

            ).total_seconds()

            db.commit()

    finally:

        db.close()

def log_agent_step(

    workflow_id,

    query,

    agent_name,

    action,

    status,

    execution_time
):

    db = SessionLocal()

    try:

        log = WorkflowLog(

            workflow_id=workflow_id,

            user_query=query,

            agent_name=agent_name,

            action=action,

            status=status,

            execution_time=execution_time,

            timestamp=datetime.utcnow()
        )

        db.add(log)

        db.commit()

    finally:

        db.close()