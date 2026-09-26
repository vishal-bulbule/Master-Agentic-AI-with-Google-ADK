# Author: Vishal Bulbule
# Date: 2026-09-22

"""Support-ticket agent whose A2A card advertises the ADK extension.

The agent itself is an ordinary `LlmAgent` with one tool. What this sample
is about sits in `agent.json`: `capabilities.extensions` lists
`https://google.github.io/adk-docs/a2a/a2a-extension/` with
`required: false`. Clients that do not know the extension still get answers;
clients that activate it with the `A2A-Extensions` header get ADK's newer
executor, which returns the tool calls in the task's artifacts and records
the activation in the task metadata.
"""

from google.adk.agents import LlmAgent

TICKETS = {
    "T-100": {"ticket_status": "open", "priority": "high", "owner": "network team"},
    "T-101": {"ticket_status": "resolved", "priority": "low", "owner": "service desk"},
}


def get_ticket(ticket_id: str) -> dict:
    """Looks up a support ticket.

    Args:
        ticket_id: Ticket ID such as "T-100".

    Returns:
        dict with `status` and either the ticket details or `error_message`.
    """
    ticket = TICKETS.get(ticket_id.upper())
    if ticket is None:
        return {"status": "error", "error_message": f"No ticket {ticket_id}."}
    return {"status": "success", "ticket_id": ticket_id.upper(), **ticket}


root_agent = LlmAgent(
    name="ticket_desk",
    model="gemini-3.5-flash",
    description="Answers questions about support tickets.",
    instruction=(
        "You answer questions about support tickets. Call `get_ticket` with "
        "the ticket ID and report its status, priority and owner."
    ),
    tools=[get_ticket],
)
