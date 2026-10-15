import asyncio
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from src.state import TravelState
from src.core.llm import get_llm
from src.mcp.tools import aviation_mcp_call
from src.agents.prompts import FLIGHT_AGENT_PROMPT_TEMPLATE


def flight_agent(state: TravelState) -> dict:
    """
    Flight Specialist Agent:
    Retrieves airport and airline data via AviationStack MCP and formulates route guidance.
    """
    query = state["user_query"]
    llm = get_llm()

    try:
        airports = asyncio.run(aviation_mcp_call("list_airports"))
        airlines = asyncio.run(aviation_mcp_call("list_airlines"))

        prompt = FLIGHT_AGENT_PROMPT_TEMPLATE.format(
            query=query,
            airport_data=str(airports)[:3000],
            airline_data=str(airlines)[:3000],
        )

        response = llm.invoke(
            [
                SystemMessage(content="You are an expert travel flight planner."),
                HumanMessage(content=prompt),
            ]
        )
        flight_data = response.content
    except Exception as exc:
        flight_data = f"Flight information unavailable: {exc}"

    return {
        "flight_results": flight_data,
        "messages": [AIMessage(content="Flight recommendations generated")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
