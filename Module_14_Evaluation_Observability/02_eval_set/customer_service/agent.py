# Author: Vishal Bulbule
# Date: 2026-09-22

"""Small customer-service agent used as the target of a multi-session eval set.

Three tools with hardcoded data: order lookup, refund, and escalation. The eval
set in `tests/customer_service.evalset.json` checks which tools the agent calls,
in which order, and with which arguments.

Notice that `escalate_to_human` takes a `category` from a fixed list instead of
a free-text reason. Tool trajectory metrics compare arguments exactly, so a
free-text argument would make that call impossible to assert on.
"""

from google.adk.agents import LlmAgent

_ORDERS = {
    "A100": {"status": "shipped", "carrier": "BlueDart", "eta_days": 2},
    "A101": {"status": "processing", "carrier": None, "eta_days": 5},
    "A102": {"status": "delivered", "carrier": "BlueDart", "eta_days": 0},
}

_ESCALATION_CATEGORIES = {"unknown_order", "complaint", "other"}


def lookup_order(order_id: str) -> dict:
    """Returns the shipping status of an order.

    Args:
        order_id: Order id such as "A100" (case-insensitive).

    Returns:
        Dict with `status` (`success` or `not_found`) and either `order`
        (status, carrier, eta_days) or `error_message`.
    """
    info = _ORDERS.get(order_id.upper())
    if info is None:
        return {"status": "not_found", "error_message": f"Order {order_id} not in system."}
    return {"status": "success", "order": info}


def issue_refund(order_id: str, amount: float) -> dict:
    """Issues a refund for an order.

    Args:
        order_id: Order id such as "A100".
        amount: Refund amount in USD.

    Returns:
        Dict with `status` and either `refund_id` or `error_message`.
    """
    if order_id.upper() not in _ORDERS:
        return {"status": "not_found", "error_message": f"Cannot refund unknown order {order_id}."}
    return {"status": "success", "refund_id": f"R-{order_id.upper()}-{int(amount)}"}


def escalate_to_human(order_id: str, category: str) -> dict:
    """Hands the conversation to a human agent.

    Args:
        order_id: The order the request is about, or "none" if there is no order.
        category: One of "unknown_order", "complaint", or "other".

    Returns:
        Dict with `status` and either `ticket_id` or `error_message`.
    """
    if category not in _ESCALATION_CATEGORIES:
        return {
            "status": "invalid_input",
            "error_message": f"category must be one of {sorted(_ESCALATION_CATEGORIES)}.",
        }
    return {"status": "success", "ticket_id": "T-9001", "order_id": order_id, "category": category}


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="customer_service",
    description="Handles order status, refunds, and escalations.",
    instruction=(
        "You are a polite customer-service agent.\n"
        "- Use lookup_order to check shipping status.\n"
        "- Before issuing a refund on an order you have not looked up in this "
        "conversation, call lookup_order to confirm it exists. Then call "
        "issue_refund. The user's request is enough confirmation; do not ask again.\n"
        "- If an order is not found, call escalate_to_human with category "
        "unknown_order and tell the user a human agent will follow up.\n"
        "- Use escalate_to_human with category complaint or other for anything "
        "else you cannot resolve."
    ),
    tools=[lookup_order, issue_refund, escalate_to_human],
)
