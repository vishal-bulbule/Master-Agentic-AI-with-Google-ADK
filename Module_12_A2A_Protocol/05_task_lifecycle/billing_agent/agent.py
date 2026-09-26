# Author: Vishal Bulbule
# Date: 2026-09-22

"""Billing agent whose A2A task pauses in INPUT_REQUIRED and then resumes.

Served with `adk api_server --a2a`, every request becomes an A2A task. When
the customer has several open invoices, the agent calls `ask_client`, a
`LongRunningFunctionTool`. ADK's A2A executor turns a pending long-running
call into the task state `TASK_STATE_INPUT_REQUIRED`, with the call (and its
question) in `status.message`. The task is paused, not finished.

The client resumes the same task by sending a message with the same `taskId`
and `contextId` whose part is the `ask_client` function response. The agent
then calls `close_invoice` and the task ends in `TASK_STATE_COMPLETED`.
"""

from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.tools.long_running_tool import LongRunningFunctionTool

OPEN_INVOICES = {
    "acme": {"INV-19": 12_000, "INV-22": 84_500, "INV-30": 3_100},
    "globex": {"INV-41": 56_000},
}


def find_open_invoices(customer: str) -> dict:
    """Lists the open invoices of a customer.

    Args:
        customer: Customer name, such as "Acme".

    Returns:
        dict with `status` and either `invoices` (id to amount in INR) or
        `error_message`.
    """
    invoices = OPEN_INVOICES.get(customer.lower())
    if invoices is None:
        return {"status": "error", "error_message": f"No customer '{customer}'."}
    return {"status": "success", "customer": customer, "invoices": invoices}


def ask_client(question: str) -> Optional[dict]:
    """Asks the calling client a question and waits for its answer.

    Args:
        question: The question, including the options to choose from.

    Returns:
        None. The call stays pending, which pauses the A2A task in
        INPUT_REQUIRED; the client's answer arrives later as this tool's
        response.
    """
    return None


def close_invoice(customer: str, invoice_id: str) -> dict:
    """Closes one open invoice.

    Args:
        customer: Customer name, such as "Acme".
        invoice_id: Invoice ID, such as "INV-22".

    Returns:
        dict with `status` and either the closed invoice or `error_message`.
    """
    invoices = OPEN_INVOICES.get(customer.lower(), {})
    if invoice_id not in invoices:
        return {
            "status": "error",
            "error_message": f"{customer} has no open invoice {invoice_id}.",
        }
    return {
        "status": "success",
        "invoice": invoice_id,
        "invoice_status": "closed",
        "amount_inr": invoices[invoice_id],
    }


root_agent = LlmAgent(
    name="billing_agent",
    model="gemini-3.5-flash",
    description="Closes customer invoices; asks which one when it is ambiguous.",
    instruction=(
        "You close customer invoices. First call `find_open_invoices`. If the "
        "customer has exactly one open invoice, close it with `close_invoice`. "
        "If there are several and the request does not name one, call "
        "`ask_client` with a question that lists the options; never guess. "
        "When `ask_client` returns the answer, close that invoice and confirm "
        "the invoice ID and amount."
    ),
    tools=[
        find_open_invoices,
        LongRunningFunctionTool(ask_client),
        close_invoice,
    ],
)
