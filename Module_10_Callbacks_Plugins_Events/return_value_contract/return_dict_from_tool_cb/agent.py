# Author: Vishal Bulbule
# Date: 2026-09-22

"""before_tool returns a dict, so the tool body is skipped.

The returned dict is sent to the model as the tool result. Use this to mock
expensive or side-effecting tools in tests, or to deny a call on permission
grounds.
"""

from typing import Any, Optional

from google.adk.agents import LlmAgent
from google.adk.tools import BaseTool, ToolContext


def get_weather(city: str) -> dict:
    """Returns the current weather for a city.

    A real implementation would call a weather API. In this sample the
    before_tool callback replaces the result, so this body never runs.

    Args:
        city: City name, for example "Pune".

    Returns:
        A dict with status, city, temp_c, and note.
    """
    return {"status": "success", "city": city, "temp_c": 99, "note": "real call"}


def mock_tool(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext
) -> Optional[dict]:
    print(f"[before_tool] returning dict, tool '{tool.name}' skipped")
    return {
        "status": "success",
        "city": args.get("city", "unknown"),
        "temp_c": 22,
        "note": "mock reading returned by before_tool callback",
    }


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="return_dict_agent",
    description="before_tool returns a dict, bypassing the real tool body.",
    instruction=(
        "You are a weather assistant. Always call get_weather to answer and "
        "report the temperature you receive."
    ),
    tools=[get_weather],
    before_tool_callback=mock_tool,
)
