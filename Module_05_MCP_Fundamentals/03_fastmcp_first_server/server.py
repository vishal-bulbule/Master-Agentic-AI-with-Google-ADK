# Author: Vishal Bulbule
# Date: 2026-09-22

"""The smallest useful MCP server: one tool over stdio.

`@mcp.tool()` reads the function signature, type hints, and docstring and
turns them into the tool's name, description, and JSON input schema. That is
what an MCP host receives from `tools/list`. `mcp.run()` with no arguments
uses the stdio transport: the host starts this script as a child process and
exchanges JSON-RPC messages over stdin and stdout.

Run:
    python server.py
Inspect:
    npx @modelcontextprotocol/inspector python server.py
"""

from fastmcp import FastMCP

mcp = FastMCP("weather-demo")

# Stub data so the sample runs offline. A real server would call a weather API.
_FAKE_WEATHER = {
    "pune": {"temp_c": 31, "condition": "sunny"},
    "mumbai": {"temp_c": 29, "condition": "humid"},
    "bengaluru": {"temp_c": 24, "condition": "cloudy"},
    "delhi": {"temp_c": 35, "condition": "hazy"},
}


@mcp.tool()
def get_weather(city: str) -> dict:
    """Return the current weather for a city.

    Args:
        city: City name, for example "Pune".

    Returns:
        A dict with status, city, temp_c, and condition, or status "error"
        and an error message if the city is unknown.
    """
    weather = _FAKE_WEATHER.get(city.strip().lower())
    if weather is None:
        return {"status": "error", "city": city, "error": "unknown city"}
    return {"status": "success", "city": city, **weather}


if __name__ == "__main__":
    mcp.run()
