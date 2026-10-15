from langgraph.graph import StateGraph, START, END
from src.state import TravelState
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
)
from src.core.database import get_checkpointer


def create_travel_graph() -> StateGraph:
    """Instantiate and wire the StateGraph nodes and conditional edges."""
    workflow = StateGraph(TravelState)

    # 1. Register Nodes
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("guardrail_blocked", guardrail_blocked_agent)
    workflow.add_node("flight_agent", flight_agent)
    workflow.add_node("hotel_agent", hotel_agent)
    workflow.add_node("weather_agent", weather_agent)
    workflow.add_node("budget_agent", budget_agent)
    workflow.add_node("itinerary_agent", itinerary_agent)
    workflow.add_node("human_approval", human_approval_agent)
    workflow.add_node("final_agent", final_agent)

    # 2. Add Edges & Conditional Routing
    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges("supervisor", route_from_supervisor, ROUTE_MAP)

    workflow.add_conditional_edges(
        "flight_agent", route_after_agent("flight_agent"), ROUTE_MAP
    )
    workflow.add_conditional_edges(
        "hotel_agent", route_after_agent("hotel_agent"), ROUTE_MAP
    )
    workflow.add_conditional_edges(
        "weather_agent", route_after_agent("weather_agent"), ROUTE_MAP
    )
    workflow.add_conditional_edges(
        "budget_agent", route_after_agent("budget_agent"), ROUTE_MAP
    )

    workflow.add_edge("itinerary_agent", "human_approval")
    workflow.add_edge("human_approval", "final_agent")
    workflow.add_edge("final_agent", END)
    workflow.add_edge("guardrail_blocked", END)

    return workflow


def get_compiled_graph(checkpointer=None):
    """
    Compile the StateGraph with the PostgreSQL checkpointer.
    If checkpointer is omitted, uses the lazy database checkpointer.
    """
    workflow = create_travel_graph()
    active_checkpointer = checkpointer if checkpointer is not None else get_checkpointer()
    return workflow.compile(checkpointer=active_checkpointer)
