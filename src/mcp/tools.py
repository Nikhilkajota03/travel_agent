from typing import Any
from src.mcp.client import get_server_tool
from src.core.llm import get_llm


async def tavily_mcp_search(query: str):
    """Search the web for hotels, attractions, or travel advice using Tavily MCP."""
    search_tool = await get_server_tool("tavily", "tavily_search")
    return await search_tool.ainvoke({"query": query})


async def aviation_mcp_call(tool_name: str, tool_args: dict[str, Any] | None = None):
    """Call an AviationStack flight database tool via AviationStack MCP."""
    aviation_tool = await get_server_tool("aviationstack", tool_name)
    return await aviation_tool.ainvoke(tool_args or {})


async def weather_mcp_search(city: str):
    """Fetch current weather data for a city using custom Weather MCP server."""
    weather_tool = await get_server_tool("weather", "get_current_weather")
    return await weather_tool.ainvoke({"city": city})


async def forecast_mcp_search(city: str):
    """Fetch forecast data for a city using custom Weather MCP server."""
    forecast_tool = await get_server_tool("weather", "get_forecast")
    return await forecast_tool.ainvoke({"city": city})


def extract_destination(query: str) -> str:
    """Extract destination city or country name from the user request using the LLM."""
    prompt = f"""
Extract only the destination city or country from the travel request.

Travel request:
{query}

Return only the destination name.
Do not add any explanation.
"""
    llm = get_llm()
    response = llm.invoke(prompt)
    destination = str(response.content).strip()

    if not destination:
        raise ValueError("The destination could not be extracted from the request.")

    return destination
