# Author: Vishal Bulbule
# Date: 2026-09-22

"""Cost logger: an after_tool callback that meters every tool call.

After each tool runs, the callback looks up a per-tool price, adds it to a
running total in session state, and prints one line. It returns None, so the
tool result reaches the model unchanged.

Prices are made up. In a real system they come from your billing config or a
metering service.
"""

from typing import Any, Optional

from google.adk.agents import LlmAgent
from google.adk.tools import BaseTool, ToolContext

TOOL_COSTS_USD = {
    "search_web": 0.005,
    "lookup_price": 0.001,
    "get_weather": 0.0008,
}
DEFAULT_COST_USD = 0.0005
STATE_KEY = "total_cost_usd"


def search_web(query: str) -> dict:
    """Searches the web. Returns canned results in this sample.

    Args:
        query: Search terms.

    Returns:
        A dict with status, query, and a list of results.
    """
    return {"status": "success", "query": query, "results": [f"result for {query}"]}


def lookup_price(sku: str) -> dict:
    """Looks up the price of a product by SKU.

    Args:
        sku: Product SKU, for example "abc-1".

    Returns:
        A dict with status, sku, and price_inr, or an error message.
    """
    prices = {"abc-1": 99.0, "xyz-2": 1499.0}
    if sku.lower() not in prices:
        return {"status": "error", "error_message": f"Unknown SKU '{sku}'."}
    return {"status": "success", "sku": sku, "price_inr": prices[sku.lower()]}


def get_weather(city: str) -> dict:
    """Returns the current weather for a city. Canned data in this sample.

    Args:
        city: City name.

    Returns:
        A dict with status, city, and temp_c.
    """
    return {"status": "success", "city": city, "temp_c": 28}


def cost_logger(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
    tool_response: dict,
) -> Optional[dict]:
    """Adds the tool's cost to the session total and prints it."""
    cost = TOOL_COSTS_USD.get(tool.name, DEFAULT_COST_USD)
    total = tool_context.state.get(STATE_KEY, 0.0) + cost
    tool_context.state[STATE_KEY] = total
    print(f"[cost] tool={tool.name} cost=${cost:.4f} session_total=${total:.4f}")
    return None


root_agent = LlmAgent(
    model="gemini-3.5-flash",
    name="cost_logger_agent",
    description="Research assistant with search, price, and weather tools.",
    instruction=(
        "You are a research assistant with three tools: search_web, "
        "lookup_price, and get_weather. Pick the right one for each request."
    ),
    tools=[search_web, lookup_price, get_weather],
    after_tool_callback=cost_logger,
)
