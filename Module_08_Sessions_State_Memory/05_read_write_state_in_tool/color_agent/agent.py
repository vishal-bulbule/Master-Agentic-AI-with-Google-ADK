# Author: Vishal Bulbule
# Date: 2026-09-22

"""Read and write state from inside a tool with `tool_context.state`.

`remember_color` writes and `recall_color` reads the same key. The key uses
the `user:` prefix, so the value belongs to the user rather than to one
session: a brand-new session for the same `user_id` can recall it.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

STATE_KEY = "user:favorite_color"


def remember_color(color: str, tool_context: ToolContext) -> dict:
    """Save the user's favorite color in user-scoped state.

    Args:
        color: The color to remember.
        tool_context: Injected by ADK; gives the tool access to session state.

    Returns:
        A dict with status and the saved color.
    """
    tool_context.state[STATE_KEY] = color
    return {"status": "saved", "color": color}


def recall_color(tool_context: ToolContext) -> dict:
    """Return the saved favorite color, or "unknown" if none is stored.

    Args:
        tool_context: Injected by ADK; gives the tool access to session state.

    Returns:
        A dict with status and the color.
    """
    color = tool_context.state.get(STATE_KEY, "unknown")
    return {"status": "ok", "color": color}


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="color_memory_agent",
    description="Remembers and recalls the user's favorite color.",
    instruction=(
        "If the user tells you a favorite color, call remember_color(color). "
        "If they ask which color you remember, call recall_color() and answer "
        "with that color. If recall_color returns 'unknown', say you do not "
        "have one on record."
    ),
    tools=[remember_color, recall_color],
)
