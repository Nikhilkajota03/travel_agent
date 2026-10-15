"""
Trip Planner Backend Facade for Backward Compatibility.

This module re-exports the modular components from the `src` package, preserving
full backward compatibility with existing tests, scripts, and endpoints.
"""
from src.state import TravelState, KNOWN_AGENTS, AGENT_ORDER, get_empty_constraints as _empty_constraints
from src.core.llm import get_llm, llm_text as _llm_text, json_from_llm as _json_from_llm
from src.core.database import get_database_url, get_checkpointer
from src.agents import (
    supervisor_agent,
    guardrail_blocked_agent,
    flight_agent,
    hotel_agent,
    weather_agent,
    budget_agent,
    itinerary_agent,
    human_approval_agent,
    final_agent,
)
from src.graph.routing import (
    ROUTE_MAP,
    route_from_supervisor,
    route_after_agent,
    _selected_agents,
)
from src.graph.builder import create_travel_graph, get_compiled_graph
from src.graph.service import (
    run_travel_agent,
    resume_travel_agent,
    serialize_result as _serialize_result,
    extract_interrupt_payload as _interrupt_payload,
    get_graph,
)

# Graph instances
graph = create_travel_graph()
travel_graph = None


def _init_travel_graph():
    global travel_graph
    if travel_graph is None:
        travel_graph = get_graph()
    return travel_graph


__all__ = [
    "TravelState",
    "KNOWN_AGENTS",
    "AGENT_ORDER",
    "_empty_constraints",
    "_llm_text",
    "_json_from_llm",
    "get_database_url",
    "get_checkpointer",
    "supervisor_agent",
    "guardrail_blocked_agent",
    "flight_agent",
    "hotel_agent",
    "weather_agent",
    "budget_agent",
    "itinerary_agent",
    "human_approval_agent",
    "final_agent",
    "ROUTE_MAP",
    "route_from_supervisor",
    "route_after_agent",
    "_selected_agents",
    "graph",
    "travel_graph",
    "run_travel_agent",
    "resume_travel_agent",
    "_serialize_result",
    "_interrupt_payload",
]
