"""
MCP Client facade for backward-compatibility.
Re-exports client instances and tools from src.mcp and src.core.llm.
"""
from src.core.llm import get_llm
from src.mcp.client import (
    mcp_client as client,
    get_server_tool as _get_server_tool,
    test_all_mcp_servers as get_all_tools,
)
from src.mcp.tools import (
    tavily_mcp_search,
    aviation_mcp_call,
    weather_mcp_search,
    forecast_mcp_search,
    extract_destination,
)

# Lazy/cached LLM instance
try:
    llm = get_llm()
except Exception:
    llm = None

__all__ = [
    "client",
    "llm",
    "_get_server_tool",
    "get_all_tools",
    "tavily_mcp_search",
    "aviation_mcp_call",
    "weather_mcp_search",
    "forecast_mcp_search",
    "extract_destination",
]