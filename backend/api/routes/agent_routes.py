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
from backend.agents.intent_agent import intent_agent
from backend.agents.followup_agent import followup_agent
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
        print("HISTORY:")
        intent = intent_agent(
            request.query,
            history
        )

        print("INTENT:", intent)
        for item in history:
            print(item)
        if intent["intent"] == "greeting":

            response = (
                "Hello! I'm your E-Commerce Operations Assistant.\n\n"
                "I can help you with:\n"
                "• Delayed Orders\n"
                "• Complaints\n"
                "• Tickets\n"
                "• Executive Dashboard\n"
                "• Company Policies (Refund, SLA, Escalation)\n"
            )

            save_message(
                request.session_id,
                "assistant",
                response
            )

            return {
                "workflow_type": "greeting",
                "analysis": {},
                "report": "",
                "chat_response": response
            }

        if intent["intent"] == "thanks":

            response = "You're welcome! Let me know if you need anything else."

            save_message(
                request.session_id,
                "assistant",
                response
            )

            return {
                "workflow_type": "thanks",
                "analysis": {},
                "report": "",
                "chat_response": response
            }

        if intent["intent"] == "goodbye":

            response = "Goodbye! Have a great day."

            save_message(
                request.session_id,
                "assistant",
                response
            )

            return {
                "workflow_type": "goodbye",
                "analysis": {},
                "report": "",
                "chat_response": response
            }

        if intent["intent"] == "help":

            response = (
                "I can help with:\n\n"
                "• Analyze delayed orders\n"
                "• Analyze complaints\n"
                "• Analyze support tickets\n"
                "• Executive dashboard summaries\n"
                "• Refund policy\n"
                "• Return policy\n"
                "• SLA & escalation policies"
            )

            save_message(
                request.session_id,
                "assistant",
                response
            )

            return {
                "workflow_type": "help",
                "analysis": {},
                "report": "",
                "chat_response": response
            }
        # Execute workflow
        if intent["intent"] == "workflow":
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

        if intent["intent"] == "followup":

            response = followup_agent(
                request.query,
                history
            )

            save_message(
                request.session_id,
                "assistant",
                response
            )

            return {
                "workflow_type": "followup",
                "analysis": {},
                "report": "",
                "chat_response": response
            }

        if intent["intent"] == "unknown":

            response = (
                "Sorry, I couldn't understand your request or it isn't supported.\n\n"
                "I can help with:\n"
                "• Delayed Orders\n"
                "• Complaints\n"
                "• Support Tickets\n"
                "• Executive Dashboard\n"
                "• Warehouse Analysis\n"
                "• Product Analysis\n"
                "• Company Policies (Refund, SLA, Escalation)\n\n"
                "Please ask a question related to e-commerce operations."
            )

            save_message(
                request.session_id,
                "assistant",
                response
            )

            return {
                "workflow_type": "unknown",
                "analysis": {},
                "report": "",
                "chat_response": response
            }
        if result.get("workflow_type") == "unknown":

            response = (
                "I'm an E-Commerce Operations Assistant.\n\n"
                "I can help you with:\n"
                "• Delayed Orders\n"
                "• Complaints\n"
                "• Support Tickets\n"
                "• Executive Dashboard\n"
                "• Warehouse Analysis\n"
                "• Product Analysis\n"
                "• Company Policies (Refund, SLA, Escalation)\n\n"
                "Please ask a question related to these topics."
            )

            save_message(
                request.session_id,
                "assistant",
                response
            )

            return {
                "workflow_type": "unknown",
                "analysis": {},
                "report": "",
                "chat_response": response
            }

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
        print("=" * 50)
        print(result)
        print("=" * 50)
        return {

            "analysis":
                result.get("analysis") or {},

            "report":
                result.get("report", ""),

            "workflow_type":
                result.get("workflow_type"),

            "chat_response":
                result.get("chat_response","")
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