# Author: Vishal Bulbule
# Date: 2026-09-22

"""Customer-service agent protected by a four-callback guardrail stack.

The callbacks live in callbacks.py:

1. PII redaction (before_model)
2. Token budget (before_model)
3. Profanity filter (after_model)
4. Cost logger (after_tool)

A callback argument also accepts a list. The before_model list runs in order
and stops at the first callback that returns a value, so redaction always runs
before the budget check sees the request. The tools are in-memory fakes.
"""

from google.adk.agents import LlmAgent

from .callbacks import (
    cost_logger,
    pii_redaction,
    profanity_filter,
    token_budget,
)

_FAKE_ORDERS = {
    "A-100": {"item": "Wireless headphones", "order_status": "delivered", "amount_inr": 4999},
    "A-101": {"item": "USB-C charger", "order_status": "in_transit", "amount_inr": 1299},
    "A-102": {"item": "Bluetooth speaker", "order_status": "delivered", "amount_inr": 3499},
}


def lookup_order(order_id: str) -> dict:
    """Looks up an order by ID.

    Args:
        order_id: The order ID, for example "A-100".

    Returns:
        A dict with status and the order fields, or an error message.
    """
    order = _FAKE_ORDERS.get(order_id.upper())
    if not order:
        return {"status": "error", "error_message": f"No order '{order_id}'."}
    return {"status": "success", "order_id": order_id.upper(), **order}


def issue_refund(order_id: str, reason: str) -> dict:
    """Issues a refund for an order.

    Args:
        order_id: The order ID, for example "A-100".
        reason: Short reason for the refund.

    Returns:
        A dict with status, refund amount, and ETA, or an error message.
    """
    order = _FAKE_ORDERS.get(order_id.upper())
    if not order:
        return {"status": "error", "error_message": f"No order '{order_id}'."}
    return {
        "status": "success",
        "order_id": order_id.upper(),
        "refund_inr": order["amount_inr"],
        "reason": reason,
        "eta_days": 5,
    }


def send_followup_email(customer_name: str, summary: str) -> dict:
    """Sends a follow-up email to the customer.

    Args:
        customer_name: The customer's name.
        summary: One-sentence summary of the resolution.

    Returns:
        A dict with status, recipient, subject, and a body preview.
    """
    return {
        "status": "success",
        "to": customer_name,
        "subject": "Follow-up from support",
        "body_preview": summary[:120],
    }


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="customer_service_agent",
    description=(
        "Customer-service agent for an online shop, protected by PII "
        "redaction, a token budget, a profanity filter, and a cost logger."
    ),
    instruction=(
        "You are a polite customer-service agent for an online electronics store. "
        "Look up orders with lookup_order. Issue refunds with issue_refund "
        "ONLY when the customer explicitly asks for one. Send a one-line "
        "follow-up using send_followup_email after resolving issues. "
        "Never repeat back personal contact info from the user."
    ),
    tools=[lookup_order, issue_refund, send_followup_email],
    before_model_callback=[pii_redaction, token_budget],
    after_model_callback=profanity_filter,
    after_tool_callback=cost_logger,
)
