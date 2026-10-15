from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from src.state import TravelState
from src.core.llm import get_llm
from src.agents.prompts import BUDGET_AGENT_PROMPT_TEMPLATE


def budget_agent(state: TravelState) -> dict:
    """
    Budget Specialist Agent:
    Evaluates costs, financial constraints, and provides realistic budget estimates.
    """
    llm = get_llm()
    prompt = BUDGET_AGENT_PROMPT_TEMPLATE.format(
        query=state["user_query"],
        constraints=state.get("trip_constraints", {}),
        flight_results=state.get("flight_results", ""),
        hotel_results=state.get("hotel_results", ""),
        weather_results=state.get("weather_results", ""),
    )

    response = llm.invoke(
        [
            SystemMessage(content="You are a practical travel budget analyst."),
            HumanMessage(content=prompt),
        ]
    )

    return {
        "budget_results": response.content,
        "messages": [AIMessage(content="Budget assessment generated.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
