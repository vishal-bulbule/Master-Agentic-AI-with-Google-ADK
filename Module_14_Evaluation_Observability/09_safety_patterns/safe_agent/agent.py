# Author: Vishal Bulbule
# Date: 2026-09-22

"""Agent with three safety layers wired in as callbacks.

- before_model_callback: input sanitization (layer 1)
- before_tool_callback: permission boundary on destructive tools (layer 2)
- after_model_callback: output review (layer 3)

Each layer short-circuits by returning a value instead of None: an LlmResponse
skips or replaces the model call, a dict replaces the tool result. Try it with
and without `is_admin` in session state to see layer 2 decide.
"""

from google.adk.agents import LlmAgent

from .layer1_input_sanitization import input_sanitizer
from .layer2_tool_permission_boundary import tool_permission_boundary
from .layer3_output_review import output_review


def delete_account(user_id: str) -> dict:
    """Permanently deletes a user account. Guarded by layer 2.

    Args:
        user_id: Id of the account to delete.

    Returns:
        Dict with `status` and `deleted_user_id`.
    """
    return {"status": "success", "deleted_user_id": user_id}


def echo(message: str) -> dict:
    """Returns the message unchanged.

    Args:
        message: Text to echo back.

    Returns:
        Dict with `status` and `echo`.
    """
    return {"status": "success", "echo": message}


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="safe_agent",
    description="Demo agent with input sanitization, tool guardrails, and output review.",
    instruction=(
        "You are a helpful assistant. Use delete_account only when the user explicitly "
        "asks to delete an account. Use echo when the user asks you to repeat something. "
        "If a tool returns permission_denied, explain that and do not retry."
    ),
    tools=[delete_account, echo],
    before_model_callback=input_sanitizer,
    before_tool_callback=tool_permission_boundary,
    after_model_callback=output_review,
)
