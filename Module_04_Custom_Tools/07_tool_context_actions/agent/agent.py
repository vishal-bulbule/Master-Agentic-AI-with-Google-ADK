# Author: Vishal Bulbule
# Date: 2026-09-22

"""Tool context actions: change what the runtime does after a tool returns.

Three flags on `tool_context.actions`:
    transfer_to_agent="<name>"  hand the conversation to another agent
    skip_summarization=True     end the turn with the tool result; the model
                                does not get another call to rewrite it
    escalate=True               stop the enclosing LoopAgent (Module 9)

`escalate` only has an effect inside a `LoopAgent`; it is shown here so the
API is familiar before Module 9.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

billing_agent = LlmAgent(
    name="billing_agent",
    model="gemini-3.5-flash",
    description="Handles billing, invoices, and payment failures.",
    instruction="You are the billing specialist. Answer billing questions and stop.",
)


def route_to_billing(tool_context: ToolContext) -> dict:
    """Hands the conversation to billing_agent.

    Call this when the user asks about invoices, refunds, payment failures,
    or anything money-related.

    Returns:
        `status` "transferring" and the target agent name.
    """
    tool_context.actions.transfer_to_agent = "billing_agent"
    return {"status": "transferring", "to": "billing_agent"}


def get_system_status(tool_context: ToolContext) -> dict:
    """Returns the current system status, to be shown to the user as-is.

    Setting `skip_summarization` ends the turn with this function response,
    so the model is not called again to rephrase it. Use it for structured
    payloads a UI renders directly.

    Returns:
        `status` "success" with service name, uptime, and open incidents.
    """
    tool_context.actions.skip_summarization = True
    return {
        "status": "success",
        "service": "orders-api",
        "uptime_hours": 4321,
        "incidents_open": 0,
    }


def check_loop_condition(value: int, tool_context: ToolContext) -> dict:
    """Signals an enclosing LoopAgent to stop once `value` reaches 5.

    Args:
        value: The counter being watched. At 5 or more the tool escalates.

    Returns:
        `status` "done" with `escalated` True, or `status` "keep_going".
    """
    if value >= 5:
        tool_context.actions.escalate = True
        return {"status": "done", "escalated": True}
    return {"status": "keep_going", "value": value}


root_agent = LlmAgent(
    name="router_agent",
    model="gemini-3.5-flash",
    description="Front-door agent that shows transfer_to_agent, skip_summarization, and escalate.",
    instruction=(
        "You are the first stop for users. "
        "If they ask about invoices, refunds, or payments, call route_to_billing. "
        "If they ask for system status, call get_system_status (its output is final). "
        "If they ask you to 'check loop' with a number, call check_loop_condition."
    ),
    sub_agents=[billing_agent],
    tools=[route_to_billing, get_system_status, check_loop_condition],
)
