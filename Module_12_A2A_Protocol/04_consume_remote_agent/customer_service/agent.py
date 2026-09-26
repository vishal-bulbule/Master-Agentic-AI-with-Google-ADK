# Author: Vishal Bulbule
# Date: 2026-09-22

"""Customer service agent that delegates catalog questions over A2A.

`RemoteA2aAgent` is a sub-agent whose body runs in another process. ADK
fetches the remote agent card on first use, then forwards each delegated turn
as an A2A message and turns the reply back into ADK events. To the parent
LlmAgent it looks like any other sub-agent, so routing still happens through
`transfer_to_agent`.

`use_legacy=False` adds the ADK A2A extension URI to the request headers,
which tells an ADK server to use its newer executor. See 06_a2a_extensions.

Start the catalog first: `adk api_server --a2a --port 8081` in
02_expose_agent. ADK serves each A2A agent under /a2a/<app_name>, so the card
is at http://localhost:8081/a2a/product_catalog/.well-known/agent-card.json.
"""

from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import (
    AGENT_CARD_WELL_KNOWN_PATH,
    RemoteA2aAgent,
)

# AGENT_CARD_WELL_KNOWN_PATH is "/.well-known/agent-card.json" with a2a-sdk 1.x.
remote_catalog = RemoteA2aAgent(
    name="catalog",
    description="Remote product catalog agent: SKU lookups and category listings.",
    agent_card=f"http://localhost:8081/a2a/product_catalog{AGENT_CARD_WELL_KNOWN_PATH}",
    use_legacy=False,
)

root_agent = LlmAgent(
    name="customer_service",
    model="gemini-3.5-flash",
    description=(
        "Front-line customer service agent. Delegates product questions to "
        "the catalog agent."
    ),
    instruction=(
        "You are the customer service agent for an electronics store.\n"
        "You have one sub-agent, `catalog`, which knows products, SKUs, and "
        "prices.\n"
        "\n"
        "Routing rules:\n"
        "1. Questions about products, SKUs, prices, stock, or categories: "
        "transfer to `catalog`.\n"
        "2. Order status, returns, shipping, or account issues: answer briefly "
        "yourself and say a human agent will follow up. Do not transfer; the "
        "catalog cannot help.\n"
        "3. Greetings and small talk: answer yourself, briefly.\n"
        "\n"
        "Be polite and concise."
    ),
    sub_agents=[remote_catalog],
)
