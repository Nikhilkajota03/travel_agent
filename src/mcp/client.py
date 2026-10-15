import os
import shutil
import sys
from pathlib import Path
from typing import Any
from langchain_mcp_adapters.client import MultiServerMCPClient

from src.config import settings

WEATHER_SERVER_FILE = Path(__file__).resolve().parent / "servers" / "weather_server.py"
if not WEATHER_SERVER_FILE.is_file():
    WEATHER_SERVER_FILE = settings.WEATHER_SERVER_PATH


def _subprocess_env(**updates: str | None) -> dict[str, str]:
    """Preserve current environment variables and inject MCP server keys."""
    env = os.environ.copy()
    for key, value in updates.items():
        if value:
            env[key] = value
    return env


# Initialize MultiServerMCPClient
mcp_client = MultiServerMCPClient(
    {
        "tavily": {
            "transport": "streamable_http",
            "url": (
                "https://mcp.tavily.com/mcp/"
                f"?tavilyApiKey={settings.TAVILY_API_KEY or ''}"
            ),
        },
        "aviationstack": {
            "transport": "stdio",
            "command": settings.UVX_COMMAND,
            "args": [
                "aviationstack-mcp",
            ],
            "env": _subprocess_env(
                AVIATION_STACK_API_KEY=settings.AVIATION_STACK_API_KEY,
            ),
        },
        "weather": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [
                str(WEATHER_SERVER_FILE),
            ],
            "env": _subprocess_env(
                OPENWEATHER_API_KEY=settings.OPENWEATHER_API_KEY,
            ),
        },
    }
)


async def get_server_tool(server_name: str, tool_name: str):
    """
    Load a single tool from a specific MCP server safely.
    Validates configuration prior to launching the subprocess.
    """
    if server_name == "tavily":
        settings.require("TAVILY_API_KEY", settings.TAVILY_API_KEY)

    elif server_name == "aviationstack":
        settings.require("AVIATION_STACK_API_KEY", settings.AVIATION_STACK_API_KEY)
        if shutil.which("uvx") is None:
            raise RuntimeError(
                "uvx was not found. Please install uv (`curl -LsSf https://astral.sh/uv/install.sh | sh`), "
                "restart your shell, and verify `uvx --version`."
            )

    elif server_name == "weather":
        settings.require("OPENWEATHER_API_KEY", settings.OPENWEATHER_API_KEY)
        if not WEATHER_SERVER_FILE.is_file():
            raise FileNotFoundError(f"Weather MCP server file not found: {WEATHER_SERVER_FILE}")

    tools = await mcp_client.get_tools(server_name=server_name)
    tool = next((item for item in tools if item.name == tool_name), None)

    if tool is None:
        available = ", ".join(sorted(item.name for item in tools)) or "none"
        raise RuntimeError(
            f"MCP tool '{tool_name}' was not found on server '{server_name}'. Available: {available}"
        )

    return tool


async def test_all_mcp_servers() -> dict[str, str]:
    """Test all MCP server connections independently and return diagnostics."""
    results = {}
    for server_name in ("tavily", "aviationstack", "weather"):
        try:
            tools = await mcp_client.get_tools(server_name=server_name)
            tool_names = ", ".join(t.name for t in tools) or "no tools"
            results[server_name] = f"OK -> {tool_names}"
        except Exception as exc:
            results[server_name] = f"FAILED -> {type(exc).__name__}: {exc}"
    return results
