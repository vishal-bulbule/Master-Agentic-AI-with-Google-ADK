# Author: Vishal Bulbule
# Date: 2026-09-22

"""Agent variant: the model chooses among tools at runtime.

The agent has two tools, `get_order_status` and `lookup_shipping_policy`, and
decides per turn whether to call one, both or neither. For the order question
it calls `get_order_status("A-1042")` and answers with the real ETA, which
neither `support_chatbot` (no tools) nor `support_rag` (fixed retrieval over
policy documents) can do.
"""

from google.adk.agents import LlmAgent


def get_order_status(order_id: str) -> dict:
    """Looks up the live status of a customer order.

    Args:
        order_id: Order ID such as "A-1042".

    Returns:
        dict with `status` and either the order details or `error_message`.
    """
    fake_orders = {
        "A-1042": {
            "order_status": "in_transit",
            "carrier": "BlueDart",
            "eta": "tomorrow by 6 PM",
        },
        "A-1043": {"order_status": "delivered", "delivered_on": "yesterday"},
    }
    if order_id in fake_orders:
        return {"status": "success", "order_id": order_id, **fake_orders[order_id]}
    return {"status": "error", "error_message": f"Order {order_id} not found."}


def lookup_shipping_policy(topic: str) -> dict:
    """Looks up a shipping policy.

    Args:
        topic: One of "standard", "express", "returns", "delays".

    Returns:
        dict with `status` and either `policy` text or `error_message`.
    """
    policies = {
        "standard": "Standard shipping takes 3-5 business days.",
        "express": "Express shipping arrives within 1-2 business days.",
        "returns": "Free returns within 30 days.",
        "delays": "Beyond the ETA, contact support for a refund or replacement.",
    }
    policy = policies.get(topic.lower())
    if policy:
        return {"status": "success", "topic": topic, "policy": policy}
    return {"status": "error", "error_message": f"No policy for '{topic}'."}


root_agent = LlmAgent(
    name="support_agent",
    model="gemini-3.5-flash",
    description="Support agent that can look up orders and policies.",
    instruction=(
        "You are a customer support agent. When the user asks about an order, "
        "call `get_order_status` with the order ID. If they ask about a policy, "
        "call `lookup_shipping_policy`. You can call multiple tools in one turn. "
        "Answer clearly and concisely."
    ),
    tools=[get_order_status, lookup_shipping_policy],
)
