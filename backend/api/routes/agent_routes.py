from fastapi import FastAPI, HTTPException
from backend.api.schemas.query_schemas import (
    QueryRequest,
    QueryResponse
)
from fastapi.middleware.cors import CORSMiddleware
from backend.workflows.ecommerce_graph import graph
from backend.api.schemas.agent_schemas import (
    AgentStatusResponse
)
from backend.services.chat_history_service import (
    save_message,
    get_conversation_history
)

from fastapi import APIRouter

router = APIRouter(
    prefix="/agents",
    tags=["Agents"]
)

@router.post(
    "/query",
    response_model=QueryResponse
)
def run_query(request: QueryRequest):

    try:

        # Save user message

        save_message(

            session_id=request.session_id,

            role="user",

            message=request.query
        )

        # Load conversation history

        history = get_conversation_history(
            request.session_id
        )

        # Execute workflow

        result = graph.invoke(
            {

                "session_id":
                    request.session_id,

                "query":
                    request.query,

                "history":
                    history
            }
        )

        if result.get("workflow_type") == "unknown":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Unsupported query. "
                    "Try: Show delayed orders, "
                    "Show executive dashboard, "
                    "Show warehouse delays, "
                    "Show top delayed products, "
                    "Show open tickets."
                )
            )

        # Save assistant response

        assistant_message = result.get(
            "chat_response",
            result.get("executive_summary", "")
        )

        save_message(
            session_id=request.session_id,
            role="assistant",
            message=result["chat_response"]
        )

        return {

            "analysis":
                result.get("analysis"),

            "report":
                result.get("report"),

            "workflow_type":
                result.get("workflow_type"),

            "chat_response":
                result.get("chat_response")
        }

    except HTTPException:
        raise

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {str(e)}"
        )
     
@router.get(
    "/status",
    response_model=list[AgentStatusResponse]
)
def get_agent_status():

    return [

        {
            "name": "Planner Agent",
            "status": "Healthy"
        },

        {
            "name": "Database Agent",
            "status": "Healthy"
        },

        {
            "name": "Analysis Agent",
            "status": "Healthy"
        },

        {
            "name": "Policy Agent",
            "status": "Healthy"
        },

        {
            "name": "Compliance Agent",
            "status": "Healthy"
        },

        {
            "name": "Executive Summary Agent",
            "status": "Healthy"
        },

        {
            "name": "Report Agent",
            "status": "Healthy"
        }
    ]