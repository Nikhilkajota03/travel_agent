from typing import Any, TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage

# Registered specialist agents and execution ordering
KNOWN_AGENTS = {
    "flight_agent",
    "hotel_agent",
    "weather_agent",
    "budget_agent",
    "itinerary_agent",
}

AGENT_ORDER = [
    "flight_agent",
    "hotel_agent",
    "weather_agent",
    "budget_agent",
    "itinerary_agent",
]


class TravelState(TypedDict, total=False):
    """
    Shared central state across the entire multi-agent LangGraph workflow.
    """
    # Conversation messages
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str

    # Supervisor & Input Guardrail
    guardrail_allowed: bool
    guardrail_reason: str
    selected_agents: list[str]
    trip_constraints: dict[str, Any]
    supervisor_reasoning: str

    # Specialist Agent Results
    flight_results: str
    hotel_results: str
    weather_results: str
    budget_results: str
    itinerary: str

    # Human-in-the-Loop & Approval
    approval_request: str
    approved: bool
    human_feedback: str
    final_response: str

    # Execution telemetry
    llm_calls: int


def get_empty_constraints() -> dict[str, Any]:
    """Return default empty trip constraints dictionary."""
    return {
        "destination": "",
        "origin": "",
        "duration": "",
        "budget": "",
        "travel_style": "",
        "special_preferences": [],
    }
