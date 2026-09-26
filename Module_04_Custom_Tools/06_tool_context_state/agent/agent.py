# Author: Vishal Bulbule
# Date: 2026-09-22

"""Tool context: read and write session state from inside a tool.

Add a parameter annotated `ToolContext` and ADK injects the context when it
calls the tool; the parameter is left out of the schema the model sees.
`tool_context.state` is dict-like, and the key prefix controls lifetime:
    user:*     persists across sessions for this user
    app:*      shared across all users of this app
    (none)     current session only
    temp:*     current invocation only, discarded afterwards

To see which keys survive, save a theme in one `adk web` session, then start
a new session: the State tab still shows `user:theme` but not `last_topic`.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext


def set_theme(theme: str, tool_context: ToolContext) -> dict:
    """Saves the user's preferred UI theme to cross-session state.

    Args:
        theme: One of "light", "dark", "solarized".

    Returns:
        `status` "success" with the saved key, or `status` "error" for an
        unknown theme.
    """
    if theme not in {"light", "dark", "solarized"}:
        return {"status": "error", "error_message": f"Unknown theme {theme!r}."}
    tool_context.state["user:theme"] = theme
    return {"status": "success", "saved": {"user:theme": theme}}


def get_theme(tool_context: ToolContext) -> dict:
    """Reads back the user's saved UI theme.

    Returns:
        `status` "success" with `theme`, or `status` "error" when no theme
        has been saved for this user.
    """
    theme = tool_context.state.get("user:theme")
    if theme is None:
        return {"status": "error", "error_message": "No theme saved yet."}
    return {"status": "success", "theme": theme}


def remember_last_topic(topic: str, tool_context: ToolContext) -> dict:
    """Stores the current conversation topic in session-only state.

    Args:
        topic: A short description of what the conversation is about.

    Returns:
        `status` "success" with the saved key.
    """
    tool_context.state["last_topic"] = topic
    return {"status": "success", "saved": {"last_topic": topic}}


root_agent = LlmAgent(
    name="preferences_agent",
    model="gemini-3.5-flash",
    description="Demonstrates tool_context.state with prefixes.",
    instruction=(
        "Help the user manage their UI preferences. "
        "Call set_theme when they tell you a preference, get_theme when they ask what is saved, "
        "and remember_last_topic only when the user asks you to remember what you are talking about."
    ),
    tools=[set_theme, get_theme, remember_last_topic],
)
