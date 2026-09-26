# Author: Vishal Bulbule
# Date: 2026-09-22

"""Tool confirmation: pause before a risky tool runs and ask a human.

Two tools on one agent:
    read_user     safe read, runs immediately
    delete_user   wrapped in `FunctionTool(..., require_confirmation=True)`

When the model calls `delete_user`, ADK does not run it. It emits an
`adk_request_confirmation` function call and waits. The client answers with a
function response `{"confirmed": true}` or `{"confirmed": false}`; only on
true does the tool body execute. `require_confirmation` also accepts a
callable that decides per call from the arguments.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

_USERS: dict[str, dict] = {
    "u-1": {"name": "Asha", "email": "asha@example.com"},
    "u-2": {"name": "Karan", "email": "karan@example.com"},
}


def read_user(user_id: str) -> dict:
    """Returns a user record by id. Safe, read-only.

    Args:
        user_id: The user id, for example `u-1`.

    Returns:
        `status` "success" with the `user` record, or `status` "error" for
        an unknown id.
    """
    user = _USERS.get(user_id)
    if not user:
        return {"status": "error", "error_message": f"No user {user_id!r}."}
    return {"status": "success", "user": {"id": user_id, **user}}


def delete_user(user_id: str) -> dict:
    """Permanently deletes a user record.

    Args:
        user_id: The user id, for example `u-1`.

    Returns:
        `status` "success" with the `deleted` record, or `status` "error"
        for an unknown id.
    """
    if user_id not in _USERS:
        return {"status": "error", "error_message": f"No user {user_id!r}."}
    removed = _USERS.pop(user_id)
    return {"status": "success", "deleted": {"id": user_id, **removed}}


root_agent = LlmAgent(
    name="user_admin_agent",
    model="gemini-3.5-flash",
    description="Reads and, with approval, deletes user records.",
    instruction=(
        "You manage user records. "
        "Call read_user freely. "
        "Call delete_user only when the user explicitly asks to delete; the runtime pauses "
        "and asks a human to confirm before the deletion runs."
    ),
    tools=[read_user, FunctionTool(func=delete_user, require_confirmation=True)],
)
