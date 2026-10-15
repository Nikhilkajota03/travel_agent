import asyncio
from langchain_core.messages import AIMessage
from src.state import TravelState
from src.mcp.tools import extract_destination, weather_mcp_search, forecast_mcp_search


def weather_agent(state: TravelState) -> dict:
    """
    Weather Specialist Agent:
    Extracts the destination and fetches current conditions & forecasts via Weather FastMCP.
    """
    city = extract_destination(state["user_query"])

    try:
        weather_data = asyncio.run(weather_mcp_search(city))
        forecast_data = asyncio.run(forecast_mcp_search(city))

        weather_results = f"""
Current Weather:
{weather_data}

Forecast:
{forecast_data}
"""
    except Exception as exc:
        print(f"WEATHER AGENT MCP ERROR: {type(exc).__name__}: {exc}", flush=True)
        weather_results = (
            f"Live weather information for {city} is temporarily unavailable. "
            "Give general seasonal guidance and advise the traveler to verify the forecast before departure."
        )

    return {
        "weather_results": weather_results,
        "messages": [AIMessage(content="Weather information processed.")],
    }
