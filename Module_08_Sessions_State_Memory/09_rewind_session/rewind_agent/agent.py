# Author: Vishal Bulbule
# Date: 2026-09-22

"""Color-setter agent used to show session rewind.

Each turn sets `state["color"]`, so every invocation leaves a visible state
change. `Runner.rewind_async` can then roll the session back to before any
earlier invocation, which restores the state that existed at that point. The
dev UI has no rewind button; the README shows the Python call.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext


def set_color(color: str, tool_context: ToolContext) -> dict:
    """Set the session-scoped color.

    Args:
        color: The color to store.
        tool_context: Injected by ADK; gives the tool access to session state.

    Returns:
        A dict with status and the stored color.
    """
    tool_context.state["color"] = color
    return {"status": "ok", "color": color}


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="rewind_color_agent",
    description="Sets state['color'] when asked.",
    instruction=(
        "When the user asks to set the color, call set_color(color) with "
        "exactly the color they named. Reply with a short confirmation."
    ),
    tools=[set_color],
)
