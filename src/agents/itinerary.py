from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from src.state import TravelState
from src.core.llm import get_llm
from src.agents.prompts import ITINERARY_AGENT_PROMPT_TEMPLATE


def itinerary_agent(state: TravelState) -> dict:
    """
    Itinerary Planner Agent:
    Consolidates flight, hotel, weather, and budget findings into a draft day-by-day plan.
    """
    llm = get_llm()
    prompt = ITINERARY_AGENT_PROMPT_TEMPLATE.format(
        query=state["user_query"],
        constraints=state.get("trip_constraints", {}),
        flight_results=state.get("flight_results", ""),
        hotel_results=state.get("hotel_results", ""),
        weather_results=state.get("weather_results", ""),
        budget_results=state.get("budget_results", ""),
    )

    response = llm.invoke(
        [
            SystemMessage(content="You are an expert travel planner."),
            HumanMessage(content=prompt),
        ]
    )

    approval_request = (
        "Please review the generated draft itinerary. Approve it to create the "
        "final polished plan, or provide feedback for revision."
    )

    return {
        "itinerary": response.content,
        "approval_request": approval_request,
        "messages": [AIMessage(content="Draft itinerary created for human review.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
