from fastapi import FastAPI, HTTPException
from backend.api.schemas import (
    QueryRequest,
    QueryResponse
)
from fastapi.middleware.cors import CORSMiddleware
from backend.workflows.ecommerce_graph import graph


from fastapi import APIRouter

router = APIRouter()

@router.post(
    "/query",
    response_model=QueryResponse
)
def run_query(request: QueryRequest):

    try:

        result = graph.invoke(
            {
                "query": request.query
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

        return {
            "analysis": result.get("analysis"),
            "report": result.get("report"),
            "workflow_type": result.get("workflow_type")
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

        print(traceback.format_exc())

        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {str(e)}"
        )
    