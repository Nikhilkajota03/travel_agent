from langchain_core.messages import SystemMessage, HumanMessage
from src.state import TravelState
from src.core.llm import get_llm
from src.agents.prompts import FINAL_AGENT_PROMPT_TEMPLATE


def final_agent(state: TravelState) -> dict:
    """
    Final Response Agent:
    Produces a polished, comprehensive 7-section travel plan, incorporating human review feedback.
    """
    llm = get_llm()

    if state.get("approved", False):
        review_instruction = (
            "The user approved the draft. Preserve its decisions while polishing it."
        )
    else:
        feedback = state.get("human_feedback", "").strip() or "Improve the draft before finalizing it."
        review_instruction = f"The user requested a revision. Apply this feedback carefully:\n{feedback}"

    final_prompt = FINAL_AGENT_PROMPT_TEMPLATE.format(
        review_instruction=review_instruction,
        query=state["user_query"],
        constraints=state.get("trip_constraints", {}),
        flight_results=state.get("flight_results", ""),
        hotel_results=state.get("hotel_results", ""),
        weather_results=state.get("weather_results", ""),
        budget_results=state.get("budget_results", ""),
        itinerary=state.get("itinerary", ""),
    )

    response = llm.invoke(
        [
            SystemMessage(content="You are a professional AI travel booking assistant."),
            HumanMessage(content=final_prompt),
        ]
    )

    return {
        "final_response": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
