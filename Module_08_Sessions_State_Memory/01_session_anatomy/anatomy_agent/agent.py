# Author: Vishal Bulbule
# Date: 2026-09-22

"""Small agent that saves a favorite color, used to inspect a session.

A session has four parts: `id`, `user_id`, `events`, and `state`. Chat with
this agent in `adk web`, then fetch the session over its REST API; the JSON
holds those four fields. The tool call, its result, and both model replies
all appear as separate entries in `events`, and the saved color appears in
`state`.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext


def save_color(color: str, tool_context: ToolContext) -> dict:
    """Save the user's favorite color into session state.

    Args:
        color: The color the user mentioned.
        tool_context: Injected by ADK; gives the tool access to session state.

    Returns:
        A dict with status and the saved color.
    """
    tool_context.state["favorite_color"] = color
    return {"status": "saved", "color": color}


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="anatomy_agent",
    description="Small agent that saves and recalls a color.",
    instruction=(
        "If the user tells you a favorite color, call save_color(color). "
        "If the user asks which color they mentioned, answer from the "
        "conversation history."
    ),
    tools=[save_color],
)
