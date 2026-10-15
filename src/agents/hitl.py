from langgraph.types import interrupt
from langchain_core.messages import AIMessage
from src.state import TravelState


def human_approval_agent(state: TravelState) -> dict:
    """
    Human-in-the-Loop (HITL) Approval Agent:
    Pauses graph execution using LangGraph's interrupt() mechanism.
    Awaits client response (approval or revision request) before proceeding.
    NOTE: Do NOT wrap interrupt() in try/except, as LangGraph uses it for flow suspension.
    """
    review = interrupt(
        {
            "question": "Do you approve this itinerary?",
            "draft_itinerary": state.get("itinerary", ""),
            "approval_request": state.get("approval_request", ""),
            "selected_agents": state.get("selected_agents", []),
            "supervisor_reasoning": state.get("supervisor_reasoning", ""),
            "expected_response": {
                "approved": True,
                "feedback": "Optional revision feedback",
            },
        }
    )

    approved = bool(review.get("approved", False))
    human_feedback = str(review.get("feedback", "")).strip()

    return {
        "approved": approved,
        "human_feedback": human_feedback,
        "messages": [AIMessage(content="Human approval step completed.")],
    }
