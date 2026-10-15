import traceback
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from src.api.schemas import TravelRequest, ApprovalRequest, HealthResponse
from src.graph.service import run_travel_agent, resume_travel_agent

router = APIRouter(prefix="/api", tags=["Travel Planning"])


@router.post("/travel")
async def create_or_continue_plan(request_data: TravelRequest):
    """Start or continue a multi-agent travel planning workflow."""
    try:
        user_message = request_data.message.strip()
        if not user_message:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "error": "Message cannot be empty."},
            )

        result = run_travel_agent(
            user_input=user_message,
            thread_id=request_data.thread_id,
        )

        return JSONResponse(content={"success": True, **result})

    except Exception as exc:
        print("API Travel Error:", exc)
        traceback.print_exc()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": str(exc)},
        )


@router.post("/travel/approve")
async def review_and_approve_plan(request_data: ApprovalRequest):
    """Submit human review decision (approve or request changes with feedback)."""
    try:
        if not request_data.approved and not request_data.feedback.strip():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "error": "Please provide revision feedback when rejecting or requesting changes.",
                },
            )

        result = resume_travel_agent(
            thread_id=request_data.thread_id,
            approved=request_data.approved,
            feedback=request_data.feedback,
        )

        return JSONResponse(content={"success": True, **result})

    except Exception as exc:
        print("API Approval Error:", exc)
        traceback.print_exc()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": str(exc)},
        )


@router.get("/health", response_model=HealthResponse, tags=["Diagnostics"])
async def health_check():
    """Health check endpoint displaying system capability features."""
    return {
        "status": "ok",
        "message": "TripMate AI Multi-Agent Service is active",
        "features": [
            "supervisor_agent",
            "input_guardrail",
            "human_in_the_loop",
            "mcp_integrations",
            "postgres_persistence",
        ],
    }
