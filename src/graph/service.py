import uuid
from typing import Any
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from src.state import get_empty_constraints
from src.graph.builder import get_compiled_graph

_compiled_graph = None


def get_graph():
    """Singleton getter for the compiled travel graph."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = get_compiled_graph()
    return _compiled_graph


def extract_interrupt_payload(result: dict[str, Any]) -> dict[str, Any] | None:
    """Extract interrupt details if the graph execution paused at an interrupt()."""
    interrupts = result.get("__interrupt__", [])
    if not interrupts:
        return None

    first_interrupt = interrupts[0]
    payload = getattr(first_interrupt, "value", first_interrupt)
    return payload if isinstance(payload, dict) else {"value": payload}


def serialize_result(result: dict[str, Any], thread_id: str) -> dict[str, Any]:
    """Serialize the graph execution state into a clean dictionary for frontend/API."""
    messages = result.get("messages", [])
    last_message = messages[-1].content if messages else ""
    answer = result.get("final_response") or last_message
    interrupt_payload = extract_interrupt_payload(result)

    if interrupt_payload:
        answer = interrupt_payload.get("draft_itinerary") or result.get("itinerary", "")

    return {
        "thread_id": thread_id,
        "answer": answer,
        "requires_approval": interrupt_payload is not None,
        "approval_request": (
            interrupt_payload.get("approval_request", "")
            if interrupt_payload
            else result.get("approval_request", "")
        ),
        "flight_results": result.get("flight_results", ""),
        "hotel_results": result.get("hotel_results", ""),
        "weather_results": result.get("weather_results", ""),
        "budget_results": result.get("budget_results", ""),
        "itinerary": (
            interrupt_payload.get("draft_itinerary", "")
            if interrupt_payload
            else result.get("itinerary", "")
        ),
        "selected_agents": result.get("selected_agents", []),
        "trip_constraints": result.get("trip_constraints", {}),
        "supervisor_reasoning": result.get("supervisor_reasoning", ""),
        "guardrail_allowed": result.get("guardrail_allowed", True),
        "guardrail_reason": result.get("guardrail_reason", ""),
        "approved": result.get("approved"),
        "human_feedback": result.get("human_feedback", ""),
        "llm_calls": result.get("llm_calls", 0),
    }


def run_travel_agent(user_input: str, thread_id: str | None = None) -> dict[str, Any]:
    """
    Start a new travel-planning run with the user prompt.
    Executes through supervisor and specialists, pausing at the HITL approval step.
    """
    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {"configurable": {"thread_id": thread_id}}
    graph = get_graph()

    result = graph.invoke(
        {
            "messages": [HumanMessage(content=user_input)],
            "user_query": user_input,
            "guardrail_allowed": True,
            "guardrail_reason": "",
            "selected_agents": [],
            "trip_constraints": get_empty_constraints(),
            "supervisor_reasoning": "",
            "flight_results": "",
            "hotel_results": "",
            "weather_results": "",
            "budget_results": "",
            "itinerary": "",
            "approval_request": "",
            "approved": False,
            "human_feedback": "",
            "final_response": "",
            "llm_calls": 0,
        },
        config=config,
    )

    return serialize_result(result, thread_id)


def resume_travel_agent(
    thread_id: str,
    approved: bool,
    feedback: str = "",
) -> dict[str, Any]:
    """
    Resume a suspended travel-planning thread after human approval or revision review.
    Executes through final_agent to generate the polished response.
    """
    if not thread_id:
        raise ValueError("thread_id is required to resume a travel plan.")

    config = {"configurable": {"thread_id": thread_id}}
    graph = get_graph()

    result = graph.invoke(
        Command(
            resume={
                "approved": approved,
                "feedback": feedback.strip(),
            }
        ),
        config=config,
    )

    return serialize_result(result, thread_id)
