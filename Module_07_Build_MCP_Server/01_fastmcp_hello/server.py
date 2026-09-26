# Author: Vishal Bulbule
# Date: 2026-09-22

"""The smallest working FastMCP server.

One decorated function becomes one MCP tool. FastMCP builds the JSON input
schema from the type hints and the description from the docstring, the same
way ADK builds a FunctionTool declaration. `mcp.run()` serves it over stdio.

Run:
    python server.py
Inspect:
    npx @modelcontextprotocol/inspector python server.py
"""

from fastmcp import FastMCP

mcp = FastMCP("my-server")


@mcp.tool()
def get_weather(city: str) -> dict:
    """Return the current weather for a city.

    Args:
        city: City name, for example "Mumbai".

    Returns:
        A dict with status, city, temp_c, and condition (stub data).
    """
    return {"status": "success", "city": city, "temp_c": 22, "condition": "sunny"}


if __name__ == "__main__":
    mcp.run()
