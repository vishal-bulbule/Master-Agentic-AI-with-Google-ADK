# Author: Vishal Bulbule
# Date: 2026-09-22

"""Layer 2: a tool permission boundary in a before_tool_callback.

Destructive tools run only when the session state has `is_admin` set to true.
Otherwise the callback returns a dict, which ADK uses as the tool result
without running the tool. The model sees the permission error and explains it.

The first control is still scoping: give an agent only the tools it needs.
This callback is the second line of defense for when scoping was not enough.
"""

from typing import Any, Optional

from google.adk.tools import BaseTool, ToolContext

DESTRUCTIVE_TOOLS = {"delete_account", "wipe_database", "issue_refund"}


def tool_permission_boundary(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext
) -> Optional[dict]:
    """Blocks destructive tools unless the session is marked admin."""
    if tool.name not in DESTRUCTIVE_TOOLS:
        return None

    if not tool_context.state.get("is_admin", False):
        print(f"[layer2] non-admin call to {tool.name} blocked")
        return {
            "status": "permission_denied",
            "error_message": (
                f"The tool '{tool.name}' requires admin permission. "
                "Ask a human agent to take over."
            ),
        }
    return None
