# Author: Vishal Bulbule
# Date: 2026-09-22

"""Anatomy of a good tool: name, type hints, docstring, status, error text.

ADK builds the tool schema the model sees from three things only: the
function name, the type-hinted parameters, and the docstring. The five rules
applied in `lookup_order_status`:
    1. Descriptive verb_noun name, not `do_thing`.
    2. Type hints on every parameter and the return value.
    3. The docstring says when to call the tool, not only what it does.
    4. It returns a dict with a `status` field.
    5. Error messages are sentences the model can act on.

Compare with `../bad_tool_agent/agent.py`, which breaks every rule.
"""

from google.adk.agents import LlmAgent

# In-memory order book standing in for a database.
_ORDERS: dict[str, dict] = {
    "A-1001": {"item": "Mechanical keyboard", "status": "shipped", "eta": "2026-05-25"},
    "A-1002": {"item": "USB-C hub", "status": "processing", "eta": "2026-05-28"},
    "A-1003": {"item": "Standing desk", "status": "delivered", "eta": "2026-05-19"},
}


def lookup_order_status(order_id: str) -> dict:
    """Fetches the current status of a customer order.

    Use this tool ONLY when the user provides an order ID (formatted like
    `A-1001`). Do not use it for general questions or to guess at orders the
    user has not named.

    Args:
        order_id: The unique identifier of the order, for example `A-1001`.

    Returns:
        On success: `{"status": "success", "order": {...}}`.
        On a miss: `{"status": "error", "error_message": "..."}`.
    """
    order = _ORDERS.get(order_id.upper())
    if not order:
        return {
            "status": "error",
            "error_message": f"Order {order_id!r} not found. Ask the user to re-check the ID.",
        }
    return {"status": "success", "order": {"id": order_id.upper(), **order}}


root_agent = LlmAgent(
    name="order_status_agent",
    model="gemini-3.5-flash",
    description="Answers questions about a customer's order status.",
    instruction=(
        "You help customers check the status of their orders. "
        "If the user mentions an order ID like 'A-1001', call lookup_order_status. "
        "If they ask vaguely ('where is my order?') ask for the ID first."
    ),
    tools=[lookup_order_status],
)
