# Author: Vishal Bulbule
# Date: 2026-09-22

"""Product catalog agent, served to other agents over A2A.

A plain ADK LlmAgent with two function tools. Nothing in this file knows about
A2A: `adk web` and `adk run` run it as a local agent, and
`adk api_server --a2a` serves it over A2A because the folder also contains an
`agent.json` agent card. Keeping the agent free of transport code is what lets
you move it between in-process and remote use.
"""

from google.adk.agents import LlmAgent

from .tools import list_categories, lookup_product

root_agent = LlmAgent(
    name="product_catalog",
    model="gemini-3.5-flash",
    description=(
        "Answers questions about the product catalog: SKUs, prices, stock, "
        "and categories."
    ),
    instruction=(
        "You are the product catalog agent for an electronics store.\n"
        "Tools:\n"
        "  - lookup_product(sku): details for a single SKU.\n"
        "  - list_categories(): the product categories in the catalog.\n"
        "\n"
        "Rules:\n"
        "1. If the user gives a SKU, call lookup_product. Never guess prices.\n"
        "2. If the user asks what kinds of products exist, call list_categories.\n"
        "3. If asked about anything outside the catalog (orders, returns, "
        "shipping), say that you only handle catalog lookups.\n"
        "4. Quote prices in INR, for example 'INR 5,499'."
    ),
    tools=[lookup_product, list_categories],
)
