# Author: Vishal Bulbule
# Date: 2026-09-22

"""Four tools, one per state scope: app:, user:, no prefix, and temp:.

Each tool writes one key and returns a snapshot of the state it can see, so
you can compare what the tool saw during the turn with what the session
service stored afterwards. `temp:` keys are visible during the turn and are
never persisted. `app:` and `user:` keys are stored separately from the
session and show up in every session of the same app or the same user.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext


def _snapshot(tool_context: ToolContext) -> dict:
    return dict(tool_context.state.to_dict())


def set_app_flag(value: bool, tool_context: ToolContext) -> dict:
    """Set the app-scoped feature flag, shared by every user of this app.

    Args:
        value: The new flag value.
        tool_context: Injected by ADK; gives the tool access to session state.

    Returns:
        A dict with status, the scope written, and a state snapshot.
    """
    tool_context.state["app:flag"] = value
    return {"status": "ok", "scope": "app:", "state_snapshot": _snapshot(tool_context)}


def set_user_name(name: str, tool_context: ToolContext) -> dict:
    """Set the user-scoped name, shared across this user's sessions.

    Args:
        name: The user's name.
        tool_context: Injected by ADK; gives the tool access to session state.

    Returns:
        A dict with status, the scope written, and a state snapshot.
    """
    tool_context.state["user:name"] = name
    return {"status": "ok", "scope": "user:", "state_snapshot": _snapshot(tool_context)}


def set_session_cart_item(item: str, tool_context: ToolContext) -> dict:
    """Append an item to the session-scoped cart (this session only).

    Args:
        item: The item to add.
        tool_context: Injected by ADK; gives the tool access to session state.

    Returns:
        A dict with status, the scope written, and a state snapshot.
    """
    cart = list(tool_context.state.get("cart", []))
    cart.append(item)
    tool_context.state["cart"] = cart
    return {"status": "ok", "scope": "session", "state_snapshot": _snapshot(tool_context)}


def set_temp_token(token: str, tool_context: ToolContext) -> dict:
    """Set a temp-scoped token that is discarded when the turn ends.

    Args:
        token: Any short string.
        tool_context: Injected by ADK; gives the tool access to session state.

    Returns:
        A dict with status, the scope written, and a state snapshot.
    """
    tool_context.state["temp:token"] = token
    return {"status": "ok", "scope": "temp:", "state_snapshot": _snapshot(tool_context)}


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="prefix_demo_agent",
    description="Demonstrates the four ADK state scopes.",
    instruction=(
        "You are demonstrating ADK state scopes. When the user asks you to "
        "set an app flag, a user name, a cart item, or a temp token, call "
        "the matching tool exactly once. Then summarize the snapshot the "
        "tool returned in one sentence."
    ),
    tools=[set_app_flag, set_user_name, set_session_cart_item, set_temp_token],
)
