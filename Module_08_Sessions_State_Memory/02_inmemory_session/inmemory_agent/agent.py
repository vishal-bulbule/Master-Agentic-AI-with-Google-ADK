# Author: Vishal Bulbule
# Date: 2026-09-22

"""Coffee-order agent used to show that in-memory sessions do not survive a restart.

The tool writes the order into session state. With `InMemorySessionService`
that state lives in the server process only, so stopping the server deletes
every session.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext


def place_order(item: str, tool_context: ToolContext) -> dict:
    """Record the user's coffee order in session state.

    Args:
        item: A short description of the drink, for example "double espresso".
        tool_context: Injected by ADK; gives the tool access to session state.

    Returns:
        A dict with status and the recorded order.
    """
    tool_context.state["order"] = item
    return {"status": "ok", "order": item}


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="coffee_order_agent",
    description="Takes a coffee order and stores it in session state.",
    instruction=(
        "You are a barista. When the user describes what they want, call "
        "place_order(item) with the final drink description. If they change "
        "their order, call place_order again with the new description."
    ),
    tools=[place_order],
)
