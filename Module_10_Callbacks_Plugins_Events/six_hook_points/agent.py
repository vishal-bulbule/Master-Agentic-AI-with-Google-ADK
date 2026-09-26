# Author: Vishal Bulbule
# Date: 2026-09-22

"""All six callback hook points wired on one agent.

Each callback prints which hook fired and returns None, so the run is not
changed. Ask for the time and the output shows the order ADK calls them in:

    before_agent, before_model, after_model, before_tool, after_tool,
    before_model, after_model, after_agent

The model is called twice: once to decide on the tool call, once to write the
answer from the tool result. A question that needs no tool skips the two tool
hooks and the second model call.
"""

from typing import Any, Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import BaseTool, ToolContext


def get_time(timezone: str) -> dict:
    """Returns a fixed clock reading. It exists only to fire the tool hooks.

    Args:
        timezone: Timezone name, for example "UTC" or "IST".

    Returns:
        A dict with status, timezone, and time.
    """
    return {"status": "success", "timezone": timezone, "time": "12:00"}


def before_agent_cb(callback_context: CallbackContext) -> None:
    print(f"hook: before_agent (agent={callback_context.agent_name})")
    return None


def after_agent_cb(callback_context: CallbackContext) -> None:
    print(f"hook: after_agent (agent={callback_context.agent_name})")
    return None


def before_model_cb(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    print("hook: before_model")
    return None


def after_model_cb(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    print("hook: after_model")
    return None


def before_tool_cb(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext
) -> Optional[dict]:
    print(f"hook: before_tool (tool={tool.name}, args={args})")
    return None


def after_tool_cb(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
    tool_response: dict,
) -> Optional[dict]:
    print(f"hook: after_tool (tool={tool.name})")
    return None


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="six_hooks_agent",
    description="Agent with all six callback hook points wired.",
    instruction=(
        "You are a clock assistant. When the user asks for the time, call the "
        "get_time tool and report what it returned."
    ),
    tools=[get_time],
    before_agent_callback=before_agent_cb,
    after_agent_callback=after_agent_cb,
    before_model_callback=before_model_cb,
    after_model_callback=after_model_cb,
    before_tool_callback=before_tool_cb,
    after_tool_callback=after_tool_cb,
)
