"""
Weather MCP Server entrypoint.
Wraps the modularized FastMCP server located at src/mcp/servers/weather_server.py.
"""
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.mcp.servers.weather_server import mcp, get_current_weather, get_forecast

if __name__ == "__main__":
    mcp.run(transport="stdio")