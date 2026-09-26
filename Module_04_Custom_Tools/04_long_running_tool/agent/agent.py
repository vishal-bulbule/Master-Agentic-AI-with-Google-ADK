# Author: Vishal Bulbule
# Date: 2026-09-22

"""Long-running tools: start work now, deliver the result later.

`ask_for_approval` stands in for opening an approval ticket. It returns at
once with `status="pending"`. Because it is wrapped in
`LongRunningFunctionTool`, ADK records the call id in the event's
`long_running_tool_ids` and the run ends there, without waiting.

Later, when the decision arrives from outside the agent (a manager clicks
Approve in another system), the client sends a new message containing a
`FunctionResponse` with the same call id and the final result. The agent then
continues and reports the outcome.
"""

import uuid

from google.adk.agents import LlmAgent
from google.adk.tools import LongRunningFunctionTool


def ask_for_approval(purpose: str, amount: float) -> dict:
    """Opens an expense-approval ticket and returns its id.

    Do not wait for approval inside this function. Create the ticket and
    return `status="pending"`; the decision arrives later as a function
    response for the same call.

    Args:
        purpose: Short reason for the expense, for example "team offsite dinner".
        amount: The amount to be approved, in INR.

    Returns:
        `{"status": "pending", "ticket_id": ..., "approver": ..., "purpose": ..., "amount": ...}`
    """
    ticket_id = f"APPROVAL-{uuid.uuid4().hex[:8].upper()}"
    return {
        "status": "pending",
        "ticket_id": ticket_id,
        "approver": "finance-manager@example.com",
        "purpose": purpose,
        "amount": amount,
    }


root_agent = LlmAgent(
    name="expense_agent",
    model="gemini-3.5-flash",
    description="Submits expense-approval requests as long-running tool calls.",
    instruction=(
        "You help users get expenses approved. When the user requests an expense, "
        "call ask_for_approval(purpose, amount). The tool returns status='pending' "
        "with a ticket id: tell the user the ticket id and that a manager has been notified. "
        "When you later receive the final result for that ticket, share the outcome."
    ),
    tools=[LongRunningFunctionTool(func=ask_for_approval)],
)
